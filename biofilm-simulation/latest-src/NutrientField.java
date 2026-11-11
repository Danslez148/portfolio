import java.util.List;
public class NutrientField {
    private double[][] concentration;
    private int concGridWidth;
    private int concGridHeight;
    private double minX;
    private double minY;
    private final double concGridCellSize = 10.0; // Assuming 1 unit per cell
    private final double initialConcentration = 3.0;
    private final double consumptionRate = 4.0;
    private final double diffusionRate = 300.0;

    //to add: particles eating nutrients and growing accordingly

    public NutrientField(double minX, double minY) {
        this.minX = minX;
        this.minY = minY;
        concGridHeight = (int) Math.ceil(2.0 * Math.abs(minY) / concGridCellSize); //check if Y flipped
        concGridWidth = (int) Math.ceil(2.0 * Math.abs(minX) / concGridCellSize);
        concentration = new double[concGridWidth][concGridHeight];
        // Initialize concentration grid
        for (int x = 0; x < concGridWidth; x++) {
            for (int y = 0; y < concGridHeight; y++) {
                concentration[x][y] = initialConcentration;
            }
        }
    }

    public int[] getConcGridXCoords(Vector2D position) {
        int gridX = (int) Math.floor((position.getX() - minX) / concGridCellSize);
        int gridY = (int) Math.floor((Math.abs(minY) - position.getY()) / concGridCellSize); //flipped?
        return new int[]{gridX, gridY};

    }

    public double getConcentration(Vector2D position) {
        int[] coords = getConcGridXCoords(position);
        int gridX = coords[0];
        int gridY = coords[1];
        if (gridX >= 0 && gridX < concGridWidth && gridY >= 0 && gridY < concGridHeight) {
            return concentration[gridX][gridY];
        }
        return 0.0; // Outside bounds
    }

    public void diffuse(double deltaTime, List<BacteriaCell> bacteria) {
        double[][] newConcentration = new double[concGridWidth][concGridHeight];

        for (int x=1; x < concGridWidth - 1; x++) {
            for (int y=1; y < concGridHeight - 1; y++) {
                // Set boundary cells on leading edge to initialConcentration (in line with Bera Et Al.)
                for (int m = 0; m < concGridWidth; m++) {
                    newConcentration[m][0] = initialConcentration;
                    newConcentration[m][concGridHeight - 1] = initialConcentration;
                }
                for (int n = 0; n < concGridHeight; n++) {
                    newConcentration[0][n] = initialConcentration;
                    newConcentration[concGridWidth - 1][n] = initialConcentration;
                }

                double laplacian = concentration[x+1][y] + concentration[x-1][y] +
                                   concentration[x][y+1] + concentration[x][y-1] -
                                   4 * concentration[x][y]; //correct implementation? needs h^2?
                
                double diffusionTerm = diffusionRate * laplacian / (concGridCellSize * concGridCellSize);

                double consumptionTerm = 0.0;
                for (BacteriaCell cell : bacteria) {
                    int[] cellCoords = getConcGridXCoords(cell.getPosition());
                    if (cellCoords[0] == x && cellCoords[1] == y) {
                        double localConc = concentration[x][y];
                        double uptake = consumptionRate * monodFunction(localConc) * cell.calcArea();
                        consumptionTerm += uptake;
                    }
                }

                newConcentration[x][y] = concentration[x][y] + (diffusionTerm - consumptionTerm) * deltaTime;

                if (newConcentration[x][y] < 0.0) {
                    newConcentration[x][y] = 0.0; // Prevent negative concentration
                }
            }
        }
        concentration = newConcentration;
    }

    public double monodFunction(double localConcentration) {
        return (localConcentration) / (localConcentration + 1.0);
    }

}
