public class SimpleBacteriaSimulation {
    private Bacteria bacteria;
  
    
    public SimpleBacteriaSimulation() {
        // Create one bacteria at center of "world" with motility force 500
        bacteria = new Bacteria(.0, 0.0, 500.0);
      
    }
    
    public void run() {
        System.out.println("Starting bacteria simulation...");
        
        double deltaTime = 0.01; 
        double elapsedTime = 0.0;
        double printInterval = 60;
        double nextPrintTime = printInterval;
        while (elapsedTime <= 3600.0*24+1) {
            
            // Update bacteria physics
            bacteria.update(deltaTime);
            

            // Print position every simulated interval
           
            if (elapsedTime>=nextPrintTime) {
                printStatus(elapsedTime);
               nextPrintTime += printInterval;
            }
            elapsedTime += deltaTime;
            
            
        }
    }
    
    private void printStatus(double elapsedTime) {
        Vector2D pos = bacteria.getPosition();
        System.out.printf("Time: %.1fs | Position: %s | Angle: %.1f° | Speed: %.2f | Length: %.2f%n",
            elapsedTime,
            pos.toString(),
            bacteria.getAngleDegrees(),
            bacteria.getSpeed(),
            bacteria.getLength()
        );
    }
    
    
   
    public static void main(String[] args) {
        SimpleBacteriaSimulation sim = new SimpleBacteriaSimulation();
        sim.run();
    }
        
}
