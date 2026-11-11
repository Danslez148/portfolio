
import java.util.*;
import java.util.concurrent.*;
// task to do force calculations
class ForceCalculationTask implements Callable<Void> {
    private final List<GridCell> cells;
    private final SpatialGrid spatialGrid;
    private final ForceCalculator forceCalculator;
    
    
    public ForceCalculationTask(List<GridCell> cells, SpatialGrid spatialGrid, SimulationConfig config) {
        this.cells = cells;
        this.spatialGrid = spatialGrid;
        this.forceCalculator = new ForceCalculator(config);
    }
    // method to calculate forces of particles in a list of cells
    @Override
    public Void call() {
        for (GridCell cell : cells) {
            List<Particle> cellParticles = cell.getParticlesCopy();
            if (cellParticles.isEmpty()) continue;
            
            List<Particle> neighbors = spatialGrid.getNeighbors(cell);
            neighbors.addAll(cellParticles); // Include particles in same cell
            
            forceCalculator.calculateRepulsiveForces(cellParticles, neighbors);
        }
        return null;
    }
}
