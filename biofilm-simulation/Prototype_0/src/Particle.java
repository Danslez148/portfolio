public abstract class Particle {
    private int id;
    private Vector2D position;
    private Vector2D velocity;
    private Vector2D totalForce;
    private double radius;
    private double length;
    
    
     public Particle(int id, Vector2D position, double mass, double radius) {
        this.id = id;
        this.position = position;
        this.velocity = new Vector2D(0, 0);
        this.totalForce = new Vector2D(0, 0);
        this.length = mass;
        this.radius = radius;
    }
    
    // Getters AI Generated
    public int getId() { return id; }
    public Vector2D getPosition() { return position; }
    public Vector2D getVelocity() { return velocity; }
    public Vector2D getTotalForce() { return totalForce; }
    public double getLength() { return length; }
    public double getRadius() { return radius; }
    
    // Setters AI Generated
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
    
    // Abstract methods
    public abstract void update(double deltaTime);
}

