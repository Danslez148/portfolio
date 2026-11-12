# Procedural Dungeon Generator (Answer Set Programming)

Generates random, always-solvable dungeon levels with **Answer Set Programming** (Clingo) and plays them in a terminal roguelike.

**Context:** UCT Honours (2026).

- `level1region.lp`: lays out a 6×6 grid of regions with an exact number of rooms, three named special rooms (Tomb of Fear, Chamber of Death, Pit of Flame) and corridors, with constraints that guarantee the exit can be reached from the start
- `room_tiles.lp`: fills each region with 9×9 tiles (walls, floors, doors, keys, chests)
- `generator.py`: runs Clingo from Python with a random seed and turns the answer set into a tile map
- `game.py`: a playable `curses` front-end (`@` player, `>` exit, `k` key, `c` chest)

## Run
```bash
pip install clingo
python game.py
```
On Windows, Python doesn't include `curses`, so also run `pip install windows-curses`.

Generating a level takes about 10 seconds. Move with the arrow keys and press `q` to quit.
