
// Vector2DTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertNotEquals;

public class BacteriaCellTest {
    private BacteriaCell bacterium;
    private SimulationConfig config;
    private NutrientField nutrientField;
    
    @BeforeEach
    void setUp() {
        config = new SimulationConfig();
        bacterium = new BacteriaCell(1, new Vector2D(0, 0), 3.0, 0.5, 0.0, 0.0, 200.0, 1100.0,
                0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        nutrientField = new NutrientField(-200, -200);
    }
    
    @Test
    void testConstructor() {
        assertEquals(1, bacterium.getId());
        assertEquals(0.0, bacterium.getPosition().getX(), 1e-10);
        assertEquals(0.0, bacterium.getPosition().getY(), 1e-10);
        assertEquals(3.0, bacterium.getLength(), 1e-10);
        assertEquals(0.5, bacterium.getRadius(), 1e-10);
        assertEquals(0.0, bacterium.getAngle(), 1e-10);
    }
    
    @Test
    void testCalcArea() {
        double expectedArea = Math.PI * 0.5 * 0.5 + 2.0 * 0.5 * 3.0;
        assertEquals(expectedArea, bacterium.calcArea(), 1e-10);
    }
    
    @Test
    void testCalcAvgArea() {
        double expectedAvgArea = Math.PI * 0.5 * 0.5 + 1.5 * 0.5 * 3.0;
        assertEquals(expectedAvgArea, bacterium.calcAvgArea(), 1e-10);
    }
    
    @Test
    void testShouldDivide() {
        assertFalse(bacterium.shouldDivide()); // length = 3.0, critLength = 5.0
        
        // Grow the bacterium to division length
        BacteriaCell longBacterium = new BacteriaCell(2, new Vector2D(0, 0), 5.5, 0.5, 0.0, 0.0, 
                200.0, 1100.0, 0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        assertTrue(longBacterium.shouldDivide());
    }
    
    @Test
    void testDivide() {
        double originalLength = bacterium.getLength();
        bacterium.divide();
        assertEquals(originalLength / 2.0, bacterium.getLength(), 1e-10);
    }
    
    @Test
    void testCreateDaughter() {
        BacteriaCell daughter = bacterium.createDaughter(2);
        
        assertEquals(2, daughter.getId());
        assertEquals(bacterium.getLength()/2, daughter.getLength(), 1e-10);
        assertEquals(bacterium.getRadius(), daughter.getRadius(), 1e-10);
        
        // Daughter should be at a different position
        assertNotEquals(bacterium.getPosition().getX(), daughter.getPosition().getX());
    }
    
    @Test
    void testUpdate() {
        Vector2D originalPosition = new Vector2D(bacterium.getPosition().getX(), bacterium.getPosition().getY());
        double originalLength = bacterium.getLength();
        
        bacterium.update(0.1, nutrientField);
        
        // Position should change due to motility
        assertTrue(bacterium.getPosition().distance(originalPosition) > 0);
        
        // Length should increase due to growth (assuming positive nutrient concentration)
        assertTrue(bacterium.getLength() >= originalLength);
        
        // Forces should be cleared after update
        assertEquals(0.0, bacterium.getTotalForce().getX(), 1e-10);
        assertEquals(0.0, bacterium.getTotalForce().getY(), 1e-10);
    }
    
    @Test
    void testForceManagement() {
        Vector2D force = new Vector2D(10.0, 5.0);
        bacterium.addForce(force);
        
        assertEquals(10.0, bacterium.getTotalForce().getX(), 1e-10);
        assertEquals(5.0, bacterium.getTotalForce().getY(), 1e-10);
        
        bacterium.clearForces();
        assertEquals(0.0, bacterium.getTotalForce().getX(), 1e-10);
        assertEquals(0.0, bacterium.getTotalForce().getY(), 1e-10);
    }
}