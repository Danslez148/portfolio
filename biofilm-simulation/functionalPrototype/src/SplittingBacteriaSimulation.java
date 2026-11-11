    import java.util.ArrayList;
    import java.util.List;
    public class SplittingBacteriaSimulation {
        
        private List<Bacteria> bacteriaList;
        private fileWriter writer;
        private double deltaTime;
        private double printInterval;
        private double simulationDuration;


        public SplittingBacteriaSimulation(String configPath) {
            // Create one bacteria at center of "world" with motility force 500
            writer = new fileWriter("./functionalPrototype/bin/test1.bin");
            bacteriaList = new ArrayList<>();
            bacteriaList.add(new Bacteria(.0, 0.0, 500.0));

            ConfigReader config = new ConfigReader(configPath);

            writer = new fileWriter("./functionalPrototype/bin/test1.bin");
            bacteriaList = new ArrayList<>();
            bacteriaList.add(new Bacteria(config.startX, config.startY, config.motilityForce));

            this.deltaTime = config.deltaTime;
            this.printInterval = config.printInterval;
            this.simulationDuration = config.simulationDuration;
        }
        
        public void run() {
            System.out.println("Starting splitting bacteria simulation...");
            
            double elapsedTime = 0.0;
            double nextPrintTime = printInterval;
            while (elapsedTime <= simulationDuration) {
                
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
                writer.writeFile(
                    elapsedTime,
                    i,
                    position.getX(),
                    position.getY(),
                    bacteria.getAngleDegrees(),
                    bacteria.getLength()
                );
            }
        }
        
        private void updateAll(double deltaTime ) {
            List<Bacteria> newBacteria = new ArrayList<>();
            //List<Bacteria> toRemove = new ArrayList<>();

            for (Bacteria bacterium : bacteriaList) {
                bacterium.update(deltaTime, bacteriaList);
                
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
            String file = "./functionalPrototype/config.txt";
            SplittingBacteriaSimulation sim = new SplittingBacteriaSimulation(file);
            sim.run();
        }
    }

