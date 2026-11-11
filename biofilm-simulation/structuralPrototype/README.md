# How the Biofilm Simulation Program Works

## Program Overview

This is a multi-threaded biofilm simulation that models bacterial growth, division, and EPS (Extracellular Polymeric Substance) production in a 2D environment. The program simulates individual bacteria as rod-shaped particles that grow, divide, interact mechanically, consume nutrients, and secrete EPS under certain conditions.

## Data Flow and Main Execution Loop

### 1. Initialization Phase

```
MultiThreadedSimulation.main()
├── Create SimulationConfig (default parameters)
├── Initialize MultiThreadedSimulation
│   ├── Create thread pool (ExecutorService)
│   ├── Initialize SpatialGrid (for efficient neighbor finding)
│   ├── Initialize NutrientField (diffusion grid)
│   ├── Create initial bacteria population
│   └── Set up DataWriter for CSV output
└── Call runSimulation()
```

### 2. Main Simulation Loop

Each time step follows this sequence:

```
For each time step (0 to totalTimeSteps):
├── 1. Update Spatial Grid (Single-threaded)
│   ├── Clear all grid cells
│   ├── For each particle in allParticles:
│   │   ├── Calculate grid coordinates from particle position
│   │   └── Add particle to appropriate grid cell
│   └── Grid now contains current particle spatial distribution
│
├── 2. Calculate Forces (Multi-threaded)
│   ├── Get list of non-empty grid cells
│   ├── Divide cells among available threads:
│   │   ├── Thread 1: assigned cells 0 to N/numThreads
│   │   ├── Thread 2: assigned cells N/numThreads to 2N/numThreads
│   │   └── Thread k: assigned cells to end of list
│   ├── Each worker thread:
│   │   ├── For each assigned grid cell:
│   │   │   ├── Get all particles in this cell
│   │   │   ├── Get all particles in 8 neighboring cells
│   │   │   ├── For each particle pair (cell + neighbors):
│   │   │   │   ├── Check if particles are close enough to interact
│   │   │   │   ├── Calculate repulsive force using capsule model
│   │   │   │   └── Add force to particle's totalForce vector
│   │   │   └── Continue to next cell
│   │   └── Thread completes its assigned cells
│   └── Main thread waits for all force calculation threads to finish
│
├── 3. Update Particles (Multi-threaded)
│   ├── Create copy of allParticles list (thread-safe)
│   ├── Divide particles among available threads:
│   │   ├── Thread 1: particles 0 to M/numThreads
│   │   ├── Thread 2: particles M/numThreads to 2M/numThreads
│   │   └── Thread k: particles to end of list
│   ├── Each worker thread:
│   │   ├── For each assigned particle:
│   │   │   ├── Call particle.update(deltaTime, nutrientField)
│   │   │   │   ├── Add motility force (bacteria only)
│   │   │   │   ├── Add random Brownian force
│   │   │   │   ├── Calculate velocity from total forces
│   │   │   │   ├── Update position using velocity
│   │   │   │   ├── Handle boundary collisions
│   │   │   │   ├── Update growth (bacteria: consume nutrients)
│   │   │   │   ├── Update rotation from torque
│   │   │   │   └── Clear forces for next step
│   │   │   ├── If particle is BacteriaCell:
│   │   │   │   ├── Check if length >= critLength (division ready)
│   │   │   │   └── Check EPS secretion conditions
│   │   │   └── Add any generated events to thread-local event list
│   │   └── Return thread's event list to main thread
│   └── Main thread collects all events from all worker threads
│
├── 4. Process Events (Single-threaded)
│   ├── For each ParticleEvent in collected events:
│   │   ├── If event type is DIVISION:
│   │   │   ├── Get parent BacteriaCell from event
│   │   │   ├── Call parent.createDaughter(newID) → creates daughter cell
│   │   │   ├── Call parent.divide() → moves parent, halves length
│   │   │   ├── Add daughter to bacteria list
│   │   │   └── Add daughter to allParticles list
│   │   └── If event type is EPS_SECRETION:
│   │       ├── Get secreting BacteriaCell from event
│   │       ├── Call bacterium.secreteEPS(newID) → creates EPS particle
│   │       ├── Add EPS particle to epsParticles list
│   │       └── Add EPS particle to allParticles list
│   └── Update nextParticleId counter for new particles
│
├── 5. Update Nutrient Field (Single-threaded)
│   ├── For each nutrient grid cell (x,y):
│   │   ├── Calculate diffusion term:
│   │   │   └── Laplacian = sum of 4 neighboring concentrations - 4*current
│   │   ├── Calculate consumption term:
│   │   │   ├── For each bacterium in this grid location:
│   │   │   └── consumption += uptakeRate * monodFunction(localConc) * bacteriaArea
│   │   ├── Update concentration:
│   │   │   └── newConc = oldConc + (diffusion - consumption) * deltaTime
│   │   └── Enforce boundary conditions (edges = initial concentration)
│   └── Replace old concentration array with new values
│
└── 6. Write Data (Single-threaded, if at output interval)
    ├── Check if elapsedTime >= nextPrintTime
    ├── If yes:
    │   ├── For each particle in allParticles:
    │   │   └── Write CSV line: time,id,x,y,angle,length,type
    │   └── Update nextPrintTime += printInterval
    └── Continue simulation loop
```

