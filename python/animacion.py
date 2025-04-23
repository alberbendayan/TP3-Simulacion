import glob
import json
import os
import sys

import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


def read_snapshots(directory):
    files = sorted(glob.glob(os.path.join(directory, "snapshot-*.txt")))
    snapshots = []

    for fname in files:
        with open(fname) as f:
            states = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(states))

    return snapshots


def main():
    if len(sys.argv) != 2:
        print("Usage: python animacion.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    snapshots = read_snapshots(os.path.join(directory, "snapshots"))
    config_path = os.path.join(directory, "config.json")

    with open(config_path) as f:
        config = json.load(f)
        area_radius = config["big_radius"]
        obstacle_radius = config["small_radius"]
        particle_radius = config["particle_radius"]
        obstacle_mass = config["obstacle_mass"]

    fig, ax = plt.subplots()

    ax.set_aspect("equal")
    ax.set_xlim(-area_radius, area_radius)
    ax.set_ylim(-area_radius, area_radius)

    area = patches.Circle((0, 0), area_radius, fill=False, color="orange")
    ax.add_patch(area)

    if obstacle_mass == 0:
        obstacle = patches.Circle((0, 0), obstacle_radius, fill=True, color="gray")
        ax.add_patch(obstacle)

    # Inicializamos las partículas
    def color(r):
        return "blue" if r == particle_radius else "gray"

    particles = [patches.Circle((x, y), r, color=color(r)) for x, y, _, _, r in snapshots[0]]

    # Añadimos las partículas al gráfico
    for p in particles:
        ax.add_patch(p)

    def update(frame):
        positions = snapshots[frame]
        for i, p in enumerate(particles):
            p.center = positions[i][:2]
        return particles

    ani = animation.FuncAnimation(fig, update, frames=len(snapshots), blit=False)
    ani.save(os.path.join(directory, "animation.mp4"), writer="ffmpeg", fps=60)


if __name__ == "__main__":
    main()
