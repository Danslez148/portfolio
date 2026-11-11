
// ForceCalculatorTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.List;

public class ForceCalculatorTest {
    private ForceCalculator calculator;
    private SimulationConfig config;
    private BacteriaCell bacterium1;
    private BacteriaCell bacterium2;
    private EPSParticle eps;
    
    @BeforeEach
    void setUp() {
        config = new SimulationConfig();
        calculator = new ForceCalculator(config);
        
        bacterium1 = new BacteriaCell(1, new Vector2D(0, 0), 3.0, 0.5, 0.0, 0.0, 200.0, 1100.0,
                0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        bacterium2 = new BacteriaCell(2, new Vector2D(0.5, 0), 3.0, 0.5, 0.0, 0.0, 200.0, 1100.0,
                0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        eps = new EPSParticle(3, new Vector2D(1, 0), 0.25, 200.0);
    }
    
    @Test
    void testConstructor() {
        assertNotNull(calculator);
    }
    
    @Test
    void testCalculateRepulsiveForces() {
        List<Particle> particles = new ArrayList<>();
        particles.add(bacterium1);
        particles.add(bacterium2);
        particles.add(eps);
        List<Particle> neighbors = new ArrayList<>();
        neighbors.add(bacterium1);
        neighbors.add(bacterium2);
        neighbors.add(eps);

        // Clear forces before calculation
        bacterium1.clearForces();
        bacterium2.clearForces();
        
        calculator.calculateRepulsiveForces(particles, neighbors);
        
        // Forces should be applied due to overlap
        assertTrue(bacterium1.getTotalForce().magnitude() > 0);
    }
    
    @Test
    void testSegmentClosestPoints() {
        Vector2D p1 = new Vector2D(0, 0);
        Vector2D q1 = new Vector2D(1, 0);
        Vector2D p2 = new Vector2D(0.5, 1);
        Vector2D q2 = new Vector2D(0.5, -1);
        
        ForceCalculator.ClosestPoints cp = calculator.segmentClosestPoints(p1, q1, p2, q2);
        
        assertNotNull(cp);
        assertNotNull(cp.pointOnSeg1);
        assertNotNull(cp.pointOnSeg2);
        assertTrue(cp.distance >= 0);
        
        // The closest points should be at (0.5, 0) and (0.5, 0)
        assertEquals(0.5, cp.pointOnSeg1.getX(), 1e-10);
        assertEquals(0.0, cp.pointOnSeg1.getY(), 1e-10);
        assertEquals(0.5, cp.pointOnSeg2.getX(), 1e-10);
        assertEquals(0.0, cp.pointOnSeg2.getY(), 1e-10);
        assertEquals(0.0, cp.distance, 1e-10);
    }
    
    @Test
    void testNoForcesWhenParticlesAreFarApart() {
        // Place particles far apart
        bacterium2.setPosition(new Vector2D(100, 100));
        
        List<Particle> particles = new ArrayList<>();
        particles.add(bacterium1);
        
        List<Particle> neighbors = new ArrayList<>();
        neighbors.add(bacterium2);
        
        bacterium1.clearForces();
        
        calculator.calculateRepulsiveForces(particles, neighbors);
        
        // No forces should be applied when particles are far apart
        assertEquals(0.0, bacterium1.getTotalForce().magnitude(), 1e-10);
    }
}