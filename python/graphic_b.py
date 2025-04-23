import argparse
import json
import os
import numpy as np
import matplotlib.pyplot as plt


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


def procesar_simulacion(base_dir, delta_t, delta_r):
    snap_dir = os.path.join(base_dir, "snapshots")
    config_file = os.path.join(base_dir, "config.json")

    with open(config_file) as f:
        config = json.load(f)

    mass = config["mass"]
    big_radius = config["big_radius"]
    small_radius = config["small_radius"]

    L_pared = 2 * np.pi * big_radius
    L_obstaculo = 2 * np.pi * small_radius

    times, snapshots = read_snapshots(snap_dir)

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
    parser.add_argument("dir_v3", help="Directorio para v0=3")
    parser.add_argument("dir_v6", help="Directorio para v0=6")
    parser.add_argument("dir_v10", help="Directorio para v0=10")
    parser.add_argument("--delta-t", type=float, default=0.1)
    parser.add_argument("--delta-r", type=float, default=0.001)
    args = parser.parse_args()


    config_file3 = os.path.join(args.dir_v3, "config.json")
    with open(config_file3) as f:
        config3 = json.load(f)
        v3 = config3["speed"]

    config_file6 = os.path.join(args.dir_v6, "config.json")
    with open(config_file6) as f:
        config6 = json.load(f)
        v6 = config6["speed"]

    config_file10 = os.path.join(args.dir_v10, "config.json")
    with open(config_file10) as f:
        config10 = json.load(f)
        v10 = config10["speed"]

    datos = {}
    for v0, path in zip([v3, v6, v10], [args.dir_v3, args.dir_v6, args.dir_v10]):
        P = procesar_simulacion(path, args.delta_t, args.delta_r)
        T = v0 ** 2
        datos[T] = P

    Ts = sorted(datos.keys())
    Ps = [datos[T] for T in Ts]

    plt.figure(figsize=(8, 5))
    plt.plot(Ts, Ps, '-', color='blue', label="P vs T (T = v₀²)")
    plt.scatter(Ts, Ps, color='black', zorder=5)

    T6 = v6 ** 2
    if T6 in datos:
        plt.scatter([T6], [datos[T6]], color='black', zorder=5)

    plt.xlabel("Temperatura relativa (T ∝ v₀²)")
    plt.ylabel("Presión promedio [N/m]")
    plt.title("Presión vs Temperatura relativa")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("presion_vs_temperatura.png")
    plt.show()

if __name__ == "__main__":
    main()
