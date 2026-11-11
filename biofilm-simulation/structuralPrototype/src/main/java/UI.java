import javax.swing.*;
import java.awt.*;
import java.io.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.function.Supplier;

public class UI extends JFrame {

    // Panels
    private JPanel mainPanel, simPanel, visPanel;

    // Simulation UI
    private JLabel simStatus;
    private JButton simChooseFile, simRun, simStop;
    private File simConfigFile;
    private AtomicBoolean simStopFlag;
    private Supplier<Boolean> simStopSupplier;

    // Visualisation UI
    private JLabel visStatus;
    private JButton visChooseFile, visRun, visStop;
    private File visInputFile;
    private Process visImageProcess;
    private Process visVideoProcess;

    // Display UI
    private JPanel displayPanel;
    private JButton loadImages, nextImage, prevImage;
    private JLabel imageLabel;
    private File[] pngFiles;
    private int currentImageIndex = 0;

    public UI() {
        setTitle("Biofilm Simulation/Visualisation");
        setSize(800, 800);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);
        setLayout(new CardLayout());

        createMainPanel();
        createSimPanel();
        createVisPanel();
        createDisplayPanel();

        add(mainPanel, "main");
        add(wrapWithBackButton(simPanel, "main"), "simulation");
        add(wrapWithBackButton(visPanel, "main"), "visualisation");
        add(wrapWithBackButton(displayPanel, "main"), "display");
    }

    private JPanel wrapWithBackButton(JPanel contentPanel, String backDestination) {
        JPanel wrapper = new JPanel(new BorderLayout());
        JPanel topBar = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
        JButton back = new JButton("Back");
        back.addActionListener(e -> showPanel(backDestination));
        topBar.add(back);
        wrapper.add(topBar, BorderLayout.NORTH);
        wrapper.add(contentPanel, BorderLayout.CENTER);
        return wrapper;
    }

    // Main menu panel
    private void createMainPanel() {
        mainPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx=0;
        gbc.fill = GridBagConstraints.NONE;
        gbc.insets = new Insets(10, 10, 10, 10);

        JButton goSim = new JButton("Run Simulation");
        goSim.setPreferredSize(new Dimension(200,50));
        gbc.gridy = 0;
        mainPanel.add(goSim, gbc);

        JButton goVis = new JButton("Visualise Results");
        goVis.setPreferredSize(new Dimension(200,50));
        gbc.gridy = 1;
        mainPanel.add(goVis, gbc);

        JButton goDisplay = new JButton("Display Images");
        goDisplay.setPreferredSize(new Dimension(200,50));
        gbc.gridy = 2;
        mainPanel.add(goDisplay, gbc);

        goSim.addActionListener(e -> showPanel("simulation"));
        goVis.addActionListener(e -> showPanel("visualisation"));
        goDisplay.addActionListener(e -> showPanel("display"));
    }

    // Simulation panel
    private void createSimPanel() {
        simPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx=0;
        gbc.fill = GridBagConstraints.NONE;
        gbc.insets = new Insets(5, 10, 5, 10);

        simChooseFile = new JButton("Choose file to input");
        simChooseFile.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 0;
        simPanel.add(simChooseFile, gbc);

        simRun = new JButton("Run Simulation");
        simRun.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 1;
        simPanel.add(simRun, gbc);

        simStop = new JButton("Stop Simulation");
        simStop.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 2;
        simPanel.add(simStop, gbc);

        simStatus = new JLabel("Simulation not started", SwingConstants.CENTER);
        simStatus.setPreferredSize(new Dimension(300,40));
        gbc.gridy = 3;
        simPanel.add(simStatus, gbc);
/* 
        JButton back = new JButton("Back");
        back.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 4;
        simPanel.add(back, gbc);

        back.addActionListener(e -> showPanel("main"));
*/
        simRun.setEnabled(false); // disabled until config is loaded
        simStop.setEnabled(false);

        // Choose file and enable Run button if file is valid
        simChooseFile.addActionListener(e -> {
            simConfigFile = chooseFile();
            if (simConfigFile != null && readConfig(simConfigFile) != null) {
                simRun.setEnabled(true);
            }
        });

        simRun.addActionListener(e -> startSimulation());
        simStop.addActionListener(e -> stopSimulation());
    }

    // Visualisation panel
    private void createVisPanel() {
        visPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx=0;
        gbc.fill = GridBagConstraints.NONE;
        gbc.anchor = GridBagConstraints.CENTER;
        gbc.insets = new Insets(5, 10, 5, 10);

        visChooseFile = new JButton("Choose input file");
        visChooseFile.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 0;
        visPanel.add(visChooseFile, gbc);

        visRun = new JButton("Run Visualisation");
        visRun.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 1;
        visPanel.add(visRun, gbc);

        visStop = new JButton("Stop Visualisation");
        visStop.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 2;
        visPanel.add(visStop, gbc);

        visStatus = new JLabel("Visualisation not started", SwingConstants.CENTER);
        visStatus.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 3;
        visPanel.add(visStatus, gbc);
/*
        JButton back = new JButton("Back");
        back.setPreferredSize(new Dimension(200,40));
        gbc.gridy = 4;
        visPanel.add(back, gbc);

        back.addActionListener(e -> showPanel("main"));
*/
        visRun.setEnabled(false); // disabled until config is loaded
        visStop.setEnabled(false);

        // Choose file and enable Run button if file is valid
        visChooseFile.addActionListener(e -> {
            visInputFile = chooseFile();
            if (visInputFile != null) {
                visRun.setEnabled(true);
            }
        });

        visRun.addActionListener(e -> startVisualisation());
        visStop.addActionListener(e -> stopVisualisation());
    }

