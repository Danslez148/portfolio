import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;

public class Simulation {
    private NutrientField nutrientField;
    private SpatialGrid spatialGrid;
    private SimulationConfig parameters;
    private List<BacteriaCell> bacteriaCells;
    private List<EPSParticle> epsParticles;
    private DataWriter dataWriter;
    private int numWorkerThreads;
    private List<SimulationWorker> workers;
    private double deltaTime;
    public static AtomicInteger cellIDCount = new AtomicInteger(0);
    // Array to track particle interactions to avoid collisions 
    // across borders counting the forces twice
    private ConcurrentLinkedQueue<String> particleInteractions;

    // Thread-safe queue for collecting division requests
    private ConcurrentLinkedQueue<BacteriaCell> divisionQueue;
    private ConcurrentLinkedQueue<BacteriaCell> epsSecretionQueue;

    private final int simulationSize = 400; // Size of the simulation area (assuming square for simplicity)

    public Simulation(int numWorkerThreads) {
        // Initialize collections first
        this.bacteriaCells = new ArrayList<>();
        this.epsParticles = new ArrayList<>();
        this.workers = new ArrayList<>();
        this.divisionQueue = new ConcurrentLinkedQueue<>();
        this.epsSecretionQueue = new ConcurrentLinkedQueue<>();
        this.particleInteractions = new ConcurrentLinkedQueue<>();
        
        // Create initial bacteria cell
        int initialCellID = cellIDCount.getAndIncrement();
        BacteriaCell bacteriaCell = new BacteriaCell(initialCellID, new Vector2D(0,0), 2, 2, 0, 0, 200, 500);
        this.bacteriaCells.add(bacteriaCell);

        // Initialize spatial grid and nutrient field based on simulation size
        this.spatialGrid = new SpatialGrid(simulationSize/4, 4, 4);
        this.nutrientField = new NutrientField(-1 * simulationSize * 0.5, -1 * simulationSize * 0.5);

        this.numWorkerThreads = numWorkerThreads;
        this.deltaTime = 0.1;
        this.dataWriter = new DataWriter("./structuralPrototype/bin/sim_output.csv");
        
        // Add initial bacteria to spatial grid
        spatialGrid.addParticleToCell(bacteriaCell);
        
        initializeWorkers();
    }

    private void initializeWorkers() {
        // Simple work distribution: divide grid cells among workers
        int totalCells = spatialGrid.getGridWidth() * spatialGrid.getGridHeight();
        int cellIndex = 0;

        for (int workerId = 0; workerId < numWorkerThreads; workerId++) {
            List<GridCell> assignedCells = new ArrayList<>();
            
            // Assign cells to workers
            int remainingCells = totalCells - cellIndex;
            int remainingWorkers = numWorkerThreads - workerId;
            int cellsForThisWorker = (remainingCells + remainingWorkers - 1) / remainingWorkers;

            for (int i = 0; i < cellsForThisWorker && cellIndex < totalCells; i++) {
                int x = cellIndex % spatialGrid.getGridWidth();
                int y = cellIndex / spatialGrid.getGridWidth();
                GridCell cell = spatialGrid.getGridCell(x, y);
                if (cell != null) {
                    assignedCells.add(cell);
                }
                cellIndex++;
            }

            

            SimulationWorker worker = new SimulationWorker(workerId, assignedCells, this, divisionQueue, epsSecretionQueue, particleInteractions);
            workers.add(worker);

            System.out.println("Worker " + workerId + " initialized with " + assignedCells.size() + " gridCells");
            for (GridCell cell : assignedCells) {
                System.out.println("(" + cell.getX() + ", " + cell.getY() + ") with " + cell.getParticles().size() + " particles");
            }
        }
    }

