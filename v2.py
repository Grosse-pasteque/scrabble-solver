import re
import json
from time import time
from colorama import init, Fore, Back
init()

# https://github.com/dolph/dictionary/blob/master/ospd.txt
# /usr/share/dict/words
start = time()
with open('cache/words-letters-count-by-points-optimized.json') as file:
    WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED = json.load(file)

print('LOAD TIMES:', time() - start)

ABC = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
WORD_MAX_LENGTH = 15
WORD_MIN_LENGTH = 2
MODES = {
    'DELETE':  Back.RED,
    'SKIP':    Back.WHITE,
    'PATTERN': Back.GREEN,
    'DEBUG':   Back.YELLOW,
}

def ensure_grid_buffer(x, y, grid): # TODO: optimize -> wastes 0.026
    width = len(grid[0]) if grid else 0
    height = len(grid)
    while y < WORD_MAX_LENGTH:
        grid.insert(0, [None] * width)
        y += 1
    while y >= len(grid) - WORD_MAX_LENGTH:
        grid.append([None] * width)
    height = len(grid)
    while x < WORD_MAX_LENGTH:
        for row in grid:
            row.insert(0, None)
        x += 1
    while x >= len(grid[0]) - WORD_MAX_LENGTH:
        for row in grid:
            row.append(None)
    return x, y


class Slot:
    def __init__(self):
        self.value = None
        self.is_blocked = False
        self.is_valid = False # TODO: instances

    def block(self):
        self.is_blocked = True
        self.is_valid = False

    def update(self, letter: str):
        if not self.is_blocked:
            if self.is_valid:
                self.is_blocked = True
                return False
            self.is_valid = True
            return True
        return False


# valid for a vertical/horizontal word
positions = (set(), set())

HORIZONTAL = 0
VERTICAL = 1
orientations = ((1, 0), (0, 1))

WALL = '%'

def place(x, y, word, deck, grid, orientation):
    # x, y = ensure_grid_buffer(x, y, grid)
    ix, iy = orientations[orientation]
    a_valid = positions[orientation]
    b_valid = positions[(orientation + 1) % 2]
    block_next = False
    grid[y - iy][x - ix] = WALL
    for letter in word:
        if (x, y) in b_valid:
            b_valid.remove((x, y))
            try: b_valid.remove((x + iy, y + ix))
            except: pass
            try: b_valid.remove((x - iy, y - ix))
            except: pass
            try: a_valid.remove((x - iy, y - ix))
            except: pass
            block_next = True
        else:
            grid[y][x] = letter
            if block_next:
                block_next = False
            else:
                a_valid.add((x, y))
        x += ix
        y += iy
        deck[letter] -= 1
        if deck[letter] < 0:
            raise ValueError(
                f"There are no {letter!r} remaining")
    grid[y][x] = WALL
    # ensure_grid_buffer(x, y, grid)

def solve(deck, debug=False):
    global WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED
    deck = { letter: deck.count(letter) for letter in ABC }
    remaining = sum(deck.values())
    rotate_mode = 0
    if remaining < WORD_MIN_LENGTH:
        return # impossible

    grid = [[None] * 101 for _ in range(101)]

    if debug:
        startup = time()
        removed = len(WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED)

    WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED = list(filter(
        lambda m: all(deck[l] >= n for l, n in m[1]),
        WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED.items()
    ))

    if debug:
        total = round(time() - startup, 5)
        mode = Back if total > 1 else Fore
        removed -= len(WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED)
        print(f"[{Back.RED}DELETE{Back.RESET}] removed {Fore.CYAN}{removed}{Fore.RESET} words in {mode.RED}{total}{mode.RESET}s")

    word, _ = WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED[0]
    grid[0][50] = grid[100][50] = 'O'
    place(50, 50, word, deck, grid, orientation=HORIZONTAL)
    print(positions)

    # find vertical
    patterns = set()
    ix, iy = orientations[VERTICAL]
    parsed = set()
    for x, y in positions[HORIZONTAL]:
        if (x, y) in parsed:
            continue
        pattern = ''
        xx, yy = x, y
        while yy >= 0 and xx >= 0:
            current = grid[yy][xx]
            if current == WALL:
                break
            if current:
                parsed.add((xx, yy))
            else:
                current = '.'
            pattern = current + pattern
            xx -= ix
            yy -= iy
        xx, yy = x + ix, y + iy
        while yy < len(grid) and xx < len(grid[yy]):
            current = grid[yy][xx]
            if current == WALL:
                break
            if current:
                parsed.add((xx, yy))
            else:
                current = '.'
            pattern += current
            xx += ix
            yy += iy
        print(pattern)
    return grid

#                |-------------------|-------------------|
#                | NOT GROUPED       | GROUPED           |
# |--------------|-------------------|-------------------|
# | NOT COMPILED | 7.460646390914917 | 7.555405378341675 |
# |--------------|-------------------|-------------------|
# | COMPILED     | 4.473367929458618 | 4.615920543670654 |
# |--------------|-------------------|-------------------|

# O.................................................B.................................................O


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Deobfuscates useless javascript forswitches.")
    parser.add_argument("letters", type=str, help="The available letters.")
    parser.add_argument("-v", "--version", action="version", version="0.0.2", help="Show script version and exit.")
    parser.add_argument("-d", "--debug", action="store_true", help="Starts the script in debug mode.")
    args = parser.parse_args()

    import cProfile
    with cProfile.Profile() as pr:
        grid = solve(args.letters, debug=args.debug)
        pr.dump_stats('stats.prof')

    for line in grid:
        print(''.join(' ' if not c else Fore.LIGHTGREEN_EX + c + Fore.RESET for c in line))


if __name__ == '__main__':
    main()
