# Biofilm Growth Simulation (Capstone)

An agent-based simulation of how bacterial biofilms grow. Individual bacteria move, divide and secrete EPS (extracellular polymeric substance) particles in a 2D environment with a diffusing nutrient field. The output is visualised as an animation (see `Prototype_0/bin/cell_movement.gif`).

**Context:** CSC3003S Capstone Project, UCT (2025). Team of 3 (Sarah-Jane Marais, Ethan, and me). We ran it as a full software engineering project: scope, risk and role documents, use-case narratives, a test strategy, a Gantt plan, weekly progress reports, and two prototypes.

## Tech
- Java (no external libraries), multithreaded `SimulationWorker`s
- Spatial grid partitioning (`SpatialGrid`, `GridCell`) for fast neighbour and collision lookups
- Python (`GifMaker.py`) to turn simulation frames into a GIF

## Structure
| Folder | Contents |
|---|---|
| `Prototype_0/` | First working prototype: particle motion, splitting bacteria, nutrient field, data output |
| `Prototype_1/` | Redesigned architecture from our class diagram (`BIOFILM_DIAGRAMS-New Class diagram.jpg`), with config, forces, analyser and UI classes |
| `latest-src/` | Latest working copy of the Prototype 1 implementation |

## Run
```bash
cd Prototype_0/src
javac *.java
java SimpleBacteriaSimulation      # or SplittingBacteriaSimulation
```

The team's main repository was hosted on the UCT Computer Science GitLab.
