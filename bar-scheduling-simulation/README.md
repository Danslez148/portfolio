# Bar Scheduling Simulation (CPU Scheduling)

A multithreaded Java simulation of a bar. Patrons (threads) place drink orders with a barman, who serves them under different CPU-scheduling policies. I added instrumentation to measure how each policy performs, then ran and analysed the experiments.

**Context:** CSC3002F Operating Systems assignment, UCT (2025). Individual. Starter framework (including the three schedulers) by the course convenor, M. M. Kuttel.

**My work:** measuring waiting time, turnaround time, barman CPU utilisation and throughput (with a sliding window), writing the results to CSV for analysis, and a report comparing the algorithms.

## Scheduling algorithms
- `0`: First-Come-First-Served (`LinkedBlockingQueue`)
- `1`: non-preemptive Shortest-Job-First (`PriorityBlockingQueue` ordered by execution time)
- `2`: Round-Robin with a configurable time quantum

Concurrency: `CountDownLatch` for a synchronised start, blocking queues between patron and barman threads.

## Run
```bash
make                      # compile
java -cp bin barScheduling.SchedulingSimulation <patrons> <alg> <contextSwitch> <quantum> <seed>
# e.g. 50 patrons, Round-Robin, quantum 100ms:
java -cp bin barScheduling.SchedulingSimulation 50 2 5 100 1
```
`test.sh` runs batches of experiments. `gitlogg.txt` is the commit history from development.
