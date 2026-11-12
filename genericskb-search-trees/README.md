# GenericsKB Search: Array vs BST vs AVL Tree

Loads the GenericsKB knowledge base (50,000 "term → statement + confidence score" entries) and supports fast lookup and update of statements. I implemented the same app on three data structures and compared their performance experimentally.

**Context:** CSC2001F Data Structures, UCT (2024). Individual, two assignments.

| Folder | Contents |
|---|---|
| `part1-array-and-bst/` | Assignment 1: array-backed and binary-search-tree versions with a Swing GUI (NetBeans project) |
| `part2-avl-tree/` | Assignment 2: self-balancing AVL tree, an experiment run with `GenericsKB-queries.txt`, and a write-up in `Report.pdf` |

## Run (AVL version)
```bash
cd part2-avl-tree
make          # compiles and runs, writing results to output.txt
```

## ⚠️ Known issues (code kept as submitted)
- **`make` in `part2-avl-tree/` fails.** The class is in package `genericskbavlapp`, but the Makefile compiles into `src/` and runs `java GenericsKbAVLApp` without that package or classpath, so Java can't find the main class. The failed run also overwrites `output.txt` with an empty file. The code also opens `GenericsKb.txt` while the file is named `GenericsKB.txt`, which only works on case-insensitive file systems (Windows). Working commands from `part2-avl-tree/`: `javac -d bin src/*.java` then `java -cp bin genericskbavlapp.GenericsKbAVLApp > output.txt` (on Linux or macOS, copy `GenericsKB.txt` to `GenericsKb.txt` first).
- **The array version in `part1-array-and-bst/` doesn't compile.** `GenericsKbArrayApp.java` still calls two GUI event handlers (`txtFileNameActionPerformed`, `txtStatementActionPerformed`) whose definitions are commented out near the end of the file. The BST version (`GenericsKbBSTApp`) compiles and runs.
