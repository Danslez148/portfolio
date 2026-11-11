import java.util.List;

public class ForceCalculator {
    
    static void calculateRepulsiveForces(List<Particle> particles , double E) {
        // Clear forces first
        for (Particle particle: particles) {
            Vector2D clearForce = new Vector2D(0, 0);
            particle.setTotalForce(clearForce);
        }

        int n = particles.size();
        for (int i = 0; i < n; i++) {
            Particle p1 = particles.get(i);
            for (int j = i + 1; j < n; j++) {
                Particle p2 = particles.get(j);

                Vector2D displacement = p2.position.subtract(p1.position);
                double distance = displacement.magnitude();
                if (distance < 1e-6) continue;

                double overlap = (p1.radius + p2.radius) - distance;
                if (overlap <= 0) continue;

                // Bera et al. repulsive force
                double forceMag = E * Math.sqrt(distance) * Math.pow(overlap, 1.5);
                Vector2D force = displacement.normalize().multiply(forceMag);
                Vector2D forceReverse = displacement.normalize().multiply(-forceMag);
            
                p1.addForce(force);
                p2.addForce(forceReverse);
            }
        }
    }
}
