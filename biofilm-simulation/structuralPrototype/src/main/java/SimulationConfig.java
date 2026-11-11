

import java.util.*;

class SimulationConfig {
    // Core simulation parameters
    private int numSimulationWorkers;
    private double motility = 0.0;
    private double BacteriaToBacteriaElasticModulus = 4e5;
    private double EPSToEPSElasticModulus = 4e5;
    private double BacteriaToEPSElasticModulus = 5e5;
    private double deltaTime;
    private int simulationTime = 100000;
    
    // Spatial domain and grid
    private double simulationSize = 400.0;
    private double gridCellSize = 6.0;

    // Initial conditions
    private int initialBacteriaCount = 1;
    private double initialBacteriaLengthMin = 3.0;
    private double initialBacteriaLengthMax = 3.5;

    // EPS / cell growth parameters
    private double KEPS ;                 // example default, adjust as needed
    private double cellAreaThreshold = 5.0;    // example default
    private double EPSAreaLimit = 0.3;         // example default
    private double EPSParticleThreshold = 1.0; // example default
    private double radiusCheck = -1;
    private double bacteriaFriction=200;
    private double EPSFriction=200;
    private double bacteriaRadius=0.5;
    // Output
    private double printInterval = 1;
    private int maxParticles;

    // Constructors
    

    public SimulationConfig() {
        this.numSimulationWorkers = 14;
        this.motility = 1100;
        this.printInterval=1;
        this.deltaTime = 0.025;
        this.maxParticles= 25000;
        this.simulationTime = 1000000;
        this.KEPS=deltaTime*1;
    }

    // Getters
    public int getNumSimulationWorkers() { return numSimulationWorkers; }
    public double getMotility() { return motility; }
    public double getBacteriaBacteriaElastic() { return BacteriaToBacteriaElasticModulus; }
    public double getEPSToEPSElasticModulus() { return EPSToEPSElasticModulus; }
    public double getBacteriaToEPSElasticModulus(){return BacteriaToEPSElasticModulus;}
    public double getDeltaTime() { return deltaTime; }
    public int getSimulationTime() { return simulationTime; }
    public double getRadiusCheck() { return radiusCheck;}
    public double getSimulationSize() { return simulationSize; }
    public double getGridCellSize() { return gridCellSize; }
    public double getBacteriaFriction() { return bacteriaFriction; }
    public double getEPSFriction() { return EPSFriction;}
    public double getBacteriaRadius() {return bacteriaRadius;}
    public int getInitialBacteriaCount() { return initialBacteriaCount; }
    public double getInitialBacteriaLengthMin() { return initialBacteriaLengthMin; }
    public double getInitialBacteriaLengthMax() { return initialBacteriaLengthMax; }

    public double getKEPS() { return KEPS; }
    public double getCellAreaThreshold() { return cellAreaThreshold; }
    public double getEPSAreaLimit() { return EPSAreaLimit; }
    public double getEPSParticleThreshold() { return EPSParticleThreshold; }

    public double getPrintInterval() { return printInterval; }
    public int getMaxParticles() { return maxParticles; }

    public void setMotility(double motility) { this.motility = motility; }
    public void setBacteriaToBacteriaElasticModulus(double modulus) { this.BacteriaToBacteriaElasticModulus = modulus; }
    public void setBacteriaToEPSElasticModulus(double modulus) { this.BacteriaToEPSElasticModulus = modulus; }
     public void setEPSToEPSElasticModulus(double modulus) { this.EPSToEPSElasticModulus = modulus; }
    public void setMaxParticles(int maxParticles) { this.maxParticles = maxParticles; }
    public void setSimulationTime(int simulationTime) { this.simulationTime = simulationTime; }
}
