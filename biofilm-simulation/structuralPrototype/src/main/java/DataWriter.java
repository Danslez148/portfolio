
import java.io.*;
import java.util.*;
// DataWriter class
class DataWriter {
    private PrintWriter writer;
    private boolean headerWritten = false;
    
    public DataWriter(String filename) {
        try {
            new File (filename).getParentFile().mkdirs();
            writer = new PrintWriter(new BufferedWriter(new FileWriter(filename)));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    
    private void writeHeader() {
        if (!headerWritten) {
            writer.println("time,id,x,y,angle,length,type");
            headerWritten = true;
        }
    }
    /*
     * write particles to file in format 
     * time, id, x, y, angle, length, type
     */
    public void WriteParticleToFile(double elapsedTime, Particle particle) {
        writeHeader();
        writer.printf("%f,%d,%f,%f,%f,%f,%s%n",
                elapsedTime,
                particle.getId(),
                particle.getX(),
                particle.getY(),
                particle.getAngle(),
                particle.getLength(),
                particle.getClass().getSimpleName());
    }
    
    public void WriteParticlesToFile(double elapsedTime, List<Particle> particles) {
        for (Particle particle : particles) {
            WriteParticleToFile(elapsedTime, particle);
        }
    }
    
    public void close() {
        if (writer != null) {
            writer.close();
        }
    }
}
