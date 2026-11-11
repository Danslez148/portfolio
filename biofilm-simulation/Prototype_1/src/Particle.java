/* nothing must be private only protected or public in this class */


public abstract class Particle {
    protected int id;
    protected Vector2D position;
    protected Vector2D velocity;
    protected Vector2D totalForce;
    protected double radius;
    protected double length;

    public abstract void update(double deltaTime);
    public void setTotalForce(Vector2D totalForce) {

    }

    public Vector2D getPosition() {
        // insert functionality
        return null;
    }

    public void setPosition(Vector2D position) {
        // insert functionality
    }

    public double getRadius() {
        // insert functionality
        return 0.0;
    }

    public void setRadius(double radius) {
        // insert functionality
    }
}
