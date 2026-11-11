import java.util.List;
import java.util.concurrent.ConcurrentLinkedQueue;

public class ForceCalculator {

    public void calculateRepulsiveForces(List<Particle> particles ,SpatialGrid spatialGrid, ConcurrentLinkedQueue<String> particleInteractions, double sameCellElasticModulus, double diffCellElasticModulus) {
        // Clear forces first
        for (Particle particle: particles) {
            particle.clearForces();
        }
        int n = particles.size();

        for (int i = 0; i < n; i++) {
            Particle p1 = particles.get(i);
            List<Particle> neighbors = spatialGrid.getParticleNeighbors(p1);
            for (Particle p2 : neighbors) {
                String interactionKey = p1.getId() + "-" + p2.getId();
                String reverseKey = p2.getId() + "-" + p1.getId();
                if (particleInteractions.contains(interactionKey) || particleInteractions.contains(reverseKey)) {
                    continue; // Skip already processed pairs
                }
                // Mark this pair as processed
                particleInteractions.add(interactionKey);

                Vector2D displacement = p2.position.subtract(p1.position);
                double distance = displacement.magnitude();
                if (distance < 1e-6) continue;

                double overlap = (p1.radius + p2.radius) - distance;
                if (overlap <= 0) continue;
                double forceMag = 0;
                // Bera et al. repulsive force
                if(p1 instanceof BacteriaCell && p2 instanceof BacteriaCell) {
                    // Both are bacteria cells
                    // Use same-cell elastic modulus
                     forceMag = sameCellElasticModulus * Math.sqrt(distance) * Math.pow(overlap, 1.5);
                } else if(p1 instanceof EPSParticle && p2 instanceof EPSParticle) {
                    // At least one is EPS particle
                    // Use different-cell elastic modulus
                    forceMag = sameCellElasticModulus * Math.sqrt(distance) * Math.pow(overlap, 1.5);
                }else{
                    // One is bacteria, one is EPS
                    // Use different-cell elastic modulus
                    forceMag = diffCellElasticModulus * Math.sqrt(distance) * Math.pow(overlap, 1.5);
                }
               
                Vector2D force = displacement.normalize().multiply(forceMag);
                Vector2D forceReverse = displacement.normalize().multiply(-forceMag);
                System.out.println("force between particles " + p1.getId() + " and " + p2.getId() + ": " + force);
                // add forces
                p1.addForce(force);
                p2.addForce(forceReverse);
            }
        }
    }
}
