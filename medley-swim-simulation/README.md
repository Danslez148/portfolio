# Medley Relay Swim Simulation (Concurrency)

A Swing animation of 10 teams swimming a medley relay. Every swimmer is a thread. The starting framework had race conditions and broke the relay rules. My job was to make it correct and thread-safe: swimmers enter in order, wait for their teammate before diving in, the race starts only when everyone is ready, and finish positions are recorded correctly.

**Context:** CSC2002S Parallel & Concurrent Programming, UCT (2024). Individual. Starter framework by the course convenor (M. M. Kuttel).

## Concurrency techniques
- `CountDownLatch` arrays to order swimmers within a team and to start the race
- `synchronized` monitors on grid blocks to stop two swimmers occupying the same cell
- `AtomicInteger` and a synchronised `FinishCounter` for race results

## Run
```bash
make
java -cp bin medleySimulation.MedleySimulation
```
`gitlog.txt` is the commit history from development.
