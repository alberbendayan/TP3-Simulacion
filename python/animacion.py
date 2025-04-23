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

    particles = [patches.Circle((x, y), r, color="black") for x, y, _, _, r in snapshots[0][:-1]]
    last_particle = snapshots[0][-1]
    particles.append(patches.Circle((0, 0), last_particle[4], color="gray"))

    # Añadimos las partículas al gráfico
    for p in particles:
        ax.add_patch(p)

    colors = ["red", "blue", "green", "purple", "orange", "yellow", "pink"]
    count = 0

    def update(frame):
        nonlocal count
        count += 1
        positions = snapshots[frame]
        for i, p in enumerate(particles):
            p.center = positions[i][:2]
            if i == len(particles) - 1:
                p.set_radius(positions[i][4])
                p.set_color(colors[count // 5 % len(colors)])
        return particles

    ani = animation.FuncAnimation(fig, update, frames=len(snapshots), blit=False)
    ani.save(os.path.join(directory, "animation.mp4"), writer="ffmpeg", fps=60)


if __name__ == "__main__":
    main()
