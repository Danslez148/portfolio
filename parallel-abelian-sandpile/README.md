# Parallel Abelian Sandpile

Simulates the Abelian sandpile cellular automaton: grains topple to their neighbours until the grid is stable. The output is an image of the final pattern. I wrote a parallel version with Java's Fork/Join framework and benchmarked it against the serial version on grids up to 1024×1024.

**Context:** CSC2002S Parallel & Concurrent Programming, UCT (2024). Individual. Serial starter code by the course convenor.

## Structure
| Folder | Contents |
|---|---|
| `serial/` | Reference serial implementation |
| `parallel/` | My Fork/Join implementation (`ParallelGridTask extends RecursiveTask`), which splits the grid recursively below a sequential cutoff |
| `tools/GridMaker/` | Small utility I wrote to generate large test grids (CSV) |
| `SpeedupResults.txt` | Timing results across grid sizes, cutoffs and machines |

## Run
```bash
cd parallel
make
java -cp bin parallelAbelianSandpile.AutomatonSimulation input/512_by_512_All_4.csv output/512.png
```
