

// GridCellTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;

public class GridCellTest {
    private GridCell cell;
    private BacteriaCell bacterium;
    private EPSParticle eps;
    
    @BeforeEach
    void setUp() {
        cell = new GridCell(5, 10);
        SimulationConfig config = new SimulationConfig();
        bacterium = new BacteriaCell(1, new Vector2D(0, 0), 3.0, 0.5, 0.0, 0.0, 200.0, 1100.0,
                0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        eps = new EPSParticle(2, new Vector2D(1, 1), 0.25, 200.0);
    }
    
    @Test
    void testConstructor() {
        assertEquals(5, cell.getX());
        assertEquals(10, cell.getY());
        assertEquals(0, cell.size());
    }
    
    @Test
    void testAddParticle() {
        cell.addParticle(bacterium);
        assertEquals(1, cell.size());
        
        List<Particle> particles = cell.getParticlesCopy();
        assertEquals(1, particles.size());
        assertEquals(bacterium, particles.get(0));
    }
    
    @Test
    void testAddMultipleParticles() {
        cell.addParticle(bacterium);
        cell.addParticle(eps);
        assertEquals(2, cell.size());
        
        List<Particle> particles = cell.getParticlesCopy();
        assertEquals(2, particles.size());
        assertTrue(particles.contains(bacterium));
        assertTrue(particles.contains(eps));
    }
    
    @Test
    void testRemoveParticle() {
        cell.addParticle(bacterium);
        cell.addParticle(eps);
        assertEquals(2, cell.size());
        
        cell.removeParticle(bacterium);
        assertEquals(1, cell.size());
        
        List<Particle> particles = cell.getParticlesCopy();
        assertFalse(particles.contains(bacterium));
        assertTrue(particles.contains(eps));
    }
    
    @Test
    void testClear() {
        cell.addParticle(bacterium);
        cell.addParticle(eps);
        assertEquals(2, cell.size());
        
        cell.clear();
        assertEquals(0, cell.size());
        assertTrue(cell.getParticlesCopy().isEmpty());
    }
    
    @Test
    void testGetParticlesCopyIsActualCopy() {
        cell.addParticle(bacterium);
        List<Particle> particles1 = cell.getParticlesCopy();
        List<Particle> particles2 = cell.getParticlesCopy();
        
        assertNotSame(particles1, particles2);
        assertEquals(particles1.size(), particles2.size());
    }
}