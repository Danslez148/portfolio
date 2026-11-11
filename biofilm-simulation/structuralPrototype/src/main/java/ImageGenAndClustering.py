import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
from sklearn.cluster import DBSCAN
import matplotlib.cm as cm
from matplotlib.patches import Patch

import sys
import os
import re
import numpy as np


# ----------------- Patch Creation Functions -----------------
def create_capsule_patches(x, y, angle, length, width=0.5):
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
    return [patches.Circle((x, y), radius)]

# ----------------- Load Data -----------------
print("Loading data...")
inputFile = sys.argv[1]
data = pd.read_csv(inputFile)

times = sorted(data["time"].unique())
x_min, x_max = data["x"].min() - 5, data["x"].max() + 5
y_min, y_max = data["y"].min() - 5, data["y"].max() + 5

filename = os.path.basename(inputFile)
start = filename.rfind("_M")
end = filename.rfind(".csv")
outputSuffix = filename[start:end]
resultsfolder = f"results{outputSuffix}"
os.makedirs(resultsfolder, exist_ok=True)

# ----------------- Last Frame Data -----------------
last_time = times[-1]
last_data = data[data["time"] == last_time].copy()
eps_data = last_data[last_data["type"] == "EPSParticle"].copy()
bacteria_data = last_data[last_data["type"] == "BacteriaCell"].copy()

# ----------------- Function to Plot Clustered Data -----------------
def plot_clustered(data_subset, type_name, filename):
    radius = 0.65 if type_name == "EPS" else 1.65
    coords = data_subset[["x", "y"]].to_numpy()
    clustering = DBSCAN(eps=radius, min_samples=2).fit(coords)
    data_subset["cluster"] = clustering.labels_

    # Save cluster sizes summary (exclude noise = -1)
    cluster_sizes_df = (
        data_subset[data_subset["cluster"] != -1]
        .groupby("cluster")
        .size()
        .reset_index(name="size")
    )
    sizes_filename = filename.replace(".png", f"cluster_sizes{outputSuffix}.csv")
    cluster_sizes_df.to_csv(sizes_filename, index=False)
    print(f"Saved cluster sizes -> {sizes_filename}")

    # Convert to dict for lookup
    cluster_sizes = dict(zip(cluster_sizes_df["cluster"], cluster_sizes_df["size"]))

    # Define fixed color palette (smallest to largest)
    color_palette = [
        "#FFE735",  # yellow
        "#FF9233",  # orange
        "#FF4040",  # red
        "#D0143A",  # crimson
        "#7E0A42",  # raspberry
        "#530037"   # deep purple
    ]
      # Compute dynamic bin edges
    sizes = list(cluster_sizes.values())
    if sizes:
        min_size = min(sizes)
        max_size = max(sizes)
        bin_edges = np.linspace(min_size, max_size, num=len(color_palette) + 1)
    else:
        bin_edges = [0] * (len(color_palette) + 1)

    # Assign colors based on bin index
    def assign_color(cluster_label):
        if cluster_label == -1:
            return "lightgray"
        size = cluster_sizes.get(cluster_label, 0)
        bin_index = np.digitize(size, bin_edges, right=False) - 1
        bin_index = min(bin_index, len(color_palette) - 1)
        return color_palette[bin_index]

    colors = [assign_color(row["cluster"]) for _, row in data_subset.iterrows()]

     # Plotting
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(f"{type_name} Clusters at Time {last_time}")
    legend_handles = []
    for i in range(len(bin_edges) - 1):
        label = f"{int(bin_edges[i])}–{int(bin_edges[i+1])}"
        color = color_palette[i]
        legend_handles.append(Patch(facecolor=color, edgecolor="none", label=label))

    # Add legend to plot
    ax.legend(handles=legend_handles, title="Cluster Size", loc="upper right", frameon=True)
    # create and add patches to the plot
    patches_list = []
    for (_, row), color in zip(data_subset.iterrows(), colors):
        if type_name == "Bacteria":
            patches_here = create_capsule_patches(row["x"], row["y"], row["angle"], row["length"] - 1, width=0.5)
        else:
            patches_here = create_eps_patch(row["x"], row["y"], radius=0.25)
        for p in patches_here:
            p.set_facecolor(color)
            p.set_edgecolor("none")
            p.set_linewidth(0.3)
            patches_list.append(p)

    collection = PatchCollection(patches_list, match_original=True)
    ax.add_collection(collection)
    plt.savefig(filename, dpi=300)
    plt.close(fig)

# ----------------- Plot Both Types (Bacteria Blue, EPS Red) -----------------
def plot_both(data, filename):
    fig, ax = plt.subplots(figsize=(8,8))
    ax.set_aspect("equal")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(f"Bacteria (blue) + EPS (red) at Time {last_time}")

    patches_list = []
    for _, row in data.iterrows():
        if row["type"] == "BacteriaCell":
            color = "blue"
            patches_here = create_capsule_patches(row["x"], row["y"], row["angle"], row["length"]-1, width=0.5)
        else:
            color = "red"
            patches_here = create_eps_patch(row["x"], row["y"], radius=0.25)
        for p in patches_here:
            p.set_facecolor(color)
            p.set_edgecolor("none")
            p.set_linewidth(0.3)
            patches_list.append(p)
    collection = PatchCollection(patches_list, match_original=True)
    ax.add_collection(collection)
    plt.savefig(filename, dpi=300)
    plt.close(fig)

# ----------------- Generate Images & CSVs -----------------
print("Generating images and CSVs...")

plot_clustered(eps_data, "EPS", os.path.join(resultsfolder, f"eps_clusters{outputSuffix}.png"))
plot_clustered(bacteria_data, "Bacteria", os.path.join(resultsfolder, f"bacteria_clusters{outputSuffix}.png"))
plot_both(last_data, os.path.join(resultsfolder, f"bacteria_eps{outputSuffix}.png"))

print("Done! Saved:")
print(" - eps_clusters.png + eps_cluster_sizes.csv")
print(" - bacteria_clusters.png + bacteria_cluster_sizes.csv")
print(" - bacteria_eps.png")