## How Multithreading Works

### Thread Pool Architecture

- Uses `ExecutorService` with fixed thread pool (default: number of CPU cores)
- Two main parallel phases per time step:
    1. **Force Calculation Phase**
    2. **Particle Update Phase**

### Force Calculation Parallelization

```java
// Divide non-empty grid cells among threads
List<GridCell> nonEmptyCells = spatialGrid.getNonEmptyCells();
int cellsPerTask = nonEmptyCells.size() / numThreads;

// Each thread gets a subset of grid cells
for (each subset of cells) {
    ForceCalculationTask task = new ForceCalculationTask(cellSubset, spatialGrid);
    Future<Void> future = executor.submit(task);
    // Task calculates repulsive forces for all particles in its assigned cells
}
```

### Particle Update Parallelization

```java
// Divide particles among threads
List<Particle> allParticles = getAllParticles();
int particlesPerTask = allParticles.size() / numThreads;

// Each thread updates a subset of particles
for (each subset of particles) {
    ParticleUpdateTask task = new ParticleUpdateTask(particleSubset, deltaTime, ...);
    Future<List<ParticleEvent>> future = executor.submit(task);
    // Task updates positions, checks for division/EPS secretion
}
```

### Thread Safety Mechanisms

- **Synchronized Collections**: `Collections.synchronizedList()` for particle lists
- **Grid Cell Locking**: Each `GridCell` has internal synchronization
- **Event Collection**: Threads collect events independently, merged in single thread
- **Atomic ID Generation**: `AtomicInteger` for unique particle IDs

## Detailed Calculations

### 1. Bacterial Growth and Division

**Growth Calculation:**

```java
// In BacteriaCell.update()
double nutrientConcentration = nutrientField.getConcentration(position);
double areaRatio = calcArea() / calcAvgArea();
double growthFactor = monodFunction(nutrientConcentration);
length += growthRate * deltaTime * areaRatio * growthFactor;

// Monod function for nutrient limitation
private double monodFunction(double nutrientDensity) {
    return nutrientDensity / (1 + nutrientDensity);
}
```

**Division Process:**

```java
// When length >= critLength (5.0)
public void divide() {
    // Calculate offset to separate parent and daughter
    double offsetX = Math.cos(angle) * (length / 2.0 + 0.5);
    double offsetY = Math.sin(angle) * (length / 2.0 + 0.5);
    
    // Move parent backward
    position = new Vector2D(position.getX() - offsetX, position.getY() - offsetY);
    
    // Halve parent length
    this.length = this.length / 2;
}

// Create daughter at forward position
public BacteriaCell createDaughter(int newId) {
    Vector2D daughterPos = new Vector2D(
        position.getX() + Math.cos(angle) * length/2,
        position.getY() + Math.sin(angle) * length/2
    );
    // Return new BacteriaCell at daughter position
}
```

### 2. EPS Secretion Logic

**Density-Based Secretion:**

```java
public boolean updateEPSSecretion(SpatialGrid spatialGrid) {
    double radiusCheck = 0.75;  // Check neighborhood radius
    double totalCellArea = 0;
    double totalEPSArea = 0;
    
    // Sum areas of all particles within radiusCheck
    for (Particle p : nearbyParticles) {
        if (distance <= radiusCheck) {
            if (p instanceof BacteriaCell) {
                totalCellArea += ((BacteriaCell)p).calcArea();
            } else if (p instanceof EPSParticle) {
                totalEPSArea += ((EPSParticle)p).calcArea();
            }
        }
    }
    
    // Calculate local densities
    double checkArea = Math.PI * radiusCheck * radiusCheck;
    double localCellAreaDensity = totalCellArea / checkArea;
    double localEPSAreaDensity = totalEPSArea / checkArea;
    
    // Start secreting if cell density high but EPS density not too high
    if (localCellAreaDensity >= CELL_AREA_THRESHOLD && 
        localEPSAreaDensity < EPS_AREA_LIMIT) {
        isSecretingEPS = true;
    }
    
    // Accumulate EPS production
    if (isSecretingEPS) {
        epsAccumulation += kEPS;
        if (epsAccumulation >= EPS_PARTICLE_THRESHOLD) {
            return true;  // Time to create EPS particle
        }
    }
    return false;
}
```

### 3. Force Calculations

**Repulsive Force Model:** The program uses a capsule-capsule interaction model for rod-shaped bacteria:

