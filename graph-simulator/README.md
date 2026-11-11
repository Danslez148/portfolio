# Taxi & Shop Dispatch Simulator (Graph Algorithms)

Reads a weighted directed road network and lists of taxi, shop and client locations. For each client it finds the nearest taxi(s) and shop(s) with Dijkstra's shortest-path algorithm, prints the routes, and handles ties and unreachable nodes.

**Context:** CSC2001F Data Structures, UCT (2024). Individual.

**Tech:** Java, adjacency-list graph, `PriorityQueue`-based Dijkstra.

## Run
```bash
cd src
javac *.java
java SimulatorOne < input.txt
```
Input format: number of nodes, then one line per node (`node dest weight dest weight …`), then the shop count and nodes, then the client count and nodes.
