import java.util.Random;

public abstract class Particle {
    protected int id;
    protected Vector2D position;
    protected Vector2D velocity;
    protected Vector2D totalForce;
    protected double radius;
    protected double length;
    protected double angle;
    protected double friction;
    protected double motility;
    protected double angularVelocity;
    protected static Random random;

    public Particle(int id, Vector2D position, double length, double radius, double angle, double angularVelocity, double friction, double motility) {
        this.id = id;
        this.position = position;
        this.velocity = new Vector2D(0, 0);
        this.totalForce = new Vector2D(0, 0);
        this.length = length;
        this.radius = radius;
        this.angle= angle;
        this.friction = friction;
        this.motility = motility;
        this.angularVelocity = angularVelocity;
        this.random = new Random(73);
    }
    
    // Getters 
    public int getId() { return id; }
    public double getX() { return getPosition().getX();}
    public double getY() { return getPosition().getY();}
    public Vector2D getPosition() { return position; }
    public Vector2D getVelocity() { return velocity; }
    public Vector2D getTotalForce() { return totalForce; }
    public double getLength() { return length; }
    public double getRadius() { return radius; }
    public double getAngle() { return angle; }
    
    // Setters
    public void setPosition(Vector2D position) { this.position = position; }
    public void setVelocity(Vector2D velocity) { this.velocity = velocity; }
    public void setTotalForce(Vector2D force) { this.totalForce = force; }
    
    // Force management
    public void addForce(Vector2D force) {
        this.totalForce = this.totalForce.add(force);
    }
    
    public void clearForces() {
        this.totalForce = new Vector2D(0, 0);
    }

    private Vector2D getRandomForce() {
        double magnitude = (random.nextDouble()-0.5)*2*1000.0; 
        double randomAngle = random.nextDouble() * 2 * Math.PI;
        return new Vector2D(
            magnitude * Math.cos(randomAngle),
            magnitude * Math.sin(randomAngle)
        );
    }
    
    // Abstract methods
    public void update(double deltaTime, SpatialGrid spatialGrid) {
         // 1. Apply motility-driven force (randomized + orientation-based)
        Vector2D motilityForce = new Vector2D(Math.cos(angle), Math.sin(angle)).multiply(motility);
        addForce(motilityForce);

        // 2. Add some random noise
        Vector2D noiseForce = getRandomForce();
        addForce(noiseForce);

        // 3. Over-damped dynamics: velocity = Force / (friction * effective length)
        Vector2D velocity = totalForce.multiply(1.0 / (friction * (length + radius * 2)));

        // 4. Update position
        position = position.add(velocity.multiply(deltaTime));

        // 5. Boundary conditions (simple clamping and bounce)
        double halfSize = 200; // simulationSize / 2
        double minX = -halfSize, maxX = halfSize;
        double minY = -halfSize, maxY = halfSize;

        // Clamp and bounce X
        if (position.getX() < minX) {
            position.setX(minX);
            velocity.setX(-velocity.getX());
        } else if (position.getX() > maxX) {
            position.setX(maxX);
            velocity.setX(-velocity.getX());
        }
        // Clamp and bounce Y
        if (position.getY() < minY) {
            position.setY(minY);
            velocity.setY(-velocity.getY());
        } else if (position.getY() > maxY) {
            position.setY(maxY);
            velocity.setY(-velocity.getY());
        }


        // 6. Add random torque for rotation
        double torque = (random.nextDouble() - 0.5) * 200;

        // 7. Angular velocity from torque
        angularVelocity = (12.0 / (friction * Math.pow((length + radius * 2), 3))) * torque;

        // 8. Update angle
        angle += angularVelocity * deltaTime;

        // 9. Normalize angle to [0, 2π]
        angle = (angle % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);

        // 10. Reset total force
        clearForces();
    };
}