```java
private void applyRepulsion(Particle p1, Particle p2) {
    // Get endpoints of rod-shaped particles
    Vector2D[] ends1 = particleEndpoints(p1);  // Returns [headPos, tailPos]
    Vector2D[] ends2 = particleEndpoints(p2);
    
    // Find closest points between the two line segments
    ClosestPoints cp = segmentClosestPoints(ends1[0], ends1[1], ends2[0], ends2[1]);
    
    // Calculate overlap (negative = no contact)
    double overlap = Math.max(p1.getRadius() + p2.getRadius() - cp.distance, 0);
    
    if (overlap > 0) {
        // Hertzian contact force: F = E * sqrt(R) * overlap^1.5
        double elasticModulus = getElasticModulus(p1, p2);
        double forceMagnitude = elasticModulus * Math.sqrt(1) * Math.pow(overlap, 1.5);
        
        // Apply force along contact direction
        Vector2D contactDirection = cp.pointOnSeg2.subtract(cp.pointOnSeg1);
        Vector2D force = contactDirection.normalize().multiply(-forceMagnitude);
        
        // Apply force and torque to particle
        p1.addForceAtPoint(force, cp.pointOnSeg1);
    }
}
```

### 4. Movement and Physics

**Overdamped Dynamics:**

```java
// In BacteriaCell.update()
// 1. Add motility force (self-propulsion)
addForce(new Vector2D(Math.cos(angle), Math.sin(angle)).multiply(motility));
addForce(getRandomForce());  // Brownian motion

// 2. Calculate velocity from total force (overdamped: no inertia)
velocity = totalForce.multiply(1.0 / (friction * (length + radius*2)));

// 3. Update position
position = position.add(velocity.multiply(deltaTime));

// 4. Rotational dynamics
angularVelocity = (12.0 / (friction * Math.pow(length + radius*2, 3))) * torque;
angle += angularVelocity * deltaTime;
```

### 5. Nutrient Field Dynamics

**Diffusion-Reaction Equation:**

```java
public void diffuse(double deltaTime, List<BacteriaCell> bacteria) {
    for (int x = 1; x < concGridWidth - 1; x++) {
        for (int y = 1; y < concGridHeight - 1; y++) {
            // Laplacian for diffusion
            double laplacian = concentration[x+1][y] + concentration[x-1][y] +
                              concentration[x][y+1] + concentration[x][y-1] -
                              4 * concentration[x][y];
            
            double diffusionTerm = diffusionRate * laplacian / (concGridCellSize^2);
            
            // Consumption by bacteria at this location
            double consumptionTerm = 0.0;
            for (BacteriaCell cell : bacteria) {
                if (cell is in this grid cell) {
                    double uptake = consumptionRate * monodFunction(localConc) * cell.calcArea();
                    consumptionTerm += uptake;
                }
            }
            
            // Update concentration
            newConcentration[x][y] = concentration[x][y] + 
                                   (diffusionTerm - consumptionTerm) * deltaTime;
        }
    }
}
```

## Spatial Grid System

**Purpose**: Efficiently find nearby particles for force calculations without checking all particle pairs.

**How it works:**

1. Divide simulation domain into grid cells (5x5 unit squares)
2. Each particle is assigned to the cell containing its position
3. To find neighbors of a particle, only check its cell + 8 adjacent cells
4. Reduces complexity from O(N²) to O(N) for neighbor finding

```java
// Grid cell assignment
int gridX = (int) Math.floor((position.getX() - minX) / cellSize);
int gridY = (int) Math.floor((position.getY() - minY) / cellSize);

// Neighbor search (only 9 cells maximum)
for (int dx = -1; dx <= 1; dx++) {
    for (int dy = -1; dy <= 1; dy++) {
        // Check cell at (currentX + dx, currentY + dy)
    }
}
```

## Data Output

**CSV Format:**

```
time,id,x,y,angle,length,type
0.000000,0,-1.250000,0.500000,1.234567,3.250000,BacteriaCell
0.000000,1,2.100000,-0.750000,0.987654,0.250000,EPSParticle
1.000000,0,-1.100000,0.600000,1.345678,3.350000,BacteriaCell
...
```

Each row represents one particle at one time point, allowing reconstruction of the entire simulation timeline for analysis.

## Performance Optimizations

1. **Spatial Grid**: O(N) neighbor finding instead of O(N²)
2. **Multithreading**: Parallel force calculation and particle updates
3. **Synchronized Collections**: Thread-safe without global locks
4. **Work Stealing**: Dynamic load balancing among threads
5. **Memory Management**: Reuse of Vector2D objects where possible
6. **Early Termination**: Stop simulation at particle limit to prevent memory issues

The multithreaded approach can achieve significant speedups on multi-core systems, with the main limitation being the single-threaded event processing phase and grid updates.