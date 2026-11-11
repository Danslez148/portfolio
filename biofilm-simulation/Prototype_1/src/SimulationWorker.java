import java.util.List;
import java.util.ArrayList;
import java.util.Queue;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.CountDownLatch;

public class SimulationWorker {
    private int workerId;
    private List<GridCell> assignedCells;
    private List<Particle> assignedParticles; 
    private ForceCalculator forceCalculator;
    private double deltaTime;
    private Simulation parentSimulation;
    private SpatialGrid spatialGrid;
    
    public SimulationWorker(int workerId, List<GridCell> assignedCells, Simulation parentSimulation) {
        this.workerId = workerId;
        this.parentSimulation = parentSimulation;
        this.assignedCells = new ArrayList<>(assignedCells);
        this.assignedParticles = new ArrayList<>();
        this.forceCalculator = new ForceCalculator();
        this.deltaTime = 1;
        initializeAssignedParticles();
        this.spatialGrid = parentSimulation.getSpatialGrid();
    }
    
    // Getters
    public int getWorkerId() { return workerId; }
    public List<GridCell> getAssignedCells() { return assignedCells; }
    public List<Particle> getAssignedParticles() { return assignedParticles; }
   
    // Initialization
    public void initializeAssignedParticles() {
        assignedParticles.clear();
        for (GridCell cell : assignedCells) {
            assignedParticles.addAll(cell.getParticles());
        }
    }
    
    
    // Core processing methods
    public void calculateForcesForAssignedCells() {
        // TODO: Calculate forces for all assigned particles
    }
    
    public void updatePositionsForAssignedCells() {
        
        for (GridCell cell : assignedCells) {
            List<Particle> cellParticles = cell.getParticlesSafeCopy();
            
            for (Particle particle : cellParticles) {
                if (!assignedParticles.contains(particle)) continue;
                
                Vector2D oldPosition = particle.getPosition();
                GridCell oldCell = spatialGrid.getGridCell(oldPosition);
                
               
                
                Vector2D newPosition = particle.getPosition();
                GridCell newCell = spatialGrid.getGridCell(newPosition);
                
                // Check for migration
                if (oldCell != newCell) {
                    spatialGrid.moveParticleToDiffCell(particle, oldCell, newCell);
                }
            }
        }
    }
 
    
    
    public void processAssignedCells(double deltaTime) {
        this.deltaTime = deltaTime;
        // TODO: Process all assigned cells for one simulation step
    }
    