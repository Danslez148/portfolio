
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;
// Abstract Particle class
abstract class Particle {
    protected int id;
    protected Vector2D position;
    protected Vector2D velocity;
    protected Vector2D totalForce;
    protected double radius;
    protected double length;
    protected double angle;
    protected double friction;
    protected double torque;
    
    // Getters
    public int getId() { return id; }
    public double getX() { return getPosition().getX(); }
    public double getY() { return getPosition().getY(); }
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
    
    public void addForceAtPoint(Vector2D force, Vector2D contactPoint) {
        Vector2D r = contactPoint.subtract(this.position);
        this.torque += r.cross(force);
        this.totalForce = this.totalForce.add(force);
    }
    
    // Abstract methods
    public abstract void update(double deltaTime, NutrientField nutrientField);
}
