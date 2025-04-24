import argparse
import json
import os
import matplotlib.pyplot as plt
import numpy as np


def read_snapshots(directory):
    files = sorted(f for f in os.listdir(directory) if f.startswith("snapshot-") and f.endswith(".txt"))
    times, snapshots = [], []
    for fname in files:
        time = float(fname.replace("snapshot-", "").replace(".txt", ""))
        times.append(time)
        with open(os.path.join(directory, fname)) as f:
            data = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(data))
    return np.array(times), snapshots


def contar_choques_obstaculo(path, delta_r=0.001):
    with open(os.path.join(path, "config.json")) as f:
        config = json.load(f)

    small_radius = config["small_radius"]
    particle_count = config["particle_count"]
    times, snapshots = read_snapshots(os.path.join(path, "snapshots"))

    choque_total, choque_distintos = [], []
    particulas_ya_chocadas = set()
    choques_totales = choques_unicos = 0
    tiempos = []

    for t, snap in zip(times, snapshots):
        choque_en_este_evento = 0
        nuevas_particulas = set()

        for idx, row in enumerate(snap):
            x, y = row[0], row[1]
            dist = np.hypot(x, y)

            if abs(dist - small_radius) <= delta_r:
                choque_en_este_evento += 1
                if idx not in particulas_ya_chocadas:
                    nuevas_particulas.add(idx)

        choques_totales += choque_en_este_evento
        choques_unicos += len(nuevas_particulas)
        particulas_ya_chocadas.update(nuevas_particulas)

        tiempos.append(t)
        choque_total.append(choques_totales)
        choque_distintos.append(choques_unicos)

    return np.array(tiempos), np.array(choque_total), np.array(choque_distintos), particle_count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+", help="Carpetas de simulaciones")
    parser.add_argument("--delta-r", type=float, default=0.001, help="Tolerancia al obstáculo")
    args = parser.parse_args()

    plt.figure()

    for dirpath in args.dirs:
        tiempos, total, distintos, particle_count = contar_choques_obstaculo(dirpath, delta_r=args.delta_r)

        label = os.path.basename(os.path.normpath(dirpath))
        plt.plot(tiempos, distintos, label=f"{label}")

    plt.xlabel("Tiempo [s]")
    plt.ylabel("Choques únicos por partícula")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("choques_unicos_multisim.png")
    plt.show()


if __name__ == "__main__":
    main()
