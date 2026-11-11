import java.io.*;

public class fileWriter {

    private DataOutputStream dataOut;

    public fileWriter(String filename) {
        try {
            dataOut = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(filename)));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void writeFile( double time, int id, double x, double y, double angle, double length) {
        try {
            dataOut.writeDouble(time);
            dataOut.writeInt(id);
            dataOut.writeDouble(x);
            dataOut.writeDouble(y);
            dataOut.writeDouble(angle);
            dataOut.writeDouble(length);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void close() {
        try {
            dataOut.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
