import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
import matplotlib.patches as patches
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.cm as cm
from numba import jit
from scipy.spatial.distance import cdist

# ----------------- Optimized Distance Functions -----------------
@jit(nopython=True)
def point_to_segment_distance(px, py, x1, y1, x2, y2):
    """Fast point-to-segment distance calculation"""
    A = px - x1
    B = py - y1
    C = x2 - x1
    D = y2 - y1
    
    dot = A * C + B * D
    len_sq = C * C + D * D
    
    if len_sq == 0:
        return np.sqrt(A * A + B * B)
    
    param = dot / len_sq
    
    if param < 0:
        xx, yy = x1, y1
    elif param > 1:
        xx, yy = x2, y2
    else:
        xx = x1 + param * C
        yy = y1 + param * D
    
    dx = px - xx
    dy = py - yy
    return np.sqrt(dx * dx + dy * dy)

@jit(nopython=True)
def segment_to_segment_distance(x1a, y1a, x1b, y1b, x2a, y2a, x2b, y2b):
    """Fast segment-to-segment distance calculation"""
    # Check all combinations of endpoints to segments
    d1 = point_to_segment_distance(x1a, y1a, x2a, y2a, x2b, y2b)
    d2 = point_to_segment_distance(x1b, y1b, x2a, y2a, x2b, y2b)
    d3 = point_to_segment_distance(x2a, y2a, x1a, y1a, x1b, y1b)
    d4 = point_to_segment_distance(x2b, y2b, x1a, y1a, x1b, y1b)
    
    return min(d1, d2, d3, d4)

@jit(nopython=True)
def compute_distance_matrix_fast(coords):
    """Optimized distance matrix computation"""
    N = coords.shape[0]
    dist_matrix = np.zeros((N, N))
    
    for i in range(N):
        for j in range(i+1, N):
            d = segment_to_segment_distance(
                coords[i,0], coords[i,1], coords[i,2], coords[i,3],
                coords[j,0], coords[j,1], coords[j,2], coords[j,3]
            )
            dist_matrix[i,j] = d
            dist_matrix[j,i] = d
    
    return dist_matrix

# ----------------- Optimized Patch Creation -----------------
def create_all_capsule_patches(bacteria_data, colors):
    """Vectorized patch creation"""
    patches_list = []
    
    # Pre-calculate all transformations
    x_vals = bacteria_data["x"].values
    y_vals = bacteria_data["y"].values
    angles = bacteria_data["angle"].values
    lengths = bacteria_data["length"].values - 1  # Apply length adjustment once
    
    for i, (x, y, angle, length) in enumerate(zip(x_vals, y_vals, angles, lengths)):
        color = colors[i]
        
        # Create shapes with pre-calculated values
        half_length = length / 2
        width = 0.5
        
        # Rectangle
        rect = patches.Rectangle((-half_length, -width/2), length, width)
        
        # Circles
        circ1 = patches.Circle((-half_length, 0), width/2)
        circ2 = patches.Circle((half_length, 0), width/2)
        
        # Apply transformation once
        trans = (plt.matplotlib.transforms.Affine2D()
                .rotate(angle)
                .translate(x, y))
        
        for shape in (rect, circ1, circ2):
            shape.set_transform(trans)
            shape.set_facecolor(color)
            shape.set_edgecolor("none")
            shape.set_linewidth(0.3)
            patches_list.append(shape)
    
    return patches_list

# ----------------- Main Analysis -----------------
print("Loading data")
data = pd.read_csv(r"./StructuralPrototype/Output/multithreaded_biofilm_M0.0_2.0-2.0-2.0.csv")

# Get last time data more efficiently
last_time = data["time"].max()
bacteria_data = data[(data["time"] == last_time) & (data["type"] == "BacteriaCell")].copy().reset_index(drop=True)

print(f"Processing {len(bacteria_data)} bacteria")

# Pre-calculate bounds
x_min, x_max = data["x"].min() - 5, data["x"].max() + 5
y_min, y_max = data["y"].min() - 5, data["y"].max() + 5

# ----------------- Optimized Segment Computation -----------------
print("Computing segment coordinates")
angles = bacteria_data["angle"].values
lengths = bacteria_data["length"].values
x_coords = bacteria_data["x"].values
y_coords = bacteria_data["y"].values

# Vectorized segment calculation
dx = (lengths / 2) * np.cos(angles)
dy = (lengths / 2) * np.sin(angles)

# Create coordinate array for distance calculation
# Format: [x1, y1, x2, y2] for each segment
segment_coords = np.column_stack([
    x_coords - dx, y_coords - dy,  # start points
    x_coords + dx, y_coords + dy   # end points
])

# ----------------- Optimized Distance Matrix -----------------
print("Computing distance matrix")
dist_matrix = compute_distance_matrix_fast(segment_coords)

# ----------------- DBSCAN Clustering -----------------
print("Running DBSCAN")
eps_touch = 0.65
clustering = DBSCAN(eps=eps_touch, min_samples=2, metric="precomputed").fit(dist_matrix)
bacteria_data["cluster"] = clustering.labels_

# ----------------- Save Results -----------------
cluster_sizes = (
    bacteria_data[bacteria_data["cluster"] != -1]
    .groupby("cluster")
    .size()
    .reset_index(name="size")
)
cluster_sizes.to_csv("bacteria_cluster_sizes.csv", index=False)
print("Saved cluster sizes -> bacteria_cluster_sizes.csv")

# ----------------- Optimized Plotting -----------------
print("Creating plot")
num_clusters = len(set(bacteria_data["cluster"])) - (1 if -1 in bacteria_data["cluster"].values else 0)
cmap = cm.get_cmap("tab10", max(num_clusters, 1))

# Pre-calculate all colors
colors = []
for cluster_id in bacteria_data["cluster"]:
    if cluster_id == -1:
        colors.append("lightgray")
    else:
        colors.append(cmap(cluster_id))

# Create figure
fig, ax = plt.subplots(figsize=(8,8))
ax.set_aspect("equal")
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_title(f"Bacteria Clusters at Time {last_time}")

# Create all patches at once
patches_list = create_all_capsule_patches(bacteria_data, colors)

# Add collection
collection = PatchCollection(patches_list, match_original=True)
ax.add_collection(collection)

plt.savefig("bacteria_clusters.png", dpi=300, bbox_inches='tight')
plt.close(fig)
print("Saved bacteria_clusters.png")