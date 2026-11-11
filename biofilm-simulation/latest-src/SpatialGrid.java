import java.util.ArrayList;
import java.util.List;

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
    public List<Particle> getParticleNeighbors(Particle particle) {
        return getParticleNeighborsThreadSafe(particle);
    }
    
    // Sarah's attempt at neghbour particle finding = using a radius to limit 
    // the number of particles it adds from each cell - radius used is the radius 
    //suggested for cluster calculations in the paper.
    public List<Particle> getParticleNeighborsThreadSafe(Particle particle) {
        List<Particle> neighbors = new ArrayList<>();
        double radius = 0.65; // Example radius to consider neighbors
        Vector2D pos = particle.getPosition();
        GridCell currentCell = getGridCell(pos);
        // above cell
        if (currentCell.getY()-1 >= 0){
            GridCell aboveCell = getGridCell(currentCell.getX(), currentCell.getY()-1);
            synchronized (aboveCell) {
                for (Particle neighbor : aboveCell.getParticles()) {
                    if (neighbor != particle) {
                        double distance = pos.distance(neighbor.getPosition());
                        if (distance <= radius) {
                            neighbors.add(neighbor);
                        }
                    }
                }
            }
        }
        // below cell
        if (currentCell.getY()+1 < gridHeight){
            GridCell belowCell = getGridCell(currentCell.getX(), currentCell.getY()+1);
            synchronized (belowCell) {
                for (Particle neighbor : belowCell.getParticles()) {
                    if (neighbor != particle) {
                        double distance = pos.distance(neighbor.getPosition());
                        if (distance <= radius) {
                            neighbors.add(neighbor);
                        }
                    }
                }
            }
        }
        // left cell
        if (currentCell.getX()-1 >= 0){
            GridCell leftCell = getGridCell(currentCell.getX()-1, currentCell.getY());
            synchronized (leftCell) {
                for (Particle neighbor : leftCell.getParticles()) {
                    if (neighbor != particle) {
                        double distance = pos.distance(neighbor.getPosition());
                        if (distance <= radius) {
                            neighbors.add(neighbor);
                        }
                    }
                }
            }
        }
        // right cell
        if (currentCell.getX()+1 < gridWidth){
            GridCell rightCell = getGridCell(currentCell.getX()+1, currentCell.getY());
            synchronized (rightCell) {
                for (Particle neighbor : rightCell.getParticles()) {
                    if (neighbor != particle) {
                        double distance = pos.distance(neighbor.getPosition());
                        if (distance <= radius) {
                            neighbors.add(neighbor);
                        }
                    }
                }
            }
        }
        List<Particle> currentCellParticles = currentCell.getParticlesSafeCopy();
        for (Particle p : currentCellParticles) {
            if (p != particle && p.getPosition().distance(particle.getPosition()) <= radius){
                neighbors.add(p);
            }
        }

        return neighbors;
        // int cellRadius = (int) Math.ceil(radius / cellSize);

        
        // int centerX = currentCell.getX();
        // int centerY = currentCell.getY();
        
        // // Check all cells within radius
        // for (int dx = -cellRadius; dx <= cellRadius; dx++) {
        //     for (int dy = -cellRadius; dy <= cellRadius; dy++) {
        //         GridCell neighborCell = getGridCell(centerX + dx, centerY + dy);
        //         if (neighborCell != null) {
        //             synchronized (neighborCell) {
        //                 for (Particle neighbor : neighborCell.getParticles()) {
        //                     if (neighbor != particle) {
        //                         double distance = pos.distance(neighbor.getPosition());
        //                         if (distance <= radius) {
        //                             neighbors.add(neighbor);
        //                         }
        //                     }
        //                 }
        //             }
        //         }
        //     }
        // }
        

    }
    


    // Worker assignment methods
    public void assignWorkToThreads(List<SimulationWorker> workers) {
        
    }
    
    public List<GridCell> getAdjacentCells(GridCell cell) {
        List<GridCell> adjacent = new ArrayList<>();
        
        return adjacent;
    }
}
