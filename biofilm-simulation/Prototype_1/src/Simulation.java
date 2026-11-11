import java.util.List;

public class Simulation {
    private NutrientField nutrientField;
    private SpatialGrid spatialGrid;
    private SimulationConfig parameters;
    private List<BacteriaCell> bacteriaCells;
    private List<EPSParticle> epsParticles;
    private DataWriter dataWriter;
    private int numWorkerThreads;
    private List<SimulationWorker> workerThreads;

    public void run() {
        // insert functionality
    }

    public void update(double deltaTime) {
        // insert functionality
    }

    public double calculateSimulationTime() {
        // insert functionality
        return 0.0;
    }
}
