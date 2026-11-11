
// NutrientFieldTest.java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.List;

public class NutrientFieldTest {
    private NutrientField nutrientField;
    private List<BacteriaCell> bacteria;
    
    @BeforeEach
    void setUp() {
        nutrientField = new NutrientField(-50.0, -50.0);
        bacteria = new ArrayList<>();
        
        BacteriaCell bacterium = new BacteriaCell(1, new Vector2D(0, 0), 3.0, 0.5, 0.0, 0.0, 
                200.0, 1100.0, 0.025, 5.0, 0.3, 1.0, -1.0, 200.0);
        bacteria.add(bacterium);
    }
    
    @Test
    void testGetConcentration() {
        double concentration = nutrientField.getConcentration(new Vector2D(0, 0));
        assertEquals(3.0, concentration, 1e-10); // Initial concentration
    }
    
    @Test
    void testGetConcentrationOutOfBounds() {
        double concentration = nutrientField.getConcentration(new Vector2D(1000, 1000));
        assertEquals(0.0, concentration, 1e-10);
    }
    
    @Test
    void testMonodFunction() {
        assertEquals(0.5, nutrientField.monodFunction(1.0), 1e-10); // 1/(1+1) = 0.5
        assertEquals(2.0/3.0, nutrientField.monodFunction(2.0), 1e-10); // 2/(2+1) = 2/3
        assertEquals(0.0, nutrientField.monodFunction(0.0), 1e-10); // 0/(0+1) = 0
    }
    
    @Test
    void testDiffuse() {
        double originalConcentration = nutrientField.getConcentration(new Vector2D(0, 0));
        
        nutrientField.diffuse(0.1, bacteria);
        
        double newConcentration = nutrientField.getConcentration(new Vector2D(0, 0));
        
        // Concentration should change due to consumption and diffusion
        // (exact value depends on implementation details)
        assertTrue(newConcentration >= 0.0); // Should not go negative
    }
    
    @Test
    void testGetConcGridXCoords() {
        int[] coords = nutrientField.getConcGridXCoords(new Vector2D(0, 0));
        
        assertEquals(2, coords.length);
        assertTrue(coords[0] >= 0);
        assertTrue(coords[1] >= 0);
    }
}
