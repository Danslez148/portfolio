package barScheduling;  

import java.io.IOException;
import java.io.FileWriter;
import java.util.List;

public class Measure {
    public static void writeCPUMetricsToFile(String filename, List<Long> windowStartTimes, List<Integer> throughputValues, double utilization) throws IOException {
        try (FileWriter writer = new FileWriter(filename, true)) {
            for (int i = 0; i < windowStartTimes.size(); i++) {
                writer.append(windowStartTimes.get(i) + "," + throughputValues.get(i) + "\n");//window start time and throughput added to file
            }
            writer.append(utilization + "\n");//utilization added to file
        }
    }

    public static void writeProccessMetricsToFile(String filename, Patron[] patrons) throws IOException {
        try (FileWriter writer = new FileWriter(filename, true)) {
            for (Patron patron : patrons) {
                writer.append((patron.getID()+1) + "," + patron.getTurnaroundTime() + "," + patron.getResponseTime() + "," + patron.getWaitingTime() + "\n"); //patron ID, turnaround time, response time and waiting time added to file
            }
        }
    }

    /// Generate a file name based on the parameters
    public static String generateFileName(String baseName, int noPatrons, int schedAlg, int q) {
        String alg;
        switch (schedAlg) {
            case 0: 
                alg = "FCFS";
                break;
            case 1:
                alg = "SJF";
                break;
            case 2:
                alg = "RR";
                break;
            default:
                alg = "Error";
                break;
        };
        return baseName + "_" + noPatrons + "_" + alg + "_" + q + ".csv";
    }    
}