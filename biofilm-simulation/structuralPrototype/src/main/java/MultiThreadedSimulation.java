
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;


// Multi-threaded simulation with work-stealing
public class MultiThreadedSimulation {
    private List<BacteriaCell> bacteria;
    private List<EPSParticle> epsParticles;
    private List<Particle> allParticles;
    private SpatialGrid spatialGrid;
    private NutrientField nutrientField;
    private SimulationConfig config;
    private DataWriter dataWriter;
    private ExecutorService executor;
    
    // Simulation parameters
    private final double SIMULATION_SIZE;
    private final double GRID_CELL_SIZE;
    private final AtomicInteger nextParticleId = new AtomicInteger(0);
    private final int numThreads;
     
    private Random random = new Random(42);
    public MultiThreadedSimulation(SimulationConfig config) {
        this.config = config;
        this.SIMULATION_SIZE = config.getSimulationSize();
        this.GRID_CELL_SIZE = config.getGridCellSize();
        this.numThreads = config.getNumSimulationWorkers();
        this.bacteria = Collections.synchronizedList(new ArrayList<>());
        this.epsParticles = Collections.synchronizedList(new ArrayList<>());
        this.allParticles = Collections.synchronizedList(new ArrayList<>());
        
        // Initialize spatial grid
        double halfSize = SIMULATION_SIZE / 2.0;
        this.spatialGrid = new SpatialGrid(-halfSize, -halfSize, halfSize, halfSize, GRID_CELL_SIZE);
        
        // Initialize nutrient field
        this.nutrientField = new NutrientField(-halfSize, -halfSize);
        
        // Initialize thread pool
        this.executor = Executors.newFixedThreadPool(numThreads);
        
        // Initialize data writer
        // Initialize data writer
        String filename = String.format(
            "./StructuralPrototype/Output/multithreaded_biofilm_M%.1f_%.1f-%.1f-%.1f.csv", 
            config.getMotility(),                  // %.1f
            config.getBacteriaBacteriaElastic()/1e5,    // %.1f
            config.getEPSToEPSElasticModulus()/1e5,     // %.1f
            config.getBacteriaToEPSElasticModulus()/1e5
        );
        this.dataWriter = new DataWriter(filename);

        
        // Create initial bacteria population
        initializeBacteria();
    }
    
    private void initializeBacteria() {
        
        int initialCount = config.getInitialBacteriaCount();
        
        //System.out.println("Initializing " + initialCount + " bacteria...");
        
        for (int i = 0; i < initialCount; i++) {
            double x = (random.nextDouble() - 0.5) * 20;
            double y = (random.nextDouble() - 0.5) * 20;
            Vector2D position = new Vector2D(x, y);
            
            double angle = random.nextDouble() * 2 * Math.PI;
            
            // Start with larger bacteria that are closer to division
            double startingLength = 3.0 + random.nextDouble() * 0.5; // 3.0-3.5 instead of 2.5
            
            BacteriaCell bacterium = new BacteriaCell(
                nextParticleId.getAndIncrement(),
                position, startingLength, config.getBacteriaRadius(), angle, 0.0, config.getBacteriaFriction(), config.getMotility()
            , config.getKEPS(), config.getCellAreaThreshold(), config.getEPSAreaLimit(),config.getEPSParticleThreshold(), config.getRadiusCheck(), config.getEPSFriction());
            
            
            bacteria.add(bacterium);
            allParticles.add(bacterium);
        }
        
        spatialGrid.updateGrid(allParticles);
        //System.out.println("Bacteria initialization complete.");
    }
    
    public void runSimulation(java.util.function.Supplier<Boolean> shouldStop) throws InterruptedException {
        double deltaTime = config.getDeltaTime();
        double elapsedTime = 0.0;
        double printInterval = config.getPrintInterval();
        double nextPrintTime = printInterval;
        int totalTimeSteps = config.getSimulationTime();
        
        System.out.println("Starting multi-threaded simulation with " + bacteria.size() + " bacteria");
        System.out.println("Using " + numThreads + " threads");
        System.out.println("Grid size: " + spatialGrid.getGridWidth() + "x" + spatialGrid.getGridHeight());
        
        dataWriter.WriteParticlesToFile(elapsedTime, new ArrayList<>(allParticles));
        
        for (int step = 0; step < totalTimeSteps && !shouldStop.get(); step++) {
            if (Thread.interrupted()) {
                throw new InterruptedException("Simulation was interrupted");
            }
            
            // Update spatial grid (single-threaded for simplicity)
            spatialGrid.updateGrid(new ArrayList<>(allParticles));
            
            // Phase 1: Calculate forces in parallel using work-stealing
            calculateForcesParallel();
            
            // Phase 2: Update particles in parallel
             updateParticlesParallel(deltaTime);
            spatialGrid.updateGrid(new ArrayList<>(allParticles));
            List<ParticleEvent> events = CheckForEventsParallel(deltaTime);
            // Phase 4: Process events (single-threaded for consistency)
            processEvents(events);
            
            // Update nutrient field
            nutrientField.diffuse(deltaTime, new ArrayList<>(bacteria));
            
            elapsedTime += deltaTime;
            
            // Write data at intervals
            if (elapsedTime >= nextPrintTime) {
                dataWriter.WriteParticlesToFile(elapsedTime, new ArrayList<>(allParticles));
                nextPrintTime += printInterval;
            }
            
            // Print progress
            if (step % 100 == 0) {
                System.out.println("Step " + step + "/" + totalTimeSteps + 
                                 " - Time: " + String.format("%.1f", elapsedTime) + 
                                 " - Bacteria: " + bacteria.size() + 
                                 ", EPS: " + epsParticles.size() +
                                 " - Total particles: " + allParticles.size());
            }
            
            // Safety check
            if (allParticles.size() > config.getMaxParticles()) {
                System.out.println("Maximum particle limit reached, ending simulation");
                break;
            }
        }
        
        // Write final state and cleanup
        dataWriter.WriteParticlesToFile(elapsedTime, new ArrayList<>(allParticles));
        dataWriter.close();
        executor.shutdown();
        
        System.out.println("Simulation completed!");
        System.out.println("Final counts - Bacteria: " + bacteria.size() + ", EPS: " + epsParticles.size());
    }
    
