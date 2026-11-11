import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class SimulationWorker {
    private int workerId;
    private List<GridCell> assignedCells;
    private List<Particle> assignedParticles; 
    private ForceCalculator forceCalculator;
    private double deltaTime;
    private SpatialGrid spatialGrid;
    private NutrientField nutrientField;
    private ConcurrentLinkedQueue<BacteriaCell> divisionQueue;
    private ConcurrentLinkedQueue<BacteriaCell> epsSecretionQueue;
    private ConcurrentLinkedQueue<String> particleInteractions;
    
    public SimulationWorker(int workerId, List<GridCell> assignedCells, 
                           Simulation parentSimulation, ConcurrentLinkedQueue<BacteriaCell> divisionQueue, ConcurrentLinkedQueue<BacteriaCell> epsSecretionQueue, ConcurrentLinkedQueue<String> particleInteractions) {
        this.workerId = workerId;
        this.assignedCells = new ArrayList<>(assignedCells);
        this.assignedParticles = new ArrayList<>();
        this.forceCalculator = new ForceCalculator();
        this.deltaTime = parentSimulation.getDeltaTime();
        this.spatialGrid = parentSimulation.getSpatialGrid();
        this.nutrientField = parentSimulation.getNutrientField();
        this.epsSecretionQueue = epsSecretionQueue;
        this.particleInteractions = particleInteractions;
        this.divisionQueue = divisionQueue;
        
        initializeAssignedParticles();
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
    
    // Method to refresh particle assignments (called after cell divisions)
    public void refreshAssignedParticles() {
        initializeAssignedParticles();
    }
    
    // Core processing methods
    public void calculateForcesForAssignedCells() {
        // Refresh assigned particles list
        initializeAssignedParticles();
        
        if (!assignedParticles.isEmpty()) {
            forceCalculator.calculateRepulsiveForces(assignedParticles, spatialGrid, particleInteractions, 20000.0, 20000.0);
        }
    }

    public void updatePositionsAndCheckDivisions() {
        // Refresh assigned particles list
        initializeAssignedParticles();
        
        for (Particle particle : assignedParticles) {
            Vector2D oldPosition = new Vector2D(particle.getPosition().getX(), particle.getPosition().getY());
            GridCell oldCell = spatialGrid.getGridCell(oldPosition);
            
            // Update particle position
            if(particle instanceof BacteriaCell){
                BacteriaCell bac = (BacteriaCell) particle;
                bac.update(deltaTime, spatialGrid, nutrientField);
           
            }else{
                     particle.update(deltaTime, spatialGrid);
            }
            
            
            Vector2D newPosition = particle.getPosition();
            GridCell newCell = spatialGrid.getGridCell(newPosition);
            
            // Check for migration between cells
            if (oldCell != newCell && oldCell != null && newCell != null) {
                spatialGrid.moveParticleToDiffCell(particle, oldCell, newCell);
            }
            
            // Check for cell division (only for BacteriaCell instances)
            if (particle instanceof BacteriaCell) {
                BacteriaCell bacteriaCell = (BacteriaCell) particle;
                if (bacteriaCell.shouldDivide()) {
                    // Add to division queue for processing by main thread
                    divisionQueue.offer(bacteriaCell);
                }
            // Check for EPS secretion (only for BacteriaCell instances)
                if (bacteriaCell.updateEPSSecretion(spatialGrid)) {
                    // Add to EPS secretion queue for processing by main thread
             //       System.out.println("EPS secretion queued by worker " + workerId + " for BacteriaCell ID: " + bacteriaCell.getId());
                    epsSecretionQueue.offer(bacteriaCell);
                }
            }
     
    }
    }
    
    /**
     * Legacy method - kept for backwards compatibility if needed
     * But now we use updatePositionsAndCheckDivisions() instead
     */
    @Deprecated
    public void updatePositionsForAssignedCells() {
        updatePositionsAndCheckDivisions();
    }
}