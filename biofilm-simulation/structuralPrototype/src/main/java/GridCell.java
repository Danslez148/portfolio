import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;

/*
 * Represents a cell in a 2D grid that can contain particles.
 * Provides thread-safe operations for adding, removing, and retrieving particles.
 */
class GridCell {
    // List of particles currently in this cell
    private final List<Particle> particles;
    
    // Coordinates of this cell in the grid
    private final int x, y;
    
    // Lock object for synchronizing access to the particles list
    private final Object lock = new Object();
    
    // Constructor initializes the cell with given coordinates
    public GridCell(int x, int y) {
        this.particles = new ArrayList<>();
        this.x = x;
        this.y = y;
    }
    
    // Adds a particle to this cell in a thread-safe manner
    public void addParticle(Particle particle) {
        synchronized(lock) {
            particles.add(particle);
        }
    }
    
    // Removes a particle from this cell in a thread-safe manner
    public void removeParticle(Particle particle) {
        synchronized(lock) {
            particles.remove(particle);
        }
    }
    
    // Returns a copy of the current particles list (thread-safe snapshot)
    public List<Particle> getParticlesCopy() {
        synchronized(lock) {
            return new ArrayList<>(particles);
        }
    }
    
    // Clears all particles from this cell (thread-safe)
    public void clear() {
        synchronized(lock) {
            particles.clear();
        }
    }
    
    // Returns the number of particles in this cell (thread-safe)
    public int size() {
        synchronized(lock) {
            return particles.size();
        }
    }
    
    // Returns the X coordinate of this cell
    public int getX() { return x; }
    
    // Returns the Y coordinate of this cell
    public int getY() { return y; }
}
