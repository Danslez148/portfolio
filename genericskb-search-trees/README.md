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
