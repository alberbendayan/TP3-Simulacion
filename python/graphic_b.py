import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np


def read_snapshots(directory, time_limit):
    files = sorted(f for f in os.listdir(directory) if f.startswith("snapshot-") and f.endswith(".txt"))
    snapshots = []
    times = []
    for fname in files:
        time = float(fname.replace("snapshot-", "").replace(".txt", ""))
        if time_limit != 0 and time > time_limit:
            break
        times.append(time)
        with open(os.path.join(directory, fname)) as f:
            data = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(data))
    return np.array(times), snapshots


def procesar_simulacion(base_dir, delta_t, delta_r, time_limit):
    snap_dir = os.path.join(base_dir, "snapshots")
    config_file = os.path.join(base_dir, "config.json")

    with open(config_file) as f:
        config = json.load(f)

    mass = config["mass"]
    big_radius = config["big_radius"]
    small_radius = config["small_radius"]

    L_pared = 2 * np.pi * big_radius
    L_obstaculo = 2 * np.pi * small_radius

    times, snapshots = read_snapshots(snap_dir, time_limit)

    t_min, t_max = times[0], times[-1]
    bin_edges = np.arange(t_min, t_max + delta_t, delta_t)

    pared_impulsos = np.zeros(len(bin_edges) - 1)
    obstaculo_impulsos = np.zeros(len(bin_edges) - 1)

    for time, snapshot in zip(times, snapshots):
        idx = np.searchsorted(bin_edges, time, side="right") - 1
        if idx < 0 or idx >= len(pared_impulsos):
            continue

        for row in snapshot:
            x, y, vx, vy, _ = row
            r = np.hypot(x, y)
            v = np.hypot(vx, vy)
            impulso = 2 * mass * v

            if abs(r - big_radius) <= delta_r:
                pared_impulsos[idx] += impulso
            elif abs(r - small_radius) <= delta_r:
                obstaculo_impulsos[idx] += impulso

    presion_pared = pared_impulsos / (delta_t * L_pared)
    presion_obstaculo = obstaculo_impulsos / (delta_t * L_obstaculo)
    presion_total = (presion_obstaculo + presion_pared) / 2

    presion_promedio = np.mean(presion_total)
    return presion_promedio


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+", help="Carpetas de simulaciones con la partícula grande")
    parser.add_argument("--delta-t", type=float, default=0.1)
    parser.add_argument("--delta-r", type=float, default=0.00055)
    parser.add_argument("--time-limit", type=float, default=0.0, help="Tiempo máximo para la simulación")
    args = parser.parse_args()

    datos = {}
    for path in args.dirs:
        with open(os.path.join(path, "config.json")) as f:
            config = json.load(f)

        v0 = config["speed"]
        P = procesar_simulacion(path, args.delta_t, args.delta_r, args.time_limit)
        T = v0**2
        datos[T] = P

    Ts = sorted(datos.keys())
    Ps = [datos[T] for T in Ts]

    plt.figure(figsize=(8, 5))
    plt.plot(Ts, Ps, "o:", color="blue", linewidth=1)
    plt.xlabel("Temperatura", fontsize=14)
    plt.ylabel("Presión promedio [N/m]", fontsize=14)
    plt.tick_params(axis="both", labelsize=12)
    plt.grid(True)
    plt.tight_layout()
    for dirpath in args.dirs:
        plt.savefig(os.path.join(dirpath, "presion_vs_temperatura.png"))
    plt.show()


if __name__ == "__main__":
    main()
