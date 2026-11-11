# Daniel Schlesinger — Software Portfolio

BSc (Hons) Computer Science student at the University of Cape Town (BSc in Mathematics & Computer Science, graduated with distinction in both).
This repository collects the software I've built at university and on my own, in one place. Each folder has its own README covering what the project does, the tech used and how to run it.

The code in each project is kept as it was submitted or last worked on. I've only added READMEs and left out build output (`.class`, `bin/`, IDE metadata), zipped submissions and private config files.

## Featured projects

| Project | What it is | Tech | Year |
|---|---|---|---|
| [honours-project-eccrs](honours-project-eccrs/) | **Honours research project (CSC4002W).** Verifies an explainable rule-based classifier (ECCRS, Most-Specific-Wins) against Rational Closure from non-monotonic logic: checks the theorem's conditions, translates rulesets into KLM knowledge bases, and implements BaseRank, RC entailment and a DPLL SAT solver from scratch. RC and MSW agree on every instance and pattern across three real datasets. 2.8k lines plus 2.4k lines of pytest tests. | Python, logic, pytest | 2026 |
| [wireguard-chat](wireguard-chat/) | Encrypted multi-user chat client with my own implementation of the WireGuard / Noise IK handshake. Team of 3; I built the async UI controller and message stores. | Python, asyncio, PyQt6, CI linting | 2026 |
| [IntelAfrica / AfriMarket prototype](https://github.com/Danslez148/NVP_prototype) ↗ | Market-search and trading dashboard for African commerce, with an interactive D3 map. [Live demo](https://intelafrica-eight.vercel.app) | React, Vite, D3 | 2026 |
| [house-of-gains-unity](house-of-gains-unity/) | Casino-themed mini-games (Higher/Lower, Roulette) and an in-game economy for a Unity game. Team of 4; my scripts. | C#, Unity | 2026 |
| [asp-dungeon-generator](asp-dungeon-generator/) | Procedural, always-solvable dungeon levels generated with Answer Set Programming, played in a terminal roguelike. | Clingo (ASP), Python, curses | 2026 |
| [opengl-solar-system](opengl-solar-system/) | Animated, textured Sun–Earth–Moon scene with GLSL shaders and lighting. | Python, OpenGL, GLSL | 2026 |
| [biofilm-simulation](biofilm-simulation/) | Third-year capstone: multithreaded agent-based simulation of bacterial biofilm growth, with JUnit tests and Python cluster analysis. Team of 3. | Java, Maven, Python | 2025 |
| [p2p-file-sharing](p2p-file-sharing/) | BitTorrent-style peer-to-peer file sharing with a tracker, seeders and leechers, plus a GUI. Team of 3. | Python, TCP/UDP sockets | 2025 |
| [bar-scheduling-simulation](bar-scheduling-simulation/) | Multithreaded simulation of FCFS, SJF and Round-Robin CPU scheduling. I built the performance measurement and analysis. | Java concurrency | 2025 |
| [parallel-abelian-sandpile](parallel-abelian-sandpile/) | Serial and Fork/Join parallel versions of a sandpile cellular automaton, with speed-up benchmarks. | Java, Fork/Join | 2024 |
| [medley-swim-simulation](medley-swim-simulation/) | Concurrent swimming-relay simulation, made thread-safe with latches, synchronisation and atomics. | Java, Swing, concurrency | 2024 |

## Data structures, algorithms and systems

| Project | What it is | Tech | Year |
|---|---|---|---|
| [genericskb-search-trees](genericskb-search-trees/) | Knowledge-base search over 50,000 statements using an array, a BST and an AVL tree, with a performance report. | Java | 2024 |
| [graph-simulator](graph-simulator/) | Delivery dispatch simulator that uses Dijkstra's shortest paths to match clients with the nearest taxis and shops. | Java | 2024 |
| [sql-classicmodels](sql-classicmodels/) | 20 SQL queries (joins, aggregation, sub-queries) on the ClassicModels sample database. | SQL / MySQL | 2024 |
| [mips-assembly](mips-assembly/) | MIPS assembly programs, including a WAV file header parser. | MIPS | 2024 |
| [compilers-ply-bla](compilers-ply-bla/) | Compiler front-end for a small language: lexer, parser (AST), evaluator and error reporting. | Python, PLY | 2026 |
| [smaller-exercises](smaller-exercises/) | Earlier coursework and practice: intro Python, OOP in Java, algorithm practice, LRU page replacement. | Python, Java | 2023–2025 |

## Skills shown
- **Languages:** Java, Python, SQL, Clingo (ASP)
- **Concurrency and parallelism:** threads, Fork/Join, latches, monitors
- **Networking and security:** sockets (TCP/UDP), custom protocol design, WireGuard/Noise cryptography
- **Logic and AI:** non-monotonic reasoning (KLM, Rational Closure), SAT solving, answer set programming
- **Engineering practice:** Git and GitHub team workflows (branches, PRs), unit tests (pytest, JUnit), Makefiles

**Built with AI assistance:** some projects use technologies I worked in mainly through AI-assisted development (Claude) rather than in depth: C#/Unity, JavaScript/React, GLSL/OpenGL, MIPS assembly, asyncio/PyQt6, Maven and CI linting. I can explain how that code works, but I don't list these as core skills.

## Contact
Cape Town, South Africa · [GitHub](https://github.com/Danslez148)
