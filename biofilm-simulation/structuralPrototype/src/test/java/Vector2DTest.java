// Vector2DTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class Vector2DTest {
    private Vector2D v1;
    private Vector2D v2;
    
    @BeforeEach
    void setUp() {
        v1 = new Vector2D(3.0, 4.0);
        v2 = new Vector2D(1.0, 2.0);
    }
    
    @Test
    void testConstructor() {
        assertEquals(3.0, v1.getX(), 1e-10);
        assertEquals(4.0, v1.getY(), 1e-10);
    }
    
    @Test
    void testAdd() {
        Vector2D result = v1.add(v2);
        assertEquals(4.0, result.getX(), 1e-10);
        assertEquals(6.0, result.getY(), 1e-10);
    }
    
    @Test
    void testSubtract() {
        Vector2D result = v1.subtract(v2);
        assertEquals(2.0, result.getX(), 1e-10);
        assertEquals(2.0, result.getY(), 1e-10);
    }
    
    @Test
    void testMultiply() {
        Vector2D result = v1.multiply(2.0);
        assertEquals(6.0, result.getX(), 1e-10);
        assertEquals(8.0, result.getY(), 1e-10);
    }
    
    @Test
    void testDot() {
        double result = v1.dot(v2);
        assertEquals(11.0, result, 1e-10); // 3*1 + 4*2 = 11
    }
    
    @Test
    void testMagnitude() {
        assertEquals(5.0, v1.magnitude(), 1e-10); // sqrt(3^2 + 4^2) = 5
    }
    
    @Test
    void testNormalize() {
        Vector2D normalized = v1.normalize();
        assertEquals(0.6, normalized.getX(), 1e-10);
        assertEquals(0.8, normalized.getY(), 1e-10);
        assertEquals(1.0, normalized.magnitude(), 1e-10);
    }
    
    @Test
    void testNormalizeZeroVector() {
        Vector2D zero = new Vector2D(0.0, 0.0);
        Vector2D normalized = zero.normalize();
        assertEquals(0.0, normalized.getX(), 1e-10);
        assertEquals(0.0, normalized.getY(), 1e-10);
    }
    
    @Test
    void testDistance() {
        double distance = v1.distance(v2);
        assertEquals(Math.sqrt(8.0), distance, 1e-10); // sqrt((3-1)^2 + (4-2)^2)
    }
    
    @Test
    void testCross() {
        double result = v1.cross(v2);
        assertEquals(2.0, result, 1e-10); // 3*2 - 4*1 = 2
    }
}







// Additional Integration Tests

