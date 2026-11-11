import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import numpy as np

# ----------------- Patch Creation Functions -----------------
def create_capsule_patches(x, y, angle, length, width=0.5):
    """Create capsule patches for BacteriaCell."""
    circ1 = patches.Circle((-length/2, 0), width/2)
    circ2 = patches.Circle((length/2, 0), width/2)
    rect = patches.Rectangle((-length/2, -width/2), length, width)

    trans = (plt.matplotlib.transforms.Affine2D()
             .rotate(angle)
             .translate(x, y))

    for shape in (rect, circ1, circ2):
        shape.set_transform(trans)

    return [rect, circ1, circ2]

def create_eps_patch(x, y, radius=0.25):
    """Create EPS particle as a circle patch."""
    return [patches.Circle((x, y), radius)]

# ----------------- Load Data -----------------
print("Loading data...")
data = pd.read_csv(r"./StructuralPrototype/Output/multithreaded_biofilm_M0.0_4.0-4.0-7.0.csv")

# ----------------- Setup Figure for Animation -----------------
fig, ax = plt.subplots(figsize=(8,8))
ax.set_aspect("equal")

x_min, x_max = data["x"].min() - 5, data["x"].max() + 5
y_min, y_max = data["y"].min() - 5, data["y"].max() + 5
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

collection = PatchCollection([], edgecolor='black', linewidth=0.3)
ax.add_collection(collection)
title_text = ax.text(0.5, 0.95, "", transform=ax.transAxes, ha='center')

# ----------------- Animation Update Function -----------------
times = sorted(data["time"].unique())

def update(frame):
    tdata = data[data["time"] == frame]
    frame_patches = []
    frame_colors = []

    for _, row in tdata.iterrows():
        if row["type"] == "BacteriaCell":
            patches_here = create_capsule_patches(
                row["x"], row["y"], row["angle"], row["length"]-1, width=0.5
            )
            frame_colors.extend(['blue'] * len(patches_here))
        elif row["type"] == "EPSParticle":
            patches_here = create_eps_patch(row["x"], row["y"], radius=0.25)
            frame_colors.extend(['red'] * len(patches_here))
        frame_patches.extend(patches_here)

    collection.set_paths(frame_patches)
    collection.set_facecolor(frame_colors)
    title_text.set_text(f"Time = {frame}")
    return collection, title_text

# ----------------- Create & Save Animation -----------------
print("Creating animation...")
ani = animation.FuncAnimation(
    fig, update, frames=times,
    repeat=False, blit=True, interval=500
)

print("Saving animation...")

def progress(i, n):
    # i = current frame index, n = total frames
    print(f"Processed timestep {i+1}/{n}")

ani.save(
    "rods_fast.mp4",
    writer="ffmpeg",
    fps=2,
    bitrate=1800,
    progress_callback=progress
)


print("Animation saved successfully!")
