import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;

/**
 * Thread-safe spatial grid structure for organizing particles in 2D space.
 * 
 * - Divides a given rectangular region into cells of fixed size.
 * - Allows efficient particle insertion and neighbor lookup.
 * - Useful for spatial partitioning in simulations, collision detection, or parallel work distribution.
 */
class SpatialGrid {
    private GridCell[][] grid;   // 2D array of grid cells
    private int gridWidth;       // number of cells along X-axis
    private int gridHeight;      // number of cells along Y-axis
    private double cellSize;     // size of each cell
    
    // Bounds of the simulation space
    private double minX, minY, maxX, maxY;
    
    /**
     * Constructs a spatial grid covering the region [minX, maxX] x [minY, maxY].
     * @param minX lower X bound
     * @param minY lower Y bound
     * @param maxX upper X bound
     * @param maxY upper Y bound
     * @param cellSize size of each cell
     */
    public SpatialGrid(double minX, double minY, double maxX, double maxY, double cellSize) {
        this.minX = minX;
        this.minY = minY;
        this.maxX = maxX;
        this.maxY = maxY;
        this.cellSize = cellSize;
        
        // Compute grid dimensions
        this.gridWidth = (int) Math.ceil((maxX - minX) / cellSize);
        this.gridHeight = (int) Math.ceil((maxY - minY) / cellSize);
        
        this.grid = new GridCell[gridWidth][gridHeight];
        
        // Initialize all cells with their coordinates
        for (int i = 0; i < gridWidth; i++) {
            for (int j = 0; j < gridHeight; j++) {
                grid[i][j] = new GridCell(i, j);
            }
        }
    }
    
    /**
     * Converts a continuous 2D position into discrete grid coordinates.
     * Ensures the coordinates remain within grid bounds.
     */
    private int[] getGridCoords(Vector2D position) {
        int gridX = (int) Math.floor((position.getX() - minX) / cellSize);
        int gridY = (int) Math.floor((position.getY() - minY) / cellSize);
        
        // Clamp values so they stay within grid
        gridX = Math.max(0, Math.min(gridWidth - 1, gridX));
        gridY = Math.max(0, Math.min(gridHeight - 1, gridY));
        
        return new int[]{gridX, gridY};
    }
    
    /**
     * Returns the grid cell containing the given position.
     */
    public GridCell getGridCell(Vector2D position) {
        int[] coords = getGridCoords(position);
        return grid[coords[0]][coords[1]];
    }
    
    /**
     * Returns the grid cell at the specified coordinates, or null if out of bounds.
     */
    public GridCell getGridCell(int x, int y) {
        if (x >= 0 && x < gridWidth && y >= 0 && y < gridHeight) {
            return grid[x][y];
        }
        return null;
    }
    
    /**
     * Adds a particle to the correct grid cell based on its position.
     */
    public void addParticle(Particle particle) {
        int[] coords = getGridCoords(particle.getPosition());
        grid[coords[0]][coords[1]].addParticle(particle);
    }
    
    /**
     * Retrieves all neighboring particles around the given cell.
     * Includes up to 8 adjacent cells (Moore neighborhood).
     */
    public List<Particle> getNeighbors(GridCell currentCell) {
        List<Particle> neighbors = new ArrayList<>();
        
        int currentX = currentCell.getX();
        int currentY = currentCell.getY();
        
        // Iterate over 3x3 region around the current cell
        for (int dx = -1; dx <= 1; dx++) {
            for (int dy = -1; dy <= 1; dy++) {
                if (dx == 0 && dy == 0) continue; // Skip the current cell
                
                int nx = currentX + dx;
                int ny = currentY + dy;
                
                // Ensure neighbor is inside grid
                if (nx >= 0 && nx < gridWidth && ny >= 0 && ny < gridHeight) {
                    neighbors.addAll(grid[nx][ny].getParticlesCopy());
                }
            }
        }
        
        return neighbors;
    }
    
    /**
     * Clears all cells (removes all particles).
     */
    public void clear() {
        for (int i = 0; i < gridWidth; i++) {
            for (int j = 0; j < gridHeight; j++) {
                grid[i][j].clear();
            }
        }
    }
    
    /**
     * Updates the grid with a new list of particles.
     * First clears the grid, then reassigns particles to cells.
     */
    public void updateGrid(List<Particle> particles) {
        clear();
        for (Particle particle : particles) {
            addParticle(particle);
        }
    }
    
    /**
     * Retrieves all non-empty cells.
     * Useful for dividing work across threads (e.g., parallel processing).
     */
    public List<GridCell> getNonEmptyCells() {
        List<GridCell> nonEmptyCells = new ArrayList<>();
        for (int i = 0; i < gridWidth; i++) {
            for (int j = 0; j < gridHeight; j++) {
                if (grid[i][j].size() > 0) {
                    nonEmptyCells.add(grid[i][j]);
                }
            }
        }
        return nonEmptyCells;
    }
    
    // Getters for grid dimensions
    public int getGridWidth() { return gridWidth; }
    public int getGridHeight() { return gridHeight; }
}
