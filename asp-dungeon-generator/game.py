import curses
from generator import generate

TILES = {
    "wall":  ('#', 1),
    "floor": ('.', 2),
    "start": ('@', 3),
    "exit":  ('>', 4),
    "key":   ('k', 5),
    "chest": ('c', 6),
}

def make_fake_grid():
    grid = {}
    for x in range(60):
        for y in range(60):
            grid[(x, y)] = "wall"
    
    # room 1
    for x in range(2, 8):
        for y in range(2, 8):
            grid[(x, y)] = "floor"
    
    # room 2
    for x in range(12, 18):
        for y in range(2, 8):
            grid[(x, y)] = "floor"
    
    # corridor
    for x in range(8, 12):
        grid[(x, 5)] = "floor"
    
    # entities
    grid[(3, 3)]  = "start"
    grid[(15, 5)] = "exit"
    grid[(5, 5)]  = "key"
    grid[(14, 3)] = "chest"
    
    return grid

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    
    curses.init_pair(1, curses.COLOR_WHITE,  curses.COLOR_BLACK)  # wall
    curses.init_pair(2, curses.COLOR_WHITE,  curses.COLOR_BLACK)  # floor
    curses.init_pair(3, curses.COLOR_GREEN,  curses.COLOR_BLACK)  # start
    curses.init_pair(4, curses.COLOR_RED,    curses.COLOR_BLACK)  # exit
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # key
    curses.init_pair(6, curses.COLOR_CYAN,   curses.COLOR_BLACK)  # chest
    curses.init_pair(7, curses.COLOR_GREEN,  curses.COLOR_BLACK)  # player

    grid, regions_data = generate()

    player_x, player_y = next(
        (x, y) for (x, y), t in grid.items() if t == "start"
    )

    MOVES = {
        curses.KEY_UP:    (0, -1),
        curses.KEY_DOWN:  (0,  1),
        curses.KEY_LEFT:  (-1, 0),
        curses.KEY_RIGHT: (1,  0),
        ord('w'): (0, -1),
        ord('s'): (0,  1),
        ord('a'): (-1, 0),
        ord('d'): (1,  0),
    }

    def draw():
        actual_h, actual_w = stdscr.getmaxyx()
        stdscr.clear()

        VP_H, VP_W = 15, 15

        # total frame size
        PANEL_W = 22
        FRAME_W = VP_W + PANEL_W + 3   # borders
        FRAME_H = VP_H + 4             # title + bottom bar + borders

        # centre the frame
        start_y = max(0, (actual_h - FRAME_H) // 2)
        start_x = max(0, (actual_w - FRAME_W) // 2)

        frame = curses.color_pair(8)
        title_pair = curses.color_pair(9)

        # --- title bar ---
        title = "D U N G E O N   C R A W L"
        stdscr.addstr(start_y, start_x,
            "╔" + "═" * (FRAME_W - 2) + "╗", frame)
        stdscr.addstr(start_y + 1, start_x, "║", frame)
        stdscr.addstr(start_y + 1, start_x + 1,
            title.center(FRAME_W - 2), title_pair)
        stdscr.addstr(start_y + 1, start_x + FRAME_W - 1, "║", frame)

        # --- divider below title ---
        stdscr.addstr(start_y + 2, start_x,
            "╠" + "═" * (VP_W + 1) + "╦" + "═" * (PANEL_W) + "╣", frame)

        # --- viewport rows ---
        cam_x = player_x - VP_W // 2
        cam_y = player_y - VP_H // 2

        for sy in range(VP_H):
            row_y = start_y + 3 + sy
            stdscr.addstr(row_y, start_x, "║", frame)

            for sx in range(VP_W):
                wx = cam_x + sx
                wy = cam_y + sy
                is_player = (wx == player_x and wy == player_y)

                if is_player:
                    stdscr.addch(row_y, start_x + 1 + sx,
                        '&', curses.color_pair(7))
                else:
                    tile = grid.get((wx, wy), "wall")
                    ch, pair = TILES[tile]
                    stdscr.addch(row_y, start_x + 1 + sx,
                        ch, curses.color_pair(pair))

            # divider between viewport and panel
            stdscr.addstr(row_y, start_x + VP_W + 1, "║", frame)

            # --- stats panel content ---
            panel_x = start_x + VP_W + 2
            special_name = "reach the exit"

            panel_lines = [
                "",
                f"  keys:   {inventory['keys']}",
                f"  chests: {inventory['chests']}",
                f"  floor:  {floor_number}",
                "",
                f"  {player_x},{player_y}",
                "",
                "  objective:",
                f"  {special_name}",
                "",
                "  wasd / arrows",
                "  n - next floor",
                "  q - quit",
                "",
                "",
            ]
            if sy < len(panel_lines):
                line = panel_lines[sy][:PANEL_W - 1]
                stdscr.addstr(row_y, panel_x,
                    line.ljust(PANEL_W - 1),
                    curses.color_pair(2))

            stdscr.addstr(row_y, start_x + FRAME_W - 1, "║", frame)

        stdscr.addstr(start_y + 3 + VP_H, start_x,
            "╠" + "═" * (FRAME_W - 2) + "╣", frame)

        msg_y = start_y + 4 + VP_H
        stdscr.addstr(msg_y, start_x, "║", frame)
        stdscr.addstr(msg_y, start_x + 1,
            f" {message}"[:FRAME_W - 2].ljust(FRAME_W - 2),
            curses.color_pair(2))
        stdscr.addstr(msg_y, start_x + FRAME_W - 1, "║", frame)

        stdscr.addstr(start_y + 5 + VP_H, start_x,
            "╚" + "═" * (FRAME_W - 2) + "╝", frame)

        stdscr.refresh()

    floor_number = 1
    regions_data = {}
    inventory = {"keys": 0, "chests": 0}
    message = "find key -> open chest -> reach exit"
    at_exit = False
    while True:
        draw()
        key = stdscr.getch()

        if key == ord('q'):
            break

        if key == ord('n'):
            current_tile = grid.get((player_x, player_y), "wall")
            if current_tile == "exit" or at_exit:
                floor_number += 1
                message = f"descending to floor {floor_number}..."
                draw()
                stdscr.refresh()
                grid, regions_data = generate()
                player_x, player_y = next(
                    (x, y) for (x, y), t in grid.items() if t == "start"
                )
                inventory = {"keys": 0, "chests": 0}
                at_exit = False
                message = "find the key, open the chest, reach the exit."


        if key in MOVES and not at_exit:
            dx, dy = MOVES[key]
            nx, ny = player_x + dx, player_y + dy
            tile = grid.get((nx, ny), "wall")
            
            if tile != "wall":
                player_x, player_y = nx, ny
                
                if tile == "key":
                    inventory["keys"] += 1
                    grid[(nx, ny)] = "floor"
                    message = "you picked up a key."
                elif tile == "chest":
                    if inventory["keys"] > 0:
                        inventory["chests"] += 1
                        inventory["keys"] -= 1
                        grid[(nx, ny)] = "floor"
                        message = "you opened the chest!"
                    else:
                        message = "you need a key to open this chest."
                elif tile == "exit":
                    at_exit = True
                    message = "you found the exit! press n for next floor, q to quit."

curses.wrapper(main)
