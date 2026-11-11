

import java.util.Random;

class EPSParticle extends Particle {
    // In each class that uses Random:
    private Random random;
    public EPSParticle(int id, Vector2D position, double radius, double friction) {
        this.id = id;
        this.position = position;
        this.radius = radius;
        this.friction = friction;
        this.length = radius*2;
        
        this.angle = 0.0;             // EPS-specific: no orientation
        this.velocity = new Vector2D(0, 0);
        this.totalForce = new Vector2D(0, 0);
        this.random =new Random(73+id);
    }

    /**
     * Calculate the area of the EPS particle
     */
    public double calcArea() {
        return Math.PI * radius * radius;
    }

    @Override
    public void update(double deltaTime, NutrientField nutrientField) {
        // 1. Add random noise
        Vector2D noiseForce = getRandomForce();
        addForce(noiseForce);

        // 2. Over-damped dynamics
        this.velocity = totalForce.multiply(1.0 / (friction/deltaTime * (radius * 2)));

        // 3. Update position
        position = position.add(velocity.multiply(deltaTime));

        // 4. Boundary handling (clamp and bounce)
        double halfSize = 200; // simulation size / 2
        double minX = -halfSize, maxX = halfSize;
        double minY = -halfSize, maxY = halfSize;

        if (position.getX() < minX) {
            position.setX(minX);
            velocity.setX(-velocity.getX());
        } else if (position.getX() > maxX) {
            position.setX(maxX);
            velocity.setX(-velocity.getX());
        }

        if (position.getY() < minY) {
            position.setY(minY);
            velocity.setY(-velocity.getY());
        } else if (position.getY() > maxY) {
            position.setY(maxY);
            velocity.setY(-velocity.getY());
        }

        // 5. Reset velocity and clear forces
        this.velocity = new Vector2D(0, 0);
        clearForces();
    }

    private Vector2D getRandomForce() {
        double magnitude = (random.nextDouble() - 0.5) * 2e-3;
        double angle = random.nextDouble() * 2 * Math.PI;
        return new Vector2D(
            magnitude * Math.cos(angle),
            magnitude * Math.sin(angle)
        );
    }
}
