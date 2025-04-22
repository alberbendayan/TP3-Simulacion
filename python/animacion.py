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
            positions = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(positions))

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
        redraw_period = config["redraw_period"]

    fig, ax = plt.subplots()

    ax.set_aspect("equal")
    ax.set_xlim(-area_radius, area_radius)
    ax.set_ylim(-area_radius, area_radius)

    area = patches.Circle((0, 0), area_radius, fill=False, color="orange")
    ax.add_patch(area)

    obstacle = patches.Circle((0, 0), obstacle_radius, fill=True, color="gray")
    ax.add_patch(obstacle)

    # Calculate marker size in points^2 so that diameter matches PARTICLE_RADIUS in data units
    fig_dpi = fig.dpi
    xlim = ax.get_xlim()
    data_width = xlim[1] - xlim[0]
    points_per_data = (ax.get_window_extent().width / data_width) * 72 / fig_dpi
    marker_size = (particle_radius * 2 * points_per_data) ** 2

    scat = ax.scatter(snapshots[0][:, 0], snapshots[0][:, 1], s=marker_size, c="blue")

    def update(frame):
        positions = snapshots[frame]
        scat.set_offsets(positions)
        return (scat,)

    ani = animation.FuncAnimation(fig, update, frames=len(snapshots), blit=False, interval=redraw_period * 1000)
    ani.save("animation.mp4", writer="ffmpeg", fps=1 / redraw_period)


if __name__ == "__main__":
    main()
