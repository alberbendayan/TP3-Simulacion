import glob
import os
import sys

import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np

PARTICLE_RADIUS = 0.0005
AREA_RADIUS = 0.05
OBSTACLE_RADIUS = 0.005


def read_snapshots(directory):
    files = sorted(glob.glob(os.path.join(directory, "snapshot-*.txt")))
    snapshots = []
    for fname in files:
        with open(fname) as f:
            positions = [list(map(float, line.split())) for line in f if line.strip()]
            snapshots.append(np.array(positions))
    return snapshots


def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    snapshots = read_snapshots(directory)

    fig, ax = plt.subplots()

    ax.set_aspect("equal")
    ax.set_xlim(-AREA_RADIUS, AREA_RADIUS)
    ax.set_ylim(-AREA_RADIUS, AREA_RADIUS)

    area = patches.Circle((0, 0), AREA_RADIUS, fill=False, color="orange")
    ax.add_patch(area)

    obstacle = patches.Circle((0, 0), OBSTACLE_RADIUS, fill=True, color="gray")
    ax.add_patch(obstacle)

    # Calculate marker size in points^2 so that diameter matches PARTICLE_RADIUS in data units
    fig_dpi = fig.dpi
    xlim = ax.get_xlim()
    data_width = xlim[1] - xlim[0]
    points_per_data = (ax.get_window_extent().width / data_width) * 72 / fig_dpi
    marker_size = (PARTICLE_RADIUS * 2 * points_per_data) ** 2

    scat = ax.scatter(
        snapshots[0][:, 0],
        snapshots[0][:, 1],
        s=marker_size,
        c="blue",
    )

    def update(frame):
        positions = snapshots[frame]
        scat.set_offsets(positions)
        return (scat,)

    ani = animation.FuncAnimation(
        fig, update, frames=len(snapshots), blit=False, interval=100
    )
    ani.save("animation.mp4", writer="ffmpeg", fps=60)
    plt.show()


if __name__ == "__main__":
    main()
