
// EPSParticleTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class EPSParticleTest {
    private EPSParticle eps;
    private NutrientField nutrientField;
    
    @BeforeEach
    void setUp() {
        eps = new EPSParticle(1, new Vector2D(10, 20), 0.25, 200.0);
        nutrientField = new NutrientField(-200, -200);
    }
    
    @Test
    void testConstructor() {
        assertEquals(1, eps.getId());
        assertEquals(10.0, eps.getPosition().getX(), 1e-10);
        assertEquals(20.0, eps.getPosition().getY(), 1e-10);
        assertEquals(0.25, eps.getRadius(), 1e-10);
        assertEquals(0.5, eps.getLength(), 1e-10); // length = radius * 2
        assertEquals(0.0, eps.getAngle(), 1e-10);
    }
    
    @Test
    void testCalcArea() {
        double expectedArea = Math.PI * 0.25 * 0.25;
        assertEquals(expectedArea, eps.calcArea(), 1e-10);
    }
    
    @Test
    void testUpdate() {
        Vector2D originalPosition = new Vector2D(eps.getPosition().getX(), eps.getPosition().getY());
        
        eps.update(0.1, nutrientField);
        
        // Position may change due to random forces
        // Forces should be cleared after update
        assertEquals(0.0, eps.getTotalForce().getX(), 1e-10);
        assertEquals(0.0, eps.getTotalForce().getY(), 1e-10);
        
        // Velocity should be reset to zero
        assertEquals(0.0, eps.getVelocity().getX(), 1e-10);
        assertEquals(0.0, eps.getVelocity().getY(), 1e-10);
    }
    
    @Test
    void testBoundaryHandling() {
        // Test particle at boundary
        EPSParticle boundaryEPS = new EPSParticle(2, new Vector2D(250, 250), 0.25, 200.0);
        boundaryEPS.update(0.1, nutrientField);
        
        // Should be clamped to boundary
        assertTrue(boundaryEPS.getPosition().getX() <= 200.0);
        assertTrue(boundaryEPS.getPosition().getY() <= 200.0);
    }
}