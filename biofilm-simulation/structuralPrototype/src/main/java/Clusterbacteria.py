import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import numpy as np
from shapely.geometry import LineString
from sklearn.cluster import DBSCAN
import matplotlib.cm as cm

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

# ----------------- Load Data -----------------
print("Loading data")
data = pd.read_csv(r"./StructuralPrototype/Output/multithreaded_biofilm_M500.0_2.0-2.0-2.0.csv")
times = sorted(data["time"].unique())
last_time = times[-1]
last_data = data[data["time"] == last_time].copy()
bacteria_data = last_data[last_data["type"] == "BacteriaCell"].copy()

x_min, x_max = data["x"].min() - 5, data["x"].max() + 5
y_min, y_max = data["y"].min() - 5, data["y"].max() + 5

# ----------------- Compute Bacteria Segments -----------------
def segment_coords(row):
    x, y, angle, length = row["x"], row["y"], row["angle"], row["length"]
    dx = (length/2) * np.cos(angle)
    dy = (length/2) * np.sin(angle)
    return np.array([x-dx, y-dy]), np.array([x+dx, y+dy])

segments = [segment_coords(r) for _, r in bacteria_data.iterrows()]

def segment_distance(seg1, seg2):
    return LineString(seg1).distance(LineString(seg2))

# ----------------- Build Distance Matrix -----------------
N = len(segments)
dist_matrix = np.zeros((N, N))
for i in range(N):
    for j in range(i+1, N):
        d = segment_distance(segments[i], segments[j])
        dist_matrix[i,j] = dist_matrix[j,i] = d

# ----------------- DBSCAN on Segment Distances -----------------
# eps: distance for rods to be considered touching
eps_touch = 0.65  # adjust depending on width
clustering = DBSCAN(eps=eps_touch, min_samples=2, metric="precomputed").fit(dist_matrix)
bacteria_data["cluster"] = clustering.labels_

# ----------------- Save Cluster Sizes -----------------
cluster_sizes = (
    bacteria_data[bacteria_data["cluster"] != -1]
    .groupby("cluster")
    .size()
    .reset_index(name="size")
)
cluster_sizes.to_csv("bacteria_cluster_sizes.csv", index=False)
print("Saved cluster sizes -> bacteria_cluster_sizes.csv")

# ----------------- Plot Bacteria Clusters -----------------
num_clusters = len(set(bacteria_data["cluster"])) - (1 if -1 in bacteria_data["cluster"].values else 0)
cmap = cm.get_cmap("tab10", num_clusters if num_clusters > 0 else 1)

colors = []
for _, row in bacteria_data.iterrows():
    if row["cluster"] == -1:
        colors.append("lightgray")
    else:
        colors.append(cmap(row["cluster"]))

fig, ax = plt.subplots(figsize=(8,8))
ax.set_aspect("equal")
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_title(f"Bacteria Clusters at Time {last_time}")

patches_list = []
for (_, row), color in zip(bacteria_data.iterrows(), colors):
    patches_here = create_capsule_patches(row["x"], row["y"], row["angle"], row["length"]-1, width=0.5)
    for p in patches_here:
        p.set_facecolor(color)
        p.set_edgecolor("none")
        p.set_linewidth(0.3)
        patches_list.append(p)

collection = PatchCollection(patches_list, match_original=True)
ax.add_collection(collection)
plt.savefig("bacteria_clusters.png", dpi=300)
plt.close(fig)

print("Saved bacteria_clusters.png")
