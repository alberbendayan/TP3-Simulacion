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

    area = patches.Circle((0, 0), AREA_RADIUS, fill=False, color="orange", lw=4)
    ax.add_patch(area)

    obstacle = patches.Circle((0, 0), OBSTACLE_RADIUS, fill=True, color="gray")
    ax.add_patch(obstacle)

    # scat = ax.scatter([], [], s=(PARTICLE_RADIUS * 2 * 1000) ** 2, color="blue")
    scat = ax.scatter(
        snapshots[0][:, 0],
        snapshots[0][:, 1],
        # s=(PARTICLE_RADIUS * 2 * 1000) ** 2,
        c="blue",
    )

    # def init():
    #     # scat.set_offsets(np.empty((0, 2)))
    #     scat.set_offsets([])
    #     return (scat,)

    def update(frame):
        positions = snapshots[frame]
        scat.set_offsets(positions)
        return (scat,)

    ani = animation.FuncAnimation(
        fig, update, frames=len(snapshots), blit=False, interval=100
    )
    ani.save("animation.mp4", writer="ffmpeg")
    plt.show()


if __name__ == "__main__":
    main()
