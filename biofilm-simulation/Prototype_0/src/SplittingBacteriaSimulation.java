import java.util.ArrayList;
import java.util.List;
public class SplittingBacteriaSimulation {
    
    private List<Bacteria> bacteriaList;
    private DataWriter writer;
    public SplittingBacteriaSimulation() {
        // Create one bacteria at center of "world" with motility force 500
        writer = new DataWriter("./bin/test1.bin");
        bacteriaList = new ArrayList<>();
        bacteriaList.add(new Bacteria(.0, 0.0, 500.0));
    }
    
    public void run() {
        System.out.println("Starting splitting bacteria simulation...");
        
        double deltaTime = 0.001; 
        double elapsedTime = 0.0;
        double printInterval = 600;
        double nextPrintTime = printInterval;
        while (elapsedTime <= 3600.0*24+1) {
            
            // Update bacteria physics
            updateAll(deltaTime);

            // Print position every simulated interval
           
            if (elapsedTime>=nextPrintTime) {
                printStatus(elapsedTime);
                nextPrintTime += printInterval;
            }
            elapsedTime += deltaTime;
            
            
        }
        writer.close();
    }
    
    private void printStatus(double elapsedTime) {
        for (int i = 0; i < bacteriaList.size(); i++) {
            Bacteria bacteria = bacteriaList.get(i);
            Vector2D position = bacteria.getPosition();
            System.out.printf("ID:%d | Time: %.1fs | Position: %s | Angle: %.1f° | Speed: %.2f | Length: %.2f%n",
                i,
                elapsedTime,
                position.toString(),
                bacteria.getAngleDegrees(),
                bacteria.getSpeed(),
                bacteria.getLength()
            );

            writer.WriteFile(
                elapsedTime,
                i,
                position.getX(),
                position.getY(),
                bacteria.getAngleDegrees(),
                bacteria.getSpeed(),
                bacteria.getLength()
            );
        }
    }
    
    private void updateAll(double deltaTime) {
        List<Bacteria> newBacteria = new ArrayList<>();
        //List<Bacteria> toRemove = new ArrayList<>();

        for (Bacteria bacterium : bacteriaList) {
            bacterium.update(deltaTime);
            
            // Check if this bacterium should divide
            if (bacterium.shouldDivide(deltaTime)) {
                Bacteria[] daughters = bacterium.divide();
                newBacteria.add(daughters[0]);
                //newBacteria.add(daughters[1]);
                //toRemove.add(bacterium); // Mark parent for removal
            }
        }
        
        // Apply changes after iteration
        //bacteriaList.removeAll(toRemove);
        bacteriaList.addAll(newBacteria);
    }
    
    public static void main(String[] args) {
        SplittingBacteriaSimulation sim = new SplittingBacteriaSimulation();
        sim.run();
    }
}

