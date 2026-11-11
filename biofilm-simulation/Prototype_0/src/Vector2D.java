// Simple 2D Vector class
class Vector2D {
    public double x, y;
    
    public Vector2D(double x, double y) {
        this.x = x;
        this.y = y;
    }
    
    // Core methods
    // Handles vector vector addition
    public Vector2D add(Vector2D other) {
        return new Vector2D(x + other.x, y + other.y);
    }
    // Handles vector scalar multiplication
    public Vector2D multiply(double scalar) {
        return new Vector2D(x * scalar, y * scalar);
    }
    // Handles Dot products
    public double dot(Vector2D other) {
        return this.x * other.x + this.y * other.y;
    }
    // Handles Magnitude calculation
    public double magnitude() {
        return Math.sqrt(x * x + y * y);
    }
    // Handles normilization
    public Vector2D normalize() {
        double mag = magnitude();
        if (mag == 0) return new Vector2D(0, 0);
        return new Vector2D(x / mag, y / mag);
    }

    // To string method
    @Override
    public String toString() {
        return String.format("(%.2f, %.2f)", x, y);
    }

    // Additional methods
    // Finds distance between two vectors
    public double distance(Vector2D other) {
    double dx = this.x - other.x;
    double dy = this.y - other.y;
    return Math.sqrt(dx * dx + dy * dy);
    }
    // Rotates vector
    public Vector2D rotate(double angle) {
    double cos = Math.cos(angle);
    double sin = Math.sin(angle);
    return new Vector2D(x * cos - y * sin, x * sin + y * cos);
    }
    
    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

}
