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


def calcular_DCM_por_bins(times, snapshots, idx_grande, bin_dt=0.02, R_pared=None, R_grande=None, delta=1e-4):
    x0, y0 = snapshots[0][idx_grande, :2]
    t_max = times[-1]
    bins = np.arange(0, t_max + bin_dt, bin_dt)
    bin_vals = [[] for _ in range(len(bins) - 1)]

    for t, snap in zip(times, snapshots):
        pos = snap[idx_grande, :2]
        r = np.linalg.norm(pos)

        if R_pared and R_grande:
            if r >= R_pared - R_grande - delta:
                continue  # muy cerca de la pared

        d2 = np.sum((pos - [x0, y0]) ** 2)
        idx = np.searchsorted(bins, t, side="right") - 1
        if 0 <= idx < len(bin_vals):
            bin_vals[idx].append(d2)

    tiempos = []
    valores = []
    conteos = []

    for i, vals in enumerate(bin_vals):
        tiempos.append((bins[i] + bins[i + 1]) / 2)
        if vals:
            valores.append(np.mean(vals))
            conteos.append(len(vals))
        else:
            valores.append(np.nan)
            conteos.append(0)

    return np.array(tiempos), np.array(valores), np.array(conteos)


def ajustar_dcm(tiempos, dcm, conteos, t_max_ajuste=1.0, min_bin_count=3):
    mask = (~np.isnan(dcm)) & (tiempos <= t_max_ajuste) & (conteos >= min_bin_count)
    X = tiempos[mask].reshape(-1, 1)
    y = dcm[mask]

    if len(X) < 2:
        raise RuntimeError("No hay suficientes puntos válidos para ajustar el DCM")

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
    parser.add_argument("dirs", nargs="+", help="Carpetas con simulaciones de la partícula grande")
    parser.add_argument("--idx-grande", type=int, default=0)
    parser.add_argument("--bin-dt", type=float, default=0.02)
    parser.add_argument("--time-limit", type=float, default=0)
    parser.add_argument("--t-max-ajuste", type=float, default=1.0)
    parser.add_argument("--min-bin-count", type=int, default=3)
    args = parser.parse_args()

    with open(os.path.join(args.dirs[0], "config.json")) as f:
        config = json.load(f)
    R_pared = config["big_radius"]
    R_grande = config["small_radius"]

    all_dcms = []
    all_conteos = []

    for dirpath in args.dirs:
        times, snaps = read_snapshots(os.path.join(dirpath, "snapshots"), args.time_limit)
        t_bins, dcm, conteos = calcular_DCM_por_bins(
            times, snaps, idx_grande=args.idx_grande, bin_dt=args.bin_dt, R_pared=R_pared, R_grande=R_grande
        )
        all_dcms.append(dcm)
        all_conteos.append(conteos)

    all_dcms = np.array(all_dcms)
    all_conteos = np.array(all_conteos)
    dcm_promedio = np.nanmean(all_dcms, axis=0)
    dcm_std = np.nanstd(all_dcms, axis=0)
    conteos_prom = np.mean(all_conteos, axis=0)

    pendiente, intercepto, D = ajustar_dcm(
        t_bins, dcm_promedio, conteos_prom, t_max_ajuste=args.t_max_ajuste, min_bin_count=args.min_bin_count
    )

    # Figura 1
    fig1, ax1 = plt.subplots()
    ax1.errorbar(t_bins, dcm_promedio, yerr=dcm_std, fmt="o", capsize=2, label="DCM promedio ± σ")
    ax1.plot(
        t_bins, pendiente * t_bins + intercepto, "r-", label=f"Recta de ajuste (y={pendiente:.2e}·t) → D ≈ {D:.2e}"
    )
    # ax1.axvline(args.t_max_ajuste, linestyle="--", color="gray", label="Límite ajuste")
    ax1.set_xlabel("Tiempo (s)", fontsize=14)
    ax1.set_ylabel("DCM (m²)", fontsize=14)
    ax1.grid(True)
    ax1.legend()
    ax1.tick_params(axis="both", labelsize=12)
    fig1.tight_layout()
    fig1.savefig("DCM_promedio_vs_t.png")

    # Figura 2
    fig2, ax2 = plt.subplots()
    D_alt, E_min = barrido_d_para_minimo_error(ax2, t_bins, dcm_promedio)
    fig2.tight_layout()
    fig2.savefig("error_vs_D.png")

    print(f"Ajuste lineal → pendiente = {pendiente:.4e}, D = {D:.4e} m²/s")
    print(f"Barrido       → D = {D_alt:.4e} m²/s, error mínimo = {E_min:.2e}")

    plt.show()


if __name__ == "__main__":
    main()
