import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.collections import PatchCollection, LineCollection
import matplotlib.patches as patches
import numpy as np
import sys

# ----------------- Optimized Patch Creation Functions -----------------
def create_capsule_vertices(x, y, angle, length, width=0.5):
    """Create capsule as polygon vertices (faster than separate patches)."""
    # Create capsule outline as single polygon
    half_length = length / 2
    half_width = width / 2
    
    # Create semicircle points
    n_points = 8  # Reduced for speed
    angles1 = np.linspace(np.pi/2, 3*np.pi/2, n_points)
    angles2 = np.linspace(-np.pi/2, np.pi/2, n_points)
    
    # Left semicircle
    left_x = -half_length + (half_width * np.cos(angles1))
    left_y = half_width * np.sin(angles1)
    
    # Right semicircle  
    right_x = half_length + (half_width * np.cos(angles2))
    right_y = half_width * np.sin(angles2)
    
    # Combine points
    vertices = np.column_stack([
        np.concatenate([left_x, right_x]),
        np.concatenate([left_y, right_y])
    ])
    
    # Apply rotation and translation
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    rot_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    vertices = vertices @ rot_matrix.T
    vertices += np.array([x, y])
    
    return vertices

def create_circle_vertices(x, y, radius=0.25, n_points=8):
    """Create circle as polygon vertices."""
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    vertices = np.column_stack([
        x + radius * np.cos(angles),
        y + radius * np.sin(angles)
    ])
    return vertices

# ----------------- Load and Preprocess Data -----------------
print("Loading and preprocessing data...")
input_file = sys.argv[1]
find_M = input_file.find("_M")
output_suffix = input_file[find_M:input_file.rfind(".csv")]
data = pd.read_csv(input_file)

# Sort by time for faster access
data = data.sort_values('time').reset_index(drop=True)

# Pre-group data by time (much faster than repeated filtering)
time_groups = {}
for time_val in data['time'].unique():
    time_groups[time_val] = data[data['time'] == time_val]

print(f"Data loaded: {len(data)} rows, {len(time_groups)} time steps")

# ----------------- Setup Figure for Animation -----------------
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect("equal")

# Calculate bounds once
x_min, x_max = data["x"].min() - 5, data["x"].max() + 5
y_min, y_max = data["y"].min() - 5, data["y"].max() + 5
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)

# Use separate collections for different types (faster color updates)
bacteria_collection = PatchCollection([], facecolor='blue', edgecolor='none', linewidth=0.3)
eps_collection = PatchCollection([], facecolor='red', edgecolor='none', linewidth=0.3)

ax.add_collection(bacteria_collection)
ax.add_collection(eps_collection)

title_text = ax.text(0.5, 0.95, "", transform=ax.transAxes, ha='center', fontsize=12)

# ----------------- Optimized Animation Update Function -----------------
times = sorted(time_groups.keys())

def update(frame_idx):
    frame_time = times[frame_idx]
    tdata = time_groups[frame_time]
    
    # Separate data by type
    bacteria_data = tdata[tdata["type"] == "BacteriaCell"]
    eps_data = tdata[tdata["type"] == "EPSParticle"]
    
    # Create bacteria patches
    bacteria_patches = []
    if len(bacteria_data) > 0:
        for _, row in bacteria_data.iterrows():
            vertices = create_capsule_vertices(
                row["x"], row["y"], row["angle"], row["length"]-1, width=0.5
            )
            bacteria_patches.append(patches.Polygon(vertices))
    
    # Create EPS patches
    eps_patches = []
    if len(eps_data) > 0:
        for _, row in eps_data.iterrows():
            vertices = create_circle_vertices(row["x"], row["y"], radius=0.25)
            eps_patches.append(patches.Polygon(vertices))
    
    # Update collections
    bacteria_collection.set_paths(bacteria_patches)
    eps_collection.set_paths(eps_patches)
    
    title_text.set_text(f"Time = {frame_time}")
    
    return bacteria_collection, eps_collection, title_text

# ----------------- Create & Save Animation with Progress -----------------
print("Creating animation...")

# Reduce interval for faster playback during creation
ani = animation.FuncAnimation(
    fig, update, frames=len(times),
    repeat=False, blit=True, interval=100  # Reduced from 500
)

print("Saving animation...")
def progress(i, n):
    if i % max(1, n//20) == 0:  # Print every 5% progress
        print(f"Processed frame {i+1}/{n} ({100*i/n:.1f}%)")

# Optimized save settings
ani.save(
    f"output_video{output_suffix}.mp4",
    writer="ffmpeg",
    fps=5,  # Increased FPS
    bitrate=2400,  # Slightly higher bitrate
    dpi=80,  # Reduced DPI for speed
    progress_callback=progress,
    extra_args=['-preset', 'fast']  # Fast encoding preset
)

print("Animation saved successfully!")

# ----------------- Alternative: Memory-efficient version for large datasets -----------------
def create_memory_efficient_animation():
    """Alternative version that processes data in chunks to save memory."""
    print("\nCreating memory-efficient version...")
    
    fig2, ax2 = plt.subplots(figsize=(8, 8))
    ax2.set_aspect("equal")
    ax2.set_xlim(x_min, x_max)
    ax2.set_ylim(y_min, y_max)
    
    collection2 = PatchCollection([], edgecolor='none', linewidth=0.2)
    ax2.add_collection(collection2)
    title_text2 = ax2.text(0.5, 0.95, "", transform=ax2.transAxes, ha='center')
    
    def update_efficient(frame_idx):
        frame_time = times[frame_idx]
        # Load data on demand to save memory
        tdata = data[data["time"] == frame_time]
        
        all_patches = []
        all_colors = []
        
        # Vectorized operations where possible
        bacteria_mask = tdata["type"] == "BacteriaCell"
        eps_mask = tdata["type"] == "EPSParticle"
        
        # Process bacteria
        if bacteria_mask.any():
            bacteria_subset = tdata[bacteria_mask]
            for _, row in bacteria_subset.iterrows():
                vertices = create_capsule_vertices(
                    row["x"], row["y"], row["angle"], row["length"]-1
                )
                all_patches.append(patches.Polygon(vertices))
                all_colors.append('blue')
        
        # Process EPS
        if eps_mask.any():
            eps_subset = tdata[eps_mask]
            for _, row in eps_subset.iterrows():
                vertices = create_circle_vertices(row["x"], row["y"])
                all_patches.append(patches.Polygon(vertices))
                all_colors.append('red')
        
        collection2.set_paths(all_patches)
        collection2.set_facecolor(all_colors)
        title_text2.set_text(f"Time = {frame_time}")
        
        return collection2, title_text2
    
    ani2 = animation.FuncAnimation(
        fig2, update_efficient, frames=len(times),
        repeat=False, blit=True, interval=100
    )
    
    ani2.save(
        f"output_video{output_suffix}.mp4",
        writer="ffmpeg", 
        fps=5,
        bitrate=2400,
        dpi=80,
        progress_callback=progress,
        extra_args=['-preset', 'ultrafast']  # Fastest encoding
    )
    
    print("Memory-efficient animation saved!")

# Uncomment to run memory-efficient version
# create_memory_efficient_animation()