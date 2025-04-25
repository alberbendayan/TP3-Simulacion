import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np


def read_snapshots(directory, time_limit):
    files = sorted(f for f in os.listdir(directory) if f.startswith("snapshot-") and f.endswith(".txt"))
    times, snapshots = [], []
    for fname in files:
        time = float(fname.replace("snapshot-", "").replace(".txt", ""))
        if time_limit != 0 and time > time_limit:
            break
        times.append(time)
        with open(os.path.join(directory, fname)) as f:
            data = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(data))
    return np.array(times), snapshots


def contar_choques_obstaculo(path, delta_r=0.001, time_limit=0.0):
    with open(os.path.join(path, "config.json")) as f:
        config = json.load(f)

    small_radius = config["small_radius"]
    particle_count = config["particle_count"]
    times, snapshots = read_snapshots(os.path.join(path, "snapshots"), time_limit)
    speed = config["speed"]
    max_particles = particle_count * (0.99 if speed == 1 else 1)

    choque_total, choque_distintos = [], []
    particulas_ya_chocadas = set()
    choques_totales = choques_unicos = 0
    tiempos = []
    tiempo_estacionario = 0

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

        if tiempo_estacionario == 0 and choques_unicos >= max_particles:
            tiempo_estacionario = t

    return np.array(tiempos), np.array(choque_total), np.array(choque_distintos), particle_count, tiempo_estacionario


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirs", nargs="+", help="Carpetas de simulaciones")
    parser.add_argument("--delta-r", type=float, default=0.001, help="Tolerancia al obstáculo")
    parser.add_argument("--time-limit", type=float, default=0.0, help="Tiempo máximo a considerar")
    args = parser.parse_args()

    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()
    fig4, ax4 = plt.subplots()

    velocidades = []
    pendientes = []
    tiempos_estacionarios = []

    for dirpath in args.dirs:
        with open(os.path.join(dirpath, "config.json")) as f:
            config = json.load(f)
            speed = config["speed"]
            velocidades.append(speed ** 2)

        tiempos, total, distintos, count, t_est = contar_choques_obstaculo(dirpath, args.delta_r, args.time_limit)

        label = f"v = {speed:.2f} m/s"
        ax1.plot(tiempos, total, label=label)
        ax2.plot(tiempos, distintos, label=label)

        tiempos_estacionarios.append(t_est)

        if len(tiempos) >= 2:
            coeffs = np.polyfit(tiempos, total, 1)
            pendiente = coeffs[0]
        else:
            pendiente = 0.0
        pendientes.append(pendiente)

    ax1.set_xlabel("Tiempo [s]", fontsize=14)
    ax1.set_ylabel("Cantidad de choques totales", fontsize=14)
    ax1.tick_params(axis='both', labelsize=12)
    ax1.grid(True)
    ax1.legend()
    ax1.set_ylim(0, None)
    fig1.tight_layout()

    ax2.set_xlabel("Tiempo [s]", fontsize=14)
    ax2.set_ylabel("Cantidad de choques únicos", fontsize=14)
    ax2.tick_params(axis='both', labelsize=12)
    ax2.grid(True)
    ax2.legend()
    ax2.set_ylim(0, None)
    fig2.tight_layout()

    ax3.set_xlabel("Velocidad", fontsize=14)
    ax3.set_ylabel("Pendiente", fontsize=14)
    ax3.tick_params(axis='both', labelsize=12)
    ax3.grid(True)
    ax3.plot(velocidades, pendientes, "o")
    ax3.set_ylim(0, None)
    fig3.tight_layout()

    ax4.set_xlabel("Velocidad", fontsize=14)
    ax4.set_ylabel("Tiempo estacionario", fontsize=14)
    ax4.tick_params(axis='both', labelsize=12)
    ax4.grid(True)
    ax4.plot(velocidades, tiempos_estacionarios, "o")
    ax4.set_ylim(0, None)
    fig4.tight_layout()

    for dirpath in args.dirs:
        fig1.savefig(os.path.join(dirpath, "choques_totales_obstaculo.png"))
        fig2.savefig(os.path.join(dirpath, "choques_unicos_obstaculo.png"))
        fig3.savefig(os.path.join(dirpath, "pendiente_vs_velocidad.png"))
        fig4.savefig(os.path.join(dirpath, "tiempo_estacionario_vs_velocidad.png"))

    plt.show()


if __name__ == "__main__":
    main()
