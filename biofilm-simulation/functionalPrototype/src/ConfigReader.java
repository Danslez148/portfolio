import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class ConfigReader {
    public double startX;
    public double startY;
    public double motilityForce;
    public double deltaTime;
    public double printInterval;
    public double simulationDuration;

    public ConfigReader(String filePath) {
        try (BufferedReader br = new BufferedReader(new FileReader(filePath))) {
            startX = readValue(br);
            startY = readValue(br);
            motilityForce = readValue(br);
            deltaTime = readValue(br);
            printInterval = readValue(br);
            simulationDuration = readValue(br);
        } catch (IOException e) {
            throw new RuntimeException("Error reading config file", e);
        }
    }

    private double readValue(BufferedReader br) throws IOException {
        String line = br.readLine();
        if (line == null) throw new IOException("Unexpected end of config file");
        String[] parts = line.split("=");
        return Double.parseDouble(parts[1].trim());
    }
}