    public void runSimulation(int iterations) throws InterruptedException {
        ExecutorService executor = Executors.newFixedThreadPool(workers.size());

        double elapsedTime = 0.0;
        double printInterval = 10.0, nextPrintTime = 10.0;

        for (int step = 0; step < iterations; step++) {
            // Phase 1: Calculate forces
            CountDownLatch latchForces = new CountDownLatch(workers.size());
            for (SimulationWorker worker : workers) {
                executor.submit(() -> {
                    try {
                        worker.calculateForcesForAssignedCells();
                    } finally {
                        latchForces.countDown();
                    }
                });
            }
            latchForces.await();
            // refresh the particle interactions array
            particleInteractions.clear();

            // Phase 2: Update positions AND check for divisions
            CountDownLatch latchUpdate = new CountDownLatch(workers.size());
            for (SimulationWorker worker : workers) {
                executor.submit(() -> {
                    try {
                        worker.updatePositionsAndCheckDivisions();
                    } finally {
                        latchUpdate.countDown();
                    }
                });
            }
            latchUpdate.await();
            
            // Phase 3: Process divisions and secretions collected by workers
            List<BacteriaCell> newBacCells = processDivisions();
            List<EPSParticle> newEPS = processEPSSecretions();

            // Add new cells to the simulation
            bacteriaCells.addAll(newBacCells);
            epsParticles.addAll(newEPS);
            
            // Update worker assignments if new cells were created
            if (!newBacCells.isEmpty()) {
                redistributeWorkLoad();
            }
            
            // diffuse the nutrients in the nutrient field
            nutrientField.diffuse(deltaTime, bacteriaCells);

            // Print progress
            if (step % 100 == 0) {
                System.out.println("Step: " + step + ", Elapsed time: " + elapsedTime + 
                                 ", Bacteria count: " + bacteriaCells.size()+ ", EPS count: " + epsParticles.size());
            }

            if (elapsedTime >= nextPrintTime) {
                List<Particle> allParticles = new ArrayList<>();
                allParticles.addAll(bacteriaCells);
                allParticles.addAll(epsParticles);

                dataWriter.WriteParticlesToFile(elapsedTime, allParticles);

                nextPrintTime += printInterval;
            }

            elapsedTime += deltaTime;
            
            // Safety check to prevent runaway growth
            if (bacteriaCells.size() > 10000|| epsParticles.size() > 100000) {
                System.out.println("Maximum particle limit reached, ending simulation");
                break;
            }
        }

        dataWriter.close();
        executor.shutdown();
    }
    
    /**
     * Process all division requests collected by workers
     * This runs on the main thread to avoid race conditions
     */
    private List<BacteriaCell> processDivisions() {
        List<BacteriaCell> newCells = new ArrayList<>();
        
        // Use AtomicInteger for thread-safe ID assignment
        BacteriaCell cellToDivide;
        while ((cellToDivide = divisionQueue.poll()) != null) {
            // Create daughter cell with atomic ID
            BacteriaCell daughter = cellToDivide.createDaughter(cellIDCount.getAndIncrement());
            newCells.add(daughter);
            
            // Parent cell divides (reduces its size)
            cellToDivide.divide();
            
            // Add daughter to spatial grid
            spatialGrid.addParticleToCell(daughter);
        }
        
        return newCells;
    }
// come back to this depending on if ethan chnages the divisions to the workers class
    private List<EPSParticle> processEPSSecretions() {
        List<EPSParticle> newEPS = new ArrayList<>();
        BacteriaCell cellToSecrete;

        while ((cellToSecrete = epsSecretionQueue.poll()) != null) {
            // Create new EPS particle
            EPSParticle epsParticle = cellToSecrete.secreteEPS(cellIDCount.getAndIncrement());
            newEPS.add(epsParticle);
        }

        return newEPS;
    }
    
    /**
     * Redistribute workload among workers after new cells are added
     */
    private void redistributeWorkLoad() {
        for (SimulationWorker worker : workers) {
            worker.refreshAssignedParticles();
        }
    }

    // Getters
    public double getDeltaTime() {
        return deltaTime;
    }
    
    public SpatialGrid getSpatialGrid() {
        return spatialGrid;
    }

    public NutrientField getNutrientField() {
        return nutrientField;
    }

    public static void main(String[] args) {
        try {
            System.out.println("Creating simulation...");
            Simulation sim = new Simulation(10);
            System.out.println("Running simulation...");
            sim.runSimulation(10000);
        } catch (InterruptedException e) {
            System.err.println("Simulation interrupted: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("Simulation error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}