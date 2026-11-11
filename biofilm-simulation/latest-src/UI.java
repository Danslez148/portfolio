import java.awt.*;
import java.io.*;
import javax.swing.*;

public class UI {
    private String configFileName;
    private DataVisualizer dataVisualizer;
    private JFrame mainFrame = new JFrame("Biofilm Simulation");
    private JFrame simFrame = new JFrame("Simulation");
    private JFrame visFrame = new JFrame("Visualisation");
    private File resultsFile = new File("results.txt");
    private File visFile; // File containing visualization results
    /**
     * Initializes and displays the main home frame with navigation buttons.
     */
    // main home frame init
    public void beginProject(){
        mainFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        mainFrame.setSize(800, 600);
        mainFrame.setVisible(true);
        JButton simBtn = new JButton("Run New Simulation");
        JButton visBtn = new JButton("Visualize Simulation Run Data");
        simBtn.addActionListener(e -> simFrame());
        visBtn.addActionListener(l -> visFrame());
        mainFrame.setLayout(new GridBagLayout());
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.add(simBtn);
        panel.add(visBtn);
        mainFrame.add(panel, new GridBagConstraints());
    }
    /**
     * Shows the simulation frame with a centered back button.
     */
    // simulation frame init
    public void simFrame(){
        mainFrame.setVisible(false);
        simFrame.getContentPane().removeAll(); // Clear previous components
        simFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        simFrame.setSize(800, 600);
        simFrame.setLayout(new GridBagLayout());
        JPanel panel = new JPanel(new GridBagLayout());
        JButton back = new JButton("Back");
        back.addActionListener(e -> {
            simFrame.setVisible(false);
            mainFrame.setVisible(true);
        });
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.anchor = GridBagConstraints.CENTER;
        panel.add(back, gbc);
        simFrame.add(panel, gbc);
        simFrame.revalidate();
        simFrame.repaint();
        simFrame.setVisible(true);
    }
    /**
     * Shows the visualisation frame with a centered back button and file selector.
     * Selected file is used to run the data visualiser and saves the file created to the device. 
     * the open button then allows for the view of the file from the UI. 
     * ??The file name will be changed according to the parameters and the date maybe so all runs have a unique name.
     */
    public void visFrame(){
        mainFrame.setVisible(false);
        visFrame.getContentPane().removeAll(); // Clear previous components
        visFrame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        visFrame.setSize(800, 600);
        visFrame.setLayout(new GridBagLayout());
        JPanel panel = new JPanel(new GridBagLayout());
        JButton back = new JButton("Back");
        back.addActionListener(e -> {
            visFrame.setVisible(false);
            mainFrame.setVisible(true);
        });
        JButton selectFileBtn = new JButton("Select File");
        selectFileBtn.addActionListener(e -> {
            selectFileAndSaveToResults();
            // Run DataVisualizer on resultsFile and save output to visFile
            visFile = new File("visualization.txt");
            if (dataVisualizer != null && resultsFile.exists()) {
                try {
                    dataVisualizer.visualise(resultsFile, visFile);
                    JOptionPane.showMessageDialog(visFrame, "Visualization saved to " + visFile.getAbsolutePath());
                } catch (Exception ex) {
                    JOptionPane.showMessageDialog(visFrame, "Visualization error: " + ex.getMessage());
                }
            }
        });
        JButton openVisBtn = new JButton("Open Visualization File");
        openVisBtn.addActionListener(e -> {
            if (visFile != null && visFile.exists()) {
                try {
                    Desktop.getDesktop().open(visFile);
                } catch (IOException ex) {
                    JOptionPane.showMessageDialog(visFrame, "Cannot open file: " + ex.getMessage());
                }
            } else {
                JOptionPane.showMessageDialog(visFrame, "Visualization file does not exist.");
            }
        });
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.anchor = GridBagConstraints.CENTER;
        panel.add(back, gbc);
        gbc.gridy = 1;
        panel.add(selectFileBtn, gbc);
        gbc.gridy = 2;
        panel.add(openVisBtn, gbc);
        visFrame.add(panel, gbc);
        visFrame.revalidate();
        visFrame.repaint();
        visFrame.setVisible(true);
    }

    /**
     * Opens a file chooser, copies the selected file to resultsFile, and shows a message.
     */
    private void selectFileAndSaveToResults() {
        JFileChooser fileChooser = new JFileChooser();
        int result = fileChooser.showOpenDialog(visFrame);
        if (result == JFileChooser.APPROVE_OPTION) {
            File selectedFile = fileChooser.getSelectedFile();
            try (InputStream in = new FileInputStream(selectedFile);
                 OutputStream out = new FileOutputStream(resultsFile)) {
                byte[] buffer = new byte[1024];
                int bytesRead;
                while ((bytesRead = in.read(buffer)) != -1) {
                    out.write(buffer, 0, bytesRead);
                }
                JOptionPane.showMessageDialog(visFrame, "File received to " + resultsFile.getAbsolutePath());
            } catch (IOException ex) {
                JOptionPane.showMessageDialog(visFrame, "Error receiving file: " + ex.getMessage());
            }
        }
    }

    public void selectConfigFile(String filePath) {
        // insert functionality
    }

    public void visualizeData() {
        // insert functionality
    }

    public void runSimulation() {
        // insert functionality
    }

    public void visualizeSimulationData(String filePath) {
        // insert functionality
    }

    public void generateConfigUI(double value) {
        // insert functionality
    }
}
