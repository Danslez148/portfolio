import java.io.*;

public class DataWriter {

    private DataOutputStream dataOut;

    public DataWriter(String filename) {
        try {
            dataOut = new DataOutputStream(new BufferedOutputStream(new FileOutputStream(filename)));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void WriteFile( double time, int id, double x, double y, double angle, double speed, double length) {
        try {
            dataOut.writeDouble(time);
            dataOut.writeInt(id);
            dataOut.writeDouble(x);
            dataOut.writeDouble(y);
            dataOut.writeDouble(angle);
            dataOut.writeDouble(speed);
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
