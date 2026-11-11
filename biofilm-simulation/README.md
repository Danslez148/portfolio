# Biofilm Growth Simulation (Capstone)

An agent-based simulation of how bacterial biofilms grow. Bacteria move, divide and secrete EPS (extracellular polymeric substance) particles in a 2D environment with a diffusing nutrient field. The results are analysed and visualised as images, video and clusters.

**Context:** CSC3003S Capstone Project, UCT (2025). Team of 3. We ran it as a full software engineering project: scope, risk and role documents, use-case narratives, a test strategy, a Gantt plan, weekly progress reports, and two prototypes. This is the final code from our team GitLab repository. The team's original run notes are in `README_original.md`.

## Structure
| Folder | Contents |
|---|---|
| `functionalPrototype/` | First working model: splitting bacteria with a config file, plus a Python script that renders the run as a GIF (`bin/cell_movement.gif`) |
| `structuralPrototype/` | Final architecture (Maven project). A `MultiThreadedSimulation` runs force-calculation, particle-update and event-check tasks on a thread pool (`ExecutorService`). A `SpatialGrid` handles fast neighbour lookups. Includes a Swing `UI` and JUnit tests for the core classes |
| `structuralPrototype/src/main/java/*.py` | Post-processing in Python: frame/video generation and DBSCAN clustering of bacterial colonies (pandas, matplotlib, scikit-learn) |

## Tech
Java 11+, Maven, JUnit, `java.util.concurrent`, Swing · Python (pandas, matplotlib, scikit-learn)

## Run
```bash
make                                   # compiles the structural prototype into bin/
java -cp bin UI                        # launch the simulation UI
cd structuralPrototype && mvn test     # run the unit tests
```
Simulation parameters (motility, elastic moduli, max particles, run time) are set in `Config.txt`.
