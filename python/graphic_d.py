import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression


def read_snapshots(directory, time_limit):
    files = sorted(f for f in os.listdir(directory) if f.startswith("snapshot-") and f.endswith(".txt"))
    times = []
    snapshots = []
    for fname in files:
        time = float(fname.replace("snapshot-", "").replace(".txt", ""))
        if time_limit != 0 and time > time_limit:
            break
        times.append(time)
        with open(os.path.join(directory, fname)) as f:
            data = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(data))
    return np.array(times), snapshots


def calcular_DCM_por_bins(times, snapshots, idx_grande, bin_dt=0.02):
    x0, y0 = snapshots[0][idx_grande, :2]
    t_max = times[-1]
    bins = np.arange(0, t_max + bin_dt, bin_dt)
    bin_vals = [[] for _ in range(len(bins) - 1)]

    for t, snap in zip(times, snapshots):
        pos = snap[idx_grande, :2]
        d2 = np.sum((pos - [x0, y0]) ** 2)
        idx = np.searchsorted(bins, t, side="right") - 1
        if 0 <= idx < len(bin_vals):
            bin_vals[idx].append(d2)

    tiempos = []
    valores = []

    for i, vals in enumerate(bin_vals):
        if vals:
            tiempos.append((bins[i] + bins[i + 1]) / 2)
            valores.append(np.mean(vals))
        else:
            tiempos.append((bins[i] + bins[i + 1]) / 2)
            valores.append(np.nan)  # para alinear

    return np.array(tiempos), np.array(valores)


def ajustar_dcm(tiempos, dcm):
    mask = ~np.isnan(dcm)
    X = tiempos[mask].reshape(-1, 1)
    y = dcm[mask]
    model = LinearRegression()
    model.fit(X, y)
    pendiente = model.coef_[0]
    intercepto = model.intercept_
    D = pendiente / 4
    return pendiente, intercepto, D


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+", help="Carpetas de simulaciones con la partícula grande")
    parser.add_argument("--idx-grande", type=int, default=0, help="Índice de la partícula grande")
    parser.add_argument("--bin-dt", type=float, default=0.02, help="Tamaño de bin temporal")
    parser.add_argument("--time-limit", type=float, default=0, help="Límite de tiempo para el cálculo de DCM")
    args = parser.parse_args()

    all_dcms = []
    for dirpath in args.dirs:
        times, snaps = read_snapshots(os.path.join(dirpath, "snapshots"), args.time_limit)
        t_bins, dcm = calcular_DCM_por_bins(times, snaps, args.idx_grande, args.bin_dt)
        all_dcms.append(dcm)

    all_dcms = np.array(all_dcms)  # shape: (n_reps, n_tiempos)
    dcm_promedio = np.nanmean(all_dcms, axis=0)
    dcm_std = np.nanstd(all_dcms, axis=0)

    pendiente, intercepto, D = ajustar_dcm(t_bins, dcm_promedio)

    print(f"Ajuste lineal: DCM ≈ {pendiente:.4e}·t + {intercepto:.2e}")
    print(f"→ Coeficiente de difusión D ≈ {D:.4e} m²/s")

    # Plot
    plt.figure()
    plt.errorbar(t_bins, dcm_promedio, yerr=dcm_std, fmt="o", capsize=2, label="DCM promedio ± σ")
    plt.plot(t_bins, pendiente * t_bins + intercepto, "r-", label=f"Recta de ajuste (y={pendiente:.2e}·t)")
    plt.xlabel("Tiempo (s)")
    plt.ylabel("DCM (m²)")
    plt.title("DCM promedio de la partícula grande")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("DCM_promedio_vs_t.png")
    plt.show()


if __name__ == "__main__":
    main()
