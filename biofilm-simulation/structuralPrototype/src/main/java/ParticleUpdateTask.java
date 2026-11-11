
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.io.*;
// class to update particles.
class ParticleUpdateTask implements Callable<List<ParticleEvent>> {
    private final List<Particle> particles;
    private final double deltaTime;
    private final NutrientField nutrientField;
    private final SpatialGrid spatialGrid;
    
    public ParticleUpdateTask(List<Particle> particles, double deltaTime, 
                             NutrientField nutrientField, SpatialGrid spatialGrid) {
        this.particles = particles;
        this.deltaTime = deltaTime;
        this.nutrientField = nutrientField;
        this.spatialGrid = spatialGrid;
    }
    
    @Override
    public List<ParticleEvent> call() {
        List<ParticleEvent> events = new ArrayList<>();
        
        for (Particle particle : particles) {
            particle.update(deltaTime, nutrientField);
            
        }
        
        return events;
    }
}
