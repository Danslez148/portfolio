
import java.util.*;
import java.util.concurrent.*;

// task to check if events should occur on a particle.
class EventCheckTask implements Callable<List<ParticleEvent>> {
    private final List<Particle> particles;
    private final double deltaTime;
    private final NutrientField nutrientField;
    private final SpatialGrid spatialGrid;
    
    public EventCheckTask(List<Particle> particles, double deltaTime, 
                             NutrientField nutrientField, SpatialGrid spatialGrid) {
        this.particles = particles;
        this.deltaTime = deltaTime;
        this.nutrientField = nutrientField;
        this.spatialGrid = spatialGrid;
    }
    
    /*
     * check if a particle should divide or produce eps
     */
    @Override
    public List<ParticleEvent> call() {
        List<ParticleEvent> events = new ArrayList<>();
        
        for (Particle particle : particles) {

            
            // Check for division and EPS secretion
            if (particle instanceof BacteriaCell) {
                BacteriaCell bacterium = (BacteriaCell) particle;
                
                if (bacterium.shouldDivide()) {
                    events.add(new ParticleEvent(ParticleEvent.Type.DIVISION, bacterium));
                }
                
                if (bacterium.updateEPSSecretion(spatialGrid)) {
                    events.add(new ParticleEvent(ParticleEvent.Type.EPS_SECRETION, bacterium));
                }
            }
        }
        
        return events;
    }
}
