import struct
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class CellVideoGenerator:
    def __init__(self, data_file, output_gif='cell_movement.gif'):
        self.data_file = data_file
        self.output_gif = output_gif
        self.data = []
        

    def read_data(self):
        with open(self.data_file, 'rb') as f:
            while True:
                data_bytes = f.read(52)
                if len(data_bytes) < 52:
                    break
                time, cell_id, x, y, angle, speed, length = struct.unpack('>diddddd', data_bytes)
                self.data.append({
                    'time': time, 'id': cell_id, 'x': x, 'y': y, 'angle': angle, 'speed': speed, 'length': length
                })

        print(f"Read {len(self.data)} data points")


    def create_gif(self, fps=60, figsize=(10, 10)):
        if not self.data:
            print("No data to visualize!")
            return

        
        time_points = sorted(set(record['time'] for record in self.data))
        
        # Calculate bounds
        all_x = [record['x'] for record in self.data]
        all_y = [record['y'] for record in self.data]
        x_min, x_max = min(all_x), max(all_x)
        y_min, y_max = min(all_y), max(all_y)
        xy_min, xy_max = min(x_min , y_min), max(x_max, y_max)
        

        fig, axis = plt.subplots(figsize=figsize)
        axis.set_xlim(xy_min, xy_max)
        axis.set_ylim(xy_min, xy_max)
        axis.set_aspect('equal')
        axis.grid(True, alpha=0.3)
        
        def animate(frame):
            axis.clear()
            axis.set_xlim(xy_min, xy_max)
            axis.set_ylim(xy_min, xy_max)
            axis.set_aspect('equal')
            axis.grid(True, alpha=0.3)
            
            current_time = time_points[frame]
            
            # Filter data for current time point
            current_cells = [record for record in self.data if record['time'] == current_time]

            for cell_data in current_cells:
                axis.text(cell_data['x'], cell_data['y'], str("•"), 
                        ha='center', va='center', fontsize=4, fontweight='bold')

            axis.set_title(f'Time: {current_time:.2f}')

        anim = animation.FuncAnimation(fig, animate, frames=len(time_points), interval= 1000//fps)
        anim.save(self.output_gif, writer='pillow', fps=fps)
        print(f"GIF saved successfully: {self.output_gif}")
        return anim

    

generator = CellVideoGenerator(r".\bin\test1.bin", r".\bin\cell_movement.gif")
generator.read_data()
generator.create_gif()
