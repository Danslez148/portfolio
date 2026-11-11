import java.util.List;
import java.util.ArrayList;


public class GridCell {
    private List<Particle> particles;
    private int x, y;
    private final Object cellLock = new Object();  // Restricts access so only one thread can access certain things at once.
    
    public GridCell(int x, int y) {
        this.x = x;
        this.y = y;
        this.particles = new ArrayList<>();
    }
    
    // Getters AI generated
    public int getX() { return x; }
    public int getY() { return y; }
    public String getCoordinates() { return "(" + x + "," + y + ")"; }
    


    // Particle management



    public void addParticle(Particle particle) {
        synchronized (cellLock) {
            particles.add(particle);
        }
    }
    
    public void removeParticle(Particle particle) {
        synchronized (cellLock) {
            particles.remove(particle);
        }
    }
    
    public List<Particle> getParticles() {
        return particles;
    }
    
    // AI Generated
    public List<Particle> getParticlesSafeCopy() {
        synchronized (cellLock) {
            return new ArrayList<>(particles);
        }
    }
    
    // AI Generated
    public int getParticleCount() {
        synchronized (cellLock) {
            return particles.size();
        }
    }
    
    public List<GridCell> getNeighboringCells() {
        
        return new ArrayList<>();
    }
}