
import java.util.List;
import java.util.Random;

public class BacteriaCell extends Particle {
    

    private Random random;
    private double angularVelocity;
    private double motility;
    private double critLength = 5.0;  
    private double growthRate = 3.5;  
    private double age = 0.0;          

    private boolean isSecretingEPS = false;
    private final double kEPS;  
    private final double CELL_AREA_THRESHOLD;  
    private final double EPS_AREA_LIMIT ;  
    private double epsAccumulation ;  
    private final double EPS_PARTICLE_THRESHOLD ;  
    private double radiusCheck;
    double EPSFriction;
    public BacteriaCell(int id, Vector2D position, double length, double radius, 
                        double angle, double angularVelocity, double friction, double motility, double kEPS, double CELL_AREA_THRESHOLD,
                        double EPS_AREA_LIMIT, double EPS_PARTICLE_THRESHOLD, double radiusCheck,double EPSFriction) {
        this.id = id;
        this.position = position;
        this.length = length;
        this.radius = radius;
        this.angle = angle;
        this.angularVelocity = angularVelocity;
        this.friction = friction;
        this.motility = motility;
        this.velocity = new Vector2D(0,0);
        this.totalForce = new Vector2D(0,0);
        this.kEPS = kEPS;
        this.CELL_AREA_THRESHOLD = CELL_AREA_THRESHOLD;
        this.EPS_AREA_LIMIT = EPS_AREA_LIMIT;
        this.EPS_PARTICLE_THRESHOLD = EPS_PARTICLE_THRESHOLD;
        this.radiusCheck= radiusCheck;
        this.EPSFriction=EPSFriction;
        this.random= new Random(37+id);
    }

    /*
     * update method to move particle according to the forces applied to it.
     */
    @Override
    public void update(double deltaTime, NutrientField nutrientField) {
        age += deltaTime;

        // 1. Motility force
        addForce(new Vector2D(Math.cos(angle), Math.sin(angle)).multiply(motility));
        addForce(getRandomForce());

        // 2. Overdamped dynamics and changing position
        velocity = totalForce.multiply(1.0 / ((friction/deltaTime) * (length + radius*2)));
        Vector2D displacement = velocity.multiply(deltaTime);
       
        position = position.add(displacement);

        // 3. Boundary handling
        double halfSize = 200;
        if(position.getX() < -halfSize) { position.setX(-halfSize); velocity.setX(-velocity.getX()); }
        if(position.getX() > halfSize)  { position.setX(halfSize);  velocity.setX(-velocity.getX()); }
        if(position.getY() < -halfSize) { position.setY(-halfSize); velocity.setY(-velocity.getY()); }
        if(position.getY() > halfSize)  { position.setY(halfSize);  velocity.setY(-velocity.getY()); }

        // 4. Growth
        double nutrientConcentration = nutrientField.getConcentration(position);
        double areaRatio = calcArea() / calcAvgArea();
        double growthFactor = monodFunction(nutrientConcentration);
        length += growthRate * deltaTime * areaRatio * growthFactor;

        // 5. Rotation

        angle += (random.nextDouble() - 0.5) * 2 * Math.toRadians(5);
        angularVelocity = (12.0 / ((friction/deltaTime) * Math.pow(length + radius*2,3))) * torque;
        angle += angularVelocity * deltaTime;
        angle = (angle % (2*Math.PI) + 2*Math.PI) % (2*Math.PI);
        

        // 6. Clear forces for next step
        clearForces();
        torque = 0;
    }

    public boolean shouldDivide() {
        return length >= critLength;
    }
    /*
     * halve the bacterias length and move its position back by a quarter length relative to its angle.
     */
    public void divide() {
        double halfLength = length / 2.0;
        Vector2D daughterPos = new Vector2D(
            position.getX() - Math.cos(angle) * halfLength/2,
            position.getY() - Math.sin(angle) * halfLength/2
        );

        double angleNoise = (random.nextDouble() - 0.5) * Math.toRadians(2);
        this.position= daughterPos;
        this.angle=angle+angleNoise;
        this.length=this.length/2;
    }


    /* 
     * Creates a daughter in front of the parent cell setting this daughters lenght to half the parents size
     * and setting its angle to a reasonable variation from its parent.
    */
    public BacteriaCell createDaughter(int newId) {
        double halfLength = length / 2.0;
        Vector2D daughterPos = new Vector2D(
            position.getX() + Math.cos(angle) * halfLength/2,
            position.getY() + Math.sin(angle) * halfLength/2
        );

        double angleNoise = (random.nextDouble() - 0.5) * Math.toRadians(20);
        BacteriaCell daughter = new BacteriaCell(newId, daughterPos, halfLength, radius, 
                                                 angle + angleNoise, 0, friction, motility, kEPS, CELL_AREA_THRESHOLD, EPS_AREA_LIMIT, EPS_PARTICLE_THRESHOLD, radiusCheck, EPSFriction);
        return daughter;
    }

