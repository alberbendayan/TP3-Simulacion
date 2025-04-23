import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np


def read_snapshots(directory):
    files = sorted(f for f in os.listdir(directory) if f.startswith("snapshot-") and f.endswith(".txt"))
    times = []
    snapshots = []
    for fname in files:
        time = float(fname.replace("snapshot-", "").replace(".txt", ""))
        times.append(time)
        with open(os.path.join(directory, fname)) as f:
            data = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(data))
    return np.array(times), snapshots


def calcular_temperatura(snapshot_list):
    velocidades = []
    for snap in snapshot_list:
        v_squared = np.sum(snap[:, 2:] ** 2, axis=1)
        velocidades.extend(v_squared)
    return np.mean(velocidades)  # T proporcional a <v^2>


def calcular_presion_promedio_bineada(times, impulsos, L, delta_t=0.1, t_frac=0.5):
    t_min = times[0] + (times[-1] - times[0]) * t_frac
    t_max = times[-1]

    bins = np.arange(t_min, t_max + delta_t, delta_t)
    impulso_por_bin = np.zeros(len(bins) - 1)

    for t, dp in zip(times, impulsos):
        if t < t_min or t > t_max:
            continue
        idx = np.searchsorted(bins, t, side="right") - 1
        impulso_por_bin[idx] += dp

    presiones = impulso_por_bin / (delta_t * L)
    return np.mean(presiones)


def analizar_simulacion(path, delta_r=0.001, delta_t=0.1):
    with open(os.path.join(path, "config.json")) as f:
        config = json.load(f)

    mass = config["mass"]
    R_pared = config["big_radius"]
    R_obs = config["small_radius"]

    L_pared = 2 * np.pi * R_pared

    times, snapshots = read_snapshots(os.path.join(path, "snapshots"))

    impulso_pared = []
    for snap in snapshots:
        total = 0.0
        for row in snap:
            x, y, vx, vy, _ = row
            r = np.hypot(x, y)
            v = np.hypot(vx, vy)
            if abs(r - R_pared) <= delta_r:
                total += 2 * mass * v
        impulso_pared.append(total)

    impulso_pared = np.array(impulso_pared)
    T = calcular_temperatura(snapshots[int(len(snapshots) * 0.5) :])
    P = calcular_presion_promedio_bineada(times, impulso_pared, L_pared, delta_t=delta_t)

    return P, T


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+", help="Directorios de simulaciones")
    parser.add_argument("--labels", nargs="+", help="Etiquetas opcionales para cada directorio")
    parser.add_argument("--delta-r", type=float, default=0.001, help="Tolerancia al borde [m]")
    parser.add_argument("--delta-t", type=float, default=0.1, help="Intervalo de tiempo [s]")
    args = parser.parse_args()

    labels = args.labels if args.labels else args.dirs
    resultados = []

    for path, label in zip(args.dirs, labels):
        print(f"Procesando {label}...")
        P, T = analizar_simulacion(path, args.delta_r, args.delta_t)
        print(f"  → P = {P:.4f}, T = {T:.4f}")
        resultados.append((label, P, T))

    # graficar
    etiquetas, presiones, temperaturas = zip(*resultados)
    plt.figure()
    plt.plot(temperaturas, presiones, "o-", label="Simulaciones")
    for l, t, p in zip(etiquetas, temperaturas, presiones):
        plt.text(t, p, l)

    plt.xlabel("Temperatura relativa (⟨v²⟩)")
    plt.ylabel("Presión promedio [N/m]")
    plt.title("P vs T (ley de gases ideales)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("P_vs_T.png")
    plt.show()


if __name__ == "__main__":
    main()
