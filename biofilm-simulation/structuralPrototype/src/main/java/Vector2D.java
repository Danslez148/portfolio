
/**
 * Simple 2D vector class for representing positions, velocities, or directions in 2D space.
 * Provides common vector operations such as addition, subtraction, scaling, dot/cross products, 
 * magnitude calculation, normalization, and distance computation.
 */
class Vector2D {
    // X and Y components of the vector
    public double x, y;
    
    /**
     * Constructor to create a vector with specified components.
     * @param x X component
     * @param y Y component
     */
    public Vector2D(double x, double y) {
        this.x = x;
        this.y = y;
    }
    
    /**
     * Adds this vector to another vector.
     * @param other the vector to add
     * @return new Vector2D representing the sum
     */
    public Vector2D add(Vector2D other) {
        return new Vector2D(x + other.x, y + other.y);
    }
    
    /**
     * Subtracts another vector from this vector.
     * @param other the vector to subtract
     * @return new Vector2D representing the difference
     */
    public Vector2D subtract(Vector2D other) {
        return new Vector2D(x - other.x, y - other.y);
    }
    
    /**
     * Multiplies this vector by a scalar.
     * @param scalar the scaling factor
     * @return new Vector2D representing the scaled vector
     */
    public Vector2D multiply(double scalar) {
        return new Vector2D(x * scalar, y * scalar);
    }
    
    /**
     * Computes the dot product of this vector with another vector.
     * @param other the other vector
     * @return the dot product (scalar)
     */
    public double dot(Vector2D other) {
        return this.x * other.x + this.y * other.y;
    }
    
    /**
     * Computes the magnitude (length) of this vector.
     * @return magnitude
     */
    public double magnitude() {
        return Math.sqrt(x * x + y * y);
    }
    
    /**
     * Returns a normalized (unit length) version of this vector.
     * If the vector has zero length, returns a zero vector.
     * @return normalized vector
     */
    public Vector2D normalize() {
        double mag = magnitude();
        if (mag == 0) return new Vector2D(0, 0);
        return new Vector2D(x / mag, y / mag);
    }
    
    /**
     * Computes the Euclidean distance between this vector and another vector.
     * @param other the other vector
     * @return distance
     */
    public double distance(Vector2D other) {
        double dx = this.x - other.x;
        double dy = this.y - other.y;
        return Math.sqrt(dx * dx + dy * dy);
    }
    
    // Getter and setter methods for X and Y components
    public double getX() { return x; }
    public double getY() { return y; }
    public void setX(double x) { this.x = x; }
    public void setY(double y) { this.y = y; }
    
    /**
     * Computes the 2D cross product (determinant) of this vector and another vector.
     * In 2D, this gives a scalar representing the magnitude of the perpendicular vector in 3D.
     * @param v the other vector
     * @return scalar cross product
     */
    public double cross(Vector2D v) {
        return this.x * v.y - this.y * v.x;
    }
}