    private void calculateForcesParallel() throws InterruptedException {
        List<GridCell> nonEmptyCells = spatialGrid.getNonEmptyCells();
        if (nonEmptyCells.isEmpty()) return;
        
        // Distribute work among threads
        int cellsPerTask = Math.max(1, nonEmptyCells.size() / numThreads);
        List<Future<Void>> futures = new ArrayList<>();
        
        for (int i = 0; i < nonEmptyCells.size(); i += cellsPerTask) {
            int endIndex = Math.min(i + cellsPerTask, nonEmptyCells.size());
            List<GridCell> taskCells = nonEmptyCells.subList(i, endIndex);
            
            ForceCalculationTask task = new ForceCalculationTask(taskCells, spatialGrid, config);
            futures.add(executor.submit(task));
        }
        
        // Wait for all tasks to complete
        for (Future<Void> future : futures) {
            try {
                future.get();
            } catch (ExecutionException e) {
                throw new RuntimeException("Force calculation failed", e);
            }
        }
    }
    
    private List<ParticleEvent> updateParticlesParallel(double deltaTime) throws InterruptedException {
        List<Particle> particlesCopy = new ArrayList<>(allParticles);
        if (particlesCopy.isEmpty()) return new ArrayList<>();
        
        // Distribute particles among threads
        int particlesPerTask = Math.max(1, particlesCopy.size() / numThreads);
        List<Future<List<ParticleEvent>>> futures = new ArrayList<>();
        
        for (int i = 0; i < particlesCopy.size(); i += particlesPerTask) {
            int endIndex = Math.min(i + particlesPerTask, particlesCopy.size());
            List<Particle> taskParticles = particlesCopy.subList(i, endIndex);
            
            ParticleUpdateTask task = new ParticleUpdateTask(taskParticles, deltaTime, nutrientField, spatialGrid);
            futures.add(executor.submit(task));
        }
        
        // Collect all events
        List<ParticleEvent> allEvents = new ArrayList<>();
        for (Future<List<ParticleEvent>> future : futures) {
            try {
                allEvents.addAll(future.get());
            } catch (ExecutionException e) {
                throw new RuntimeException("Particle update failed", e);
            }
        }
        
        return allEvents;
    }
    private List<ParticleEvent> CheckForEventsParallel(double deltaTime) throws InterruptedException {
        List<Particle> particlesCopy = new ArrayList<>(allParticles);
        if (particlesCopy.isEmpty()) return new ArrayList<>();
        
        // Distribute particles among threads
        int particlesPerTask = Math.max(1, particlesCopy.size() / numThreads);
        List<Future<List<ParticleEvent>>> futures = new ArrayList<>();
        
        for (int i = 0; i < particlesCopy.size(); i += particlesPerTask) {
            int endIndex = Math.min(i + particlesPerTask, particlesCopy.size());
            List<Particle> taskParticles = particlesCopy.subList(i, endIndex);
            
            EventCheckTask task = new EventCheckTask(taskParticles, deltaTime, nutrientField, spatialGrid);
            futures.add(executor.submit(task));
        }
        
        // Collect all events
        List<ParticleEvent> allEvents = new ArrayList<>();
        for (Future<List<ParticleEvent>> future : futures) {
            try {
                allEvents.addAll(future.get());
            } catch (ExecutionException e) {
                throw new RuntimeException("Particle update failed", e);
            }
        }
        
        return allEvents;
    }
    


    private void processEvents(List<ParticleEvent> events) {
        for (ParticleEvent event : events) {
            switch (event.getType()) {
                case DIVISION:
                    BacteriaCell parent = event.getBacterium();
                    BacteriaCell daughter = parent.createDaughter(nextParticleId.getAndIncrement());
                    parent.divide();
                    bacteria.add(daughter);
                    allParticles.add(daughter);
                    break;
                    
                case EPS_SECRETION:
                    BacteriaCell secretor = event.getBacterium();
                    EPSParticle eps = secretor.secreteEPS(nextParticleId.getAndIncrement());
                    epsParticles.add(eps);
                    allParticles.add(eps);
                    break;
            }
        }
    }
    
    
    



    public static void main(String[] args) {
        try {
            SimulationConfig config = new SimulationConfig();
            
            MultiThreadedSimulation sim = new MultiThreadedSimulation(config);
            
            long startTime = System.currentTimeMillis();
            sim.runSimulation(() -> false);
            long endTime = System.currentTimeMillis();
            
            System.out.println("Total simulation time: " + (endTime - startTime) + " ms");
            
        } catch (Exception e) {
            System.err.println("Simulation error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}