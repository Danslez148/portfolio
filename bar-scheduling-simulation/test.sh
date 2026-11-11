#!/bin/bash

q_values=(10 50 100)

repetitions=3

for q in "${q_values[@]}"; do
    for ((i=1; i<=repetitions; i++)); do
        make run ARGS="$q 2 4 80 42"
    done
done