import java.util.List;
import java.util.ArrayList;

public class SpatialGrid {
    private GridCell[][] grid;
    private double cellSize;
    private int gridWidth;
    private int gridHeight;
    private final Object migrationLock = new Object();
    
    public SpatialGrid(double cellSize, int gridWidth, int gridHeight) {
        this.cellSize = cellSize;
        this.gridWidth = gridWidth;
        this.gridHeight = gridHeight;
        initializeGrid();
    }
    
    // AI Generated
    private void initializeGrid() {
        grid = new GridCell[gridWidth][gridHeight];
        for (int x = 0; x < gridWidth; x++) {
            for (int y = 0; y < gridHeight; y++) {
                grid[x][y] = new GridCell(x, y);
            }
        }
    }
    
    // Getters
    public double getCellSize() { return cellSize; }
    public int getGridWidth() { return gridWidth; }
    public int getGridHeight() { return gridHeight; }
    
    // Grid operations 

    // Get gridcell of given possition. i.e. find which cell a particle is in.
    public GridCell getGridCell(Vector2D position) {
        int x = Math.max(0, Math.min((int)(position.getX() / cellSize), gridWidth - 1));
        int y = Math.max(0, Math.min((int)(position.getY() / cellSize), gridHeight - 1));
        return grid[x][y];
    }
    
    public GridCell getGridCell(int x, int y) {
        if (x >= 0 && x < gridWidth && y >= 0 && y < gridHeight) {
            return grid[x][y];
        }
        return null;
    }
    
    // Particle management 

    public void addParticleToCell(Particle particle) {
        GridCell cell = getGridCell(particle.getPosition());
        cell.addParticle(particle);
    }
    
    public void removeParticleFromCell(Particle particle) {
        GridCell cell = getGridCell(particle.getPosition());
        cell.removeParticle(particle);
    }
    
    public void updateParticleCell(Particle particle, Vector2D oldPosition) {
        GridCell oldCell = getGridCell(oldPosition);
        GridCell newCell = getGridCell(particle.getPosition());
        
        if (oldCell != newCell) {
            moveParticleToDiffCell(particle, oldCell, newCell);
        }
    }
    
    // This is to move one cell to another. We need to synchronize it on a lock to prevent two threads altering the cells list at the same time. corrupting it.
    public void moveParticleToDiffCell(Particle particle, GridCell fromCell, GridCell toCell) {
        synchronized(migrationLock) {
            fromCell.removeParticle(particle);
            toCell.addParticle(particle);
        }
    }
    
    // Neighbor finding AI Generated
    public List<Particle> getNeighbors(Particle particle) {
        return getNeighborsThreadSafe(particle, cellSize);
    }
    
    // AI Generated
    public List<Particle> getNeighborsThreadSafe(Particle particle, double radius) {
        List<Particle> neighbors = new ArrayList<>();
        Vector2D pos = particle.getPosition();
        
        int cellRadius = (int) Math.ceil(radius / cellSize);
        GridCell currentCell = getGridCell(pos);
        
        int centerX = currentCell.getX();
        int centerY = currentCell.getY();
        
        // Check all cells within radius
        for (int dx = -cellRadius; dx <= cellRadius; dx++) {
            for (int dy = -cellRadius; dy <= cellRadius; dy++) {
                GridCell neighborCell = getGridCell(centerX + dx, centerY + dy);
                if (neighborCell != null) {
                    synchronized (neighborCell) {
                        for (Particle neighbor : neighborCell.getParticles()) {
                            if (neighbor != particle) {
                                double distance = pos.distance(neighbor.getPosition());
                                if (distance <= radius) {
                                    neighbors.add(neighbor);
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return neighbors;
    }
    


    // Worker assignment methods
    public void assignWorkToThreads(List<SimulationWorker> workers) {
        
    }
    
    public List<GridCell> getAdjacentCells(GridCell cell) {
        List<GridCell> adjacent = new ArrayList<>();
        
        return adjacent;
    }
}
