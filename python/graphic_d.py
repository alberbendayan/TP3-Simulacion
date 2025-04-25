import argparse
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
            valores.append(np.nan)

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


def barrido_d_para_minimo_error(ax, tiempos, dcm_promedio, D_min=0, D_max=6e-4, pasos=300):
    D_vals = np.linspace(D_min, D_max, pasos)
    errores = []
    mask = ~np.isnan(dcm_promedio)
    t_valid = tiempos[mask]
    dcm_valid = dcm_promedio[mask]

    for D in D_vals:
        dcm_modelo = 4 * D * t_valid
        error = np.mean((dcm_valid - dcm_modelo) ** 2)
        errores.append(error)

    errores = np.array(errores)
    D_opt = D_vals[np.argmin(errores)]
    E_min = np.min(errores)

    ax.plot(D_vals, errores, label="Error cuadrático medio")
    ax.axvline(D_opt, color="r", linestyle="--", label=f"Coeficiente Difusión = {D_opt:.2e}")
    ax.set_xlabel("D (m²/s)", fontsize=14)
    ax.set_ylabel("Error (m²)", fontsize=14)
    ax.grid(True)
    ax.legend()
    ax.tick_params(axis="both", labelsize=12)

    return D_opt, E_min


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+", help="Carpetas de simulaciones con la partícula grande")
    parser.add_argument("--idx-grande", type=int, default=0, help="Índice de la partícula grande")
    parser.add_argument("--bin-dt", type=float, default=0.02, help="Tamaño de bin temporal")
    parser.add_argument("--time-limit", type=float, default=0, help="Límite de tiempo")
    args = parser.parse_args()

    all_dcms = []
    for dirpath in args.dirs:
        times, snaps = read_snapshots(os.path.join(dirpath, "snapshots"), args.time_limit)
        t_bins, dcm = calcular_DCM_por_bins(times, snaps, args.idx_grande, args.bin_dt)
        all_dcms.append(dcm)

    all_dcms = np.array(all_dcms)
    dcm_promedio = np.nanmean(all_dcms, axis=0)
    dcm_std = np.nanstd(all_dcms, axis=0)

    # Figura 1: DCM vs t
    fig1, ax1 = plt.subplots()
    pendiente, intercepto, D = ajustar_dcm(t_bins, dcm_promedio)
    ax1.errorbar(t_bins, dcm_promedio, yerr=dcm_std, fmt="o", capsize=2, label="DCM promedio ± σ")
    ax1.plot(t_bins, pendiente * t_bins + intercepto, "r-", label=f"Recta de ajuste (y={pendiente:.2e}·t)")
    ax1.set_xlabel("Tiempo (s)", fontsize=14)
    ax1.set_ylabel("DCM (m²)", fontsize=14)
    ax1.tick_params(axis="both", labelsize=12)
    ax1.grid(True)
    ax1.legend()
    fig1.tight_layout()
    for dirpath in args.dirs:
        fig1.savefig(os.path.join(dirpath, "DCM_promedio_vs_t.png"))

    # Figura 2: error vs D
    fig2, ax2 = plt.subplots()
    D_alt, E_min = barrido_d_para_minimo_error(ax2, t_bins, dcm_promedio)
    fig2.tight_layout()
    for dirpath in args.dirs:
        fig2.savefig(os.path.join(dirpath, "error_vs_D.png"))

    plt.show()


if __name__ == "__main__":
    main()
