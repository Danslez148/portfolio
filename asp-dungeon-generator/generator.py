import clingo
import random

def generate():
    seed = random.randint(1,99999)

    ctl = clingo.Control(["--models=1", "--rand-freq=0.5", f"--seed={seed}"])
    ctl.load("level1region.lp")
    ctl.load("room_tiles.lp")
    ctl.ground([("base", [])])

    tiles = {}
    regions = {}

    def on_model(model):
        for atom in model.symbols(shown=True):
            name = atom.name
            args = atom.arguments

            if name == "tile_obj":
                rx, ry, tx, ty, obj = args
                rx, ry = rx.number, ry.number
                tx, ty = tx.number, ty.number
                obj = str(obj)
                wx = rx * 9 + tx
                wy = ry * 9 + ty
                if obj in ("floor", "door"):
                    tiles[(wx, wy)] = "floor"
                elif obj == "wall":
                    tiles[(wx, wy)] = "wall"

            elif name == "start":
                x, y = args
                regions["start"] = (x.number, y.number)

            elif name == "end":
                x, y = args
                regions["end"] = (x.number, y.number)

    ctl.solve(on_model=on_model)

    if "start" in regions:
        rx, ry = regions["start"]
        tiles[(rx*9+4, ry*9+4)] = "start"
    if "end" in regions:
        rx, ry = regions["end"]
        tiles[(rx*9+4, ry*9+4)] = "exit"

    return tiles, regions

if __name__ == "__main__":
    grid, regions = generate()
    for y in range(54):
        row = ""
        for x in range(54):
            tile = grid.get((x, y), "?")
            ch = {"wall":"#","floor":".","start":"@","exit":">"}.get(tile,"?")
            row += ch
        print(row)
