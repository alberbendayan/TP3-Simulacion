import argparse
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np


def read_snapshots(directory):
    files = sorted(f for f in os.listdir(directory) if f.startswith("snapshot-") and f.endswith(".txt"))
    snapshots = []
    times = []
    for fname in files:
        time = float(fname.replace("snapshot-", "").replace(".txt", ""))
        times.append(time)
        with open(os.path.join(directory, fname)) as f:
            data = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(data))
    return np.array(times), snapshots


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("basedir", help="Directorio con config.json y carpeta snapshots/")
    parser.add_argument("--delta-t", type=float, default=0.1, help="Tamaño del intervalo de tiempo")
    parser.add_argument("--delta-r", type=float, default=0.001, help="Tolerancia de proximidad al borde")
    args = parser.parse_args()

    base_dir = args.basedir
    snap_dir = os.path.join(base_dir, "snapshots")
    config_file = os.path.join(base_dir, "config.json")

    with open(config_file) as f:
        config = json.load(f)

    mass = config["mass"]
    big_radius = config["big_radius"]
    small_radius = config["small_radius"]
    particle_radius = config["particle_radius"]

    L_pared = 2 * np.pi * big_radius
    L_obstaculo = 2 * np.pi * small_radius

    delta_t = args.delta_t
    delta_r = args.delta_r

    times, snapshots = read_snapshots(snap_dir)

    t_min, t_max = times[0], times[-1]
    bin_edges = np.arange(t_min, t_max + delta_t, delta_t)

    # acumuladores por intervalo
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

    tiempos_medios = (bin_edges[:-1] + bin_edges[1:]) / 2
    presion_pared = pared_impulsos / (delta_t * L_pared)
    presion_obstaculo = obstaculo_impulsos / (delta_t * L_obstaculo)

    # graficar
    plt.figure(figsize=(10, 5))
    plt.plot(tiempos_medios, presion_pared, label="Presión Pared")
    plt.plot(tiempos_medios, presion_obstaculo, label="Presión Obstáculo")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Presión [N/m]")
    plt.title("Presión en función del tiempo")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(base_dir, "presiones_vs_tiempo.png"))
    plt.show()


if __name__ == "__main__":
    main()