    /*
     * When called checks if the bacterias local density meets the requirements to produce eps or stop producing
     * if it produces then we add keps*deltatime to the accumulated eps
     * if it is stop producing then we clear the accumulated eps
     * if the accumulated eps = threshold then return true and reset accumulated to 0.
     */
    public boolean updateEPSSecretion(SpatialGrid spatialGrid) { 

        if (radiusCheck==-1) radiusCheck=length/2;
    
        double totalCellArea = 0;
        double totalEPSArea = 0.0;

        GridCell currentCell = spatialGrid.getGridCell(position);
        List<Particle> nearbyParticles = spatialGrid.getNeighbors(currentCell);
        nearbyParticles.addAll(currentCell.getParticlesCopy());

        // Calculate densities in the neighborhood
        for (Particle p : nearbyParticles) {
            double distance = position.distance(p.getPosition());
            if (distance <= radiusCheck) {
                if (p instanceof BacteriaCell) {
                    totalCellArea += ((BacteriaCell)p).calcArea();
                } else if (p instanceof EPSParticle) {
                    totalEPSArea += ((EPSParticle)p).calcArea();
                }
            }
        }

        double checkArea = Math.PI * radiusCheck * radiusCheck;
        double localCellAreaDensity = totalCellArea; ///checkArea;
        double localEPSAreaDensity = totalEPSArea;/// checkArea;

        // Start EPS secretion if conditions are met
        if (localCellAreaDensity >= CELL_AREA_THRESHOLD && localEPSAreaDensity < EPS_AREA_LIMIT) {
            isSecretingEPS = true;
        }  
        if (localEPSAreaDensity >= EPS_AREA_LIMIT) {
            isSecretingEPS = false;
            epsAccumulation = 0; // reset if blocked by EPS crowding
        }

        // If secreting, accumulate EPS
        if (isSecretingEPS) {
            epsAccumulation += kEPS;
            if (epsAccumulation >= EPS_PARTICLE_THRESHOLD) {
                epsAccumulation = 0;
                return true; // time to release an EPS particle
            }
        }

        return false;
    }

    /*
     * produces an eps of half bacterias radius in radius.
     * only produce on the sides of bacteria
     */
    public EPSParticle secreteEPS(int id) {
        double epsRadius = radius / 2;
        double minDistance = radius * 2 + epsRadius;
        double maxDistance = length / 2;

        // Make sure the max is actually greater than the min
        if (maxDistance <= minDistance) {
            throw new IllegalArgumentException("length/2 must be greater than radius*2 + epsRadius");
        }

        double offsetAngle;
        while (true) {
            offsetAngle = random.nextDouble() * 2 * Math.PI;
            double deg = Math.toDegrees(offsetAngle);

            // Normalize angle to [0, 360)
            if (deg < 0) deg += 360;

            // Allow only LEFT/RIGHT: exclude -30→30 (front) and 150→210 (back)
            if (!((deg >= 330 || deg <= 30) || (deg >= 150 && deg <= 210))) {
                break; // valid angle found
            }
        }

        // Pick random distance between min and max
        double offsetDistance = minDistance + random.nextDouble() * (maxDistance - minDistance);

        Vector2D epsPosition = new Vector2D(
            position.getX() + offsetDistance * Math.cos(offsetAngle),
            position.getY() + offsetDistance * Math.sin(offsetAngle)
        );

        return new EPSParticle(id, epsPosition, epsRadius, EPSFriction);
    }



    /*
     * calculates area of bacteria
     */
    public double calcArea() {
        return Math.PI*radius*radius + 2.0*radius*length;
    }
    /*
     * calculates average area of bacteria. formula given in bara et al.
     */
    public double calcAvgArea() {
        return Math.PI*radius*radius + 1.5*radius*length;
    }
    // monod function
    private double monodFunction(double nutrientDensity) {
        return nutrientDensity / (1 + nutrientDensity);
    }
    // returns random force of magnitude between -10^-3 to 10^-3
    private Vector2D getRandomForce() {
        double magnitude = (random.nextDouble()-0.5)*2e-3;
        double angle = random.nextDouble() * 2 * Math.PI;
        return new Vector2D(magnitude*Math.cos(angle), magnitude*Math.sin(angle));
    }

    public double getAge() { return age; }
}