private void createDisplayPanel() {
        displayPanel = new JPanel(new BorderLayout());
        JPanel controls = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.gridx=0;
        gbc.gridy=0;
        gbc.insets = new Insets(5, 5, 5, 5);
        controls.setLayout(new GridBagLayout());

        imageLabel = new JLabel("", SwingConstants.CENTER);

        loadImages = new JButton("Load Results Folder");
        loadImages.setPreferredSize(new Dimension(200,30));
        controls.add(loadImages, gbc);

        prevImage = new JButton("Previous");
        prevImage.setPreferredSize(new Dimension(100,30));
        gbc.gridx=1;
        controls.add(prevImage, gbc);

        nextImage = new JButton("Next");
        nextImage.setPreferredSize(new Dimension(100,30));
        gbc.gridx=2;
        controls.add(nextImage, gbc);
/*
        JButton back = new JButton("Back");
        back.setPreferredSize(new Dimension(100,30));
        gbc.gridx=3;
        controls.add(back, gbc);

        back.addActionListener(e -> showPanel("main"));
*/
        // Image buttons
        loadImages.addActionListener(e -> chooseImageFolder());
        nextImage.addActionListener(e -> {
            if (pngFiles != null && pngFiles.length > 0) {
                currentImageIndex = (currentImageIndex + 1) % pngFiles.length;
                showCurrentImage();
            }
        });
        prevImage.addActionListener(e -> {
            if (pngFiles != null && pngFiles.length > 0) {
                currentImageIndex = (currentImageIndex - 1 + pngFiles.length) % pngFiles.length;
                showCurrentImage();
            }
        });

        displayPanel.add(imageLabel, BorderLayout.CENTER);
        displayPanel.add(controls, BorderLayout.NORTH);
    }

    private void chooseImageFolder() {
        File startPoint = new File(System.getProperty("user.dir"));
        JFileChooser fc = new JFileChooser(startPoint);
        fc.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        if (fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            File folder = fc.getSelectedFile();
            pngFiles = folder.listFiles((dir, name) -> name.toLowerCase().endsWith(".png"));
            if (pngFiles != null && pngFiles.length > 0) {
                currentImageIndex = 0;
                showCurrentImage();
            } else {
                JOptionPane.showMessageDialog(this, "No PNG files found in this folder.");
            }
        }
    }

    private void showCurrentImage() { // added
        if (pngFiles == null || pngFiles.length == 0) return;
        ImageIcon icon = new ImageIcon(pngFiles[currentImageIndex].getAbsolutePath());
        Image img = icon.getImage();
        //Image img = icon.getImage().getScaledInstance(displayPanel.getWidth(), displayPanel.getHeight(), Image.SCALE_SMOOTH);
        
        int panelWidth = imageLabel.getWidth();
        int panelHeight = imageLabel.getHeight();

        if (panelWidth == 0 || panelHeight == 0) {
            panelWidth = 600; // default width
            panelHeight = 600; // default height
        }

        double widthRatio = (double) panelWidth / img.getWidth(null);
        double heightRatio = (double) panelHeight / img.getHeight(null);
        double scaleFactor = Math.min(widthRatio, heightRatio);

        int newWidth = (int) (img.getWidth(null) * scaleFactor);
        int newHeight = (int) (img.getHeight(null) * scaleFactor);

        Image scaled = img.getScaledInstance(newWidth, newHeight, Image.SCALE_SMOOTH);

        imageLabel.setIcon(new ImageIcon(scaled));
    }

    private void showPanel(String name) {
        CardLayout cl = (CardLayout) getContentPane().getLayout();
        cl.show(getContentPane(), name);
    }

    private File chooseFile() {
        JFileChooser fc = new JFileChooser();
        if (fc.showOpenDialog(this) == JFileChooser.APPROVE_OPTION) {
            return fc.getSelectedFile();
        }
        return null;
    }

    private SimConfig readConfig(File file) {
        try (BufferedReader br = new BufferedReader(new FileReader(file))) {
            String motilityString = br.readLine();
            String SEMString = br.readLine();
            String DEMString = br.readLine();
            String maxParticlesString = br.readLine();
            String stepsString = br.readLine();

            if (motilityString == null || SEMString == null || DEMString == null || maxParticlesString == null || stepsString == null) {
                JOptionPane.showMessageDialog(this, "Config file must have 5 values");
                return null;
            }

            String[] motilityParts = motilityString.split(":");
            String[] SEMParts = SEMString.split(":");
            String[] DEMParts = DEMString.split(":");
            String[] maxParticlesParts = maxParticlesString.split(":");
            String[] stepsParts = stepsString.split(":");

            double v1 = Double.parseDouble(motilityParts[1].trim());
            double v2 = Double.parseDouble(SEMParts[1].trim());
            double v3 = Double.parseDouble(DEMParts[1].trim());
            int v4 = Integer.parseInt(maxParticlesParts[1].trim());
            int v5 = Integer.parseInt(stepsParts[1].trim());

            return new SimConfig(v1, v2, v3, v4, v5);
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "Error reading config file");
            return null;
        }
    }

    // Simulation logic
    private void startSimulation() {
        if (simConfigFile == null) return;

        SimConfig config = readConfig(simConfigFile);
        if (config == null) return;

        simRun.setEnabled(false);
        simStop.setEnabled(true);
        simStatus.setText("Simulation in progress...");

        simStopFlag = new AtomicBoolean(false);
        simStopSupplier = simStopFlag::get;

        Thread simThread = new Thread(() -> {
            try {
                SimulationConfig simConfig = new SimulationConfig();
                simConfig.setMotility(config.v1);
                simConfig.setBacteriaToBacteriaElasticModulus(config.v2);
                simConfig.setEPSToEPSElasticModulus(config.v2);
                simConfig.setBacteriaToEPSElasticModulus(config.v3);
                simConfig.setMaxParticles(config.v4);
                simConfig.setSimulationTime(config.v5);
                MultiThreadedSimulation sim = new MultiThreadedSimulation(simConfig);

                sim.runSimulation(simStopSupplier);

            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> JOptionPane.showMessageDialog(this, "Simulation error: " + e.getMessage()));
            } finally {
                SwingUtilities.invokeLater(() -> {
                    simStatus.setText("Simulation complete");
                    simRun.setEnabled(true);
                    simStop.setEnabled(false);
                });
            }
        });

        simThread.start();
    }

    private void stopSimulation() {
        if (simStopFlag != null) {
            simStopFlag.set(true);
            simStatus.setText("Stopping simulation...");
        }
    }

    // Visualisation logic
    private void startVisualisation() {
        if (visInputFile == null) return;

        visRun.setEnabled(false);
        visStop.setEnabled(true);
        visStatus.setText("Visualisation Running");
        //
        Thread visThread = new Thread(() -> {
            try {
                //
                String pythonExe = "python3"; 
                String script = "structuralPrototype/src/main/java/fasterVideoMaker.py";
                ProcessBuilder pb = new ProcessBuilder(pythonExe, script, visInputFile.getAbsolutePath());
                pb.redirectErrorStream(true);
                visVideoProcess = pb.start();

                readProcessOutput(visVideoProcess);

                String imageScript = "structuralPrototype/src/main/java/ImageGenAndClustering.py";
                ProcessBuilder pb2 = new ProcessBuilder(pythonExe, imageScript, visInputFile.getAbsolutePath());
                pb2.redirectErrorStream(true);
                visImageProcess = pb2.start();

                readProcessOutput(visImageProcess);

                visStatus.setText("Visualisation in progress...");

                new Thread(() -> {
                    try {
                        visVideoProcess.waitFor();
                        visImageProcess.waitFor();
                        SwingUtilities.invokeLater(() -> {
                            System.out.println("Visualisation complete");
                            visStatus.setText("Visualisation complete");
                            visRun.setEnabled(true);
                            visStop.setEnabled(false);
                        });
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }).start();
                //
            } catch (Exception e) {
                SwingUtilities.invokeLater(() -> JOptionPane.showMessageDialog(this, "Visualisation error: " + e.getMessage()));
            }
        });

        visThread.start();
    }

    private void readProcessOutput(Process process) {
        new Thread(() -> {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String finalLine = line;
                    System.out.println(finalLine);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();

        new Thread(() -> {
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(process.getErrorStream()))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    String finalLine = line;
                    System.err.println(finalLine);
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();
    }

    private void stopVisualisation() {
        visStatus.setText("Visualisation stopped");
        visRun.setEnabled(true);
        visStop.setEnabled(false);
        if (visImageProcess != null && visImageProcess.isAlive()) {
            visImageProcess.destroyForcibly();
        }
        if (visVideoProcess != null && visVideoProcess.isAlive()) {
            visVideoProcess.destroyForcibly();
        }
    }

    private static class SimConfig {
        double v1, v2, v3;
        int v4, v5;
        SimConfig(double v1, double v2, double v3, int v4, int v5) { this.v1 = v1; this.v2 = v2; this.v3 = v3; this.v4 = v4; this.v5 = v5; }
        public String toString() { return v1 + ", " + v2 + ", " + v3 + ", " + v4 + ", " + v5; }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            UI app = new UI();
            app.setVisible(true);
            app.showPanel("main");
        });
    }
}
