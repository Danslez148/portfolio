import java.util.List;
public class BacteriaCell extends Particle {
    
    private boolean isSecretingEPS = false;
    private double critLength; // Critical length for division

   public BacteriaCell(int id, Vector2D position, double length, double radius, double angle, double angularVelocity, double friction, double motility) {
        super(id, position, length, radius, angle, angularVelocity, friction, motility);
        this.critLength = 5.0; // Division threshold
    }

    public void divide() {
        // This will be called by the simulation when shouldDivide() returns true
        // The simulation will handle creating new bacteria cells
        this.length = this.length / 2.0; // Halve the parent's length
        this.angle = random.nextDouble() * 2 * Math.PI; // Random new direction
    }

    public boolean shouldDivide() {
        return length >= critLength;
    }

    // Growth calculation methods from your prototype
    public double calcArea() {
        double area = Math.PI * Math.pow(radius, 2);
        area += 2 * radius * length; 
        return area;
    }

    private double calcAvgArea() {
        double area = Math.PI * Math.pow(radius, 2) + (3.0 / 2.0) * radius * length; 
        return area;
    }

    private double monodFunction(double nutrient_density) {
        return nutrient_density / (1 + nutrient_density);
    }

    private double calcGrowthRate(double nutrientConcentration) {
        // Base growth rate (length units per time unit)
        double baseGrowthRate = 2; // Adjust this value to control growth speed
        
        // Area ratio factor
        double areaRatio = calcArea() / calcAvgArea();
        
        double nutrientFactor = monodFunction(nutrientConcentration);
        
        double growthRate = baseGrowthRate * areaRatio * nutrientFactor;
        
        return growthRate;
    }
    
   
    public void update(double deltaTime, SpatialGrid spatialGrid, NutrientField nutrientField) {
        // GROWTH LOGIC
        double growthRate = calcGrowthRate(nutrientField.getConcentration(position));
        length += growthRate * deltaTime; 
        updateEPSSecretion(spatialGrid);
        super.update(deltaTime, spatialGrid);
    }
// EPS secretion logic
    public boolean updateEPSSecretion(SpatialGrid spatialGrid) {
        //calc bac cell densisty 
        int bacCount = 1;
        int epsCount = 0;
        int particleCount = 0;
        List<Particle> particles = spatialGrid.getParticleNeighbors(this);
        for(Particle p : particles){
            if(p.getPosition().distance(position) <= 0.65){
                //within radius
                particleCount++;
                if(p instanceof BacteriaCell){
                    bacCount++;
                } else if(p instanceof EPSParticle){
                    epsCount++;
                }
            }

        }
        //calc eps density 
        double EPSDensity = (double) epsCount/particleCount;
        double bacDensity = (double) bacCount/particleCount;
        if(bacDensity >= 5.0 && !isSecretingEPS){
            //start secreting
            isSecretingEPS = true;
        }
        if(EPSDensity >= 0.3 && isSecretingEPS){
            //stop secreting
            isSecretingEPS = false;
        }
        // if(isSecretingEPS){
        //     //secrete eps
        //     EPSParticle newEPS = new EPSParticle(-1, new Vector2D(position.getX(), position.getY()), 0.5, 0.5, random.nextDouble() * 2 * Math.PI,angularVelocity, friction, motility);
        // }
        return isSecretingEPS;
    }

    public EPSParticle secreteEPS(int id){
        EPSParticle epsParticle = new EPSParticle(id, new Vector2D(position.getX(), position.getY()), 0.5, 0.5, random.nextDouble() * 2 * Math.PI, angularVelocity, friction, motility);
        return epsParticle;
    }

    
    // Getter for critical length
    public double getCritLength() {
        return critLength;
    }
    
    // Method to create a daughter cell (used by simulation)
    public BacteriaCell createDaughter(int newId) {
        // Create daughter at same position with half length
        return new BacteriaCell(newId, new Vector2D(position.getX(), position.getY()), 
                               length / 2.0, radius, 
                               random.nextDouble() * 2 * Math.PI, // Random angle
                               angularVelocity, friction, motility);
    }
}