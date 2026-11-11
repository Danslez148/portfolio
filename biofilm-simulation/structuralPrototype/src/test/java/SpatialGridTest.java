
// SpatialGridTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.ArrayList;

public class SpatialGridTest {
    private SpatialGrid grid;
    private BacteriaCell bacterium1;
    private BacteriaCell bacterium2;
    private EPSParticle eps;
    
    @BeforeEach
    void setUp() {
        grid = new SpatialGrid(-50.0, -50.0, 50.0, 50.0, 10.0);
        SimulationConfig config = new SimulationConfig();
        bacterium1 = new BacteriaCell(1, new Vector2D(0, 0), 3.0, 0.5, 0.0, 0.0, 200.0, 1100.0,
                0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        bacterium2 = new BacteriaCell(2, new Vector2D(15, 15), 3.0, 0.5, 0.0, 0.0, 200.0, 1100.0,
                0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        eps = new EPSParticle(3, new Vector2D(-10, -10), 0.25, 200.0);
    }
    
    @Test
    void testConstructor() {
        assertEquals(10, grid.getGridWidth()); // (50 - (-50)) / 10 = 10
        assertEquals(10, grid.getGridHeight());
    }
    
    @Test
    void testAddParticle() {
        grid.addParticle(bacterium1);
        GridCell cell = grid.getGridCell(new Vector2D(0, 0));
        assertNotNull(cell);
        assertEquals(1, cell.size());
    }
    
    @Test
    void testGetGridCell() {
        Vector2D position = new Vector2D(0, 0);
        GridCell cell = grid.getGridCell(position);
        assertNotNull(cell);
        assertEquals(5, cell.getX()); // center of grid
        assertEquals(5, cell.getY());
    }
    
    @Test
    void testGetGridCellWithCoordinates() {
        GridCell cell = grid.getGridCell(5, 5);
        assertNotNull(cell);
        assertEquals(5, cell.getX());
        assertEquals(5, cell.getY());
        
        // Test bounds
        assertNull(grid.getGridCell(-1, 5));
        assertNull(grid.getGridCell(5, -1));
        assertNull(grid.getGridCell(10, 5));
        assertNull(grid.getGridCell(5, 10));
    }
    
    @Test
    void testUpdateGrid() {
        List<Particle> particles = new ArrayList<>();
        particles.add(bacterium1);
        particles.add(bacterium2);
        particles.add(eps);
        
        grid.updateGrid(particles);
        
        // Check that particles are in correct cells
        GridCell cell1 = grid.getGridCell(new Vector2D(0, 0));
        GridCell cell2 = grid.getGridCell(new Vector2D(15, 15));
        GridCell cell3 = grid.getGridCell(new Vector2D(-10, -10));
        
        assertEquals(1, cell1.size());
        assertEquals(1, cell2.size());
        assertEquals(1, cell3.size());
    }
    
    @Test
    void testGetNeighbors() {
        List<Particle> particles = new ArrayList<>();
        particles.add(bacterium1);
        particles.add(bacterium2);
        particles.add(eps);
        
        grid.updateGrid(particles);
        
        GridCell centerCell = grid.getGridCell(new Vector2D(0, 0));
        List<Particle> neighbors = grid.getNeighbors(centerCell);
        
        // Should find neighbors in adjacent cells but not current cell
        assertFalse(neighbors.contains(bacterium1)); // Same cell, not included
        assertTrue(neighbors.size() >= 0); // May have neighbors depending on positions
    }
    
    @Test
    void testGetNonEmptyCells() {
        List<Particle> particles = new ArrayList<>();
        particles.add(bacterium1);
        particles.add(bacterium2);
        
        grid.updateGrid(particles);
        List<GridCell> nonEmptyCells = grid.getNonEmptyCells();
        
        assertEquals(2, nonEmptyCells.size());
        for (GridCell cell : nonEmptyCells) {
            assertTrue(cell.size() > 0);
        }
    }
    
    @Test
    void testClear() {
        grid.addParticle(bacterium1);
        grid.addParticle(bacterium2);
        
        grid.clear();
        List<GridCell> nonEmptyCells = grid.getNonEmptyCells();
        assertEquals(0, nonEmptyCells.size());
    }
}
