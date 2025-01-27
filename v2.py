import re
import json
from time import time
from colorama import init, Fore, Back
import cProfile
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


# valid for a vertical/horizontal word
positions = (set(), set())

HORIZONTAL = 0
VERTICAL = 1
orientations = ((1, 0), (0, 1))

WALL = '%'

def place(x, y, word, deck, grid, *, orientation, debug):
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
    if debug:
        print(f"[{Fore.GREEN}PLACED{Fore.RESET}]    placing '{Fore.LIGHTGREEN_EX}{word}{Fore.RESET}'")
        print(f"[{Fore.LIGHTYELLOW_EX}REMAIN{Fore.RESET}]    {Fore.MAGENTA}{sum(deck.values())}{Fore.RESET} letters remaining")

    # ensure_grid_buffer(x, y, grid)

def get_subblocks(offset, pattern):
    current = Block(offset, [])
    subpatterns = [current]
    placed_count = 0
    for i, part in enumerate(pattern):
        if part.__class__ == int:
            if placed_count and i < len(pattern) - 1:
                placed_count = 0
                subpatterns.append(Block(offset + 1, [part]))
            offset += part
        else:
            offset += 1
            if not placed_count and len(part) == 1:
                placed_count += 1
        current.pattern.append(part)
        last = subpatterns[-1]
        if current != last:
            current = last
    extended = []
    for i, a in enumerate(subpatterns):
        combination = a
        inner_extended = []
        for b in subpatterns[i + 1:]:
            combination = combination + b
            inner_extended.append(combination)
        for j, block in enumerate(inner_extended):
            if j < len(inner_extended) - 1:
                block.pattern[-1] -= 1
            if i:
                block.pattern[0] -= 1
            block.prepare()
        extended += inner_extended
    for i, block in enumerate(subpatterns):
        if i < len(subpatterns) - 1:
            block.pattern[-1] -= 1
        if i:
            block.pattern[0] -= 1
        block.prepare()
    return subpatterns + extended


class Block:
    def __init__(self, offset, pattern):
        self.offset = offset
        self.pattern = pattern
        self.indexes = {}
        self.placed_count = { letter: 0 for letter in ABC }
        self.placed = set()
        self.is_fixed = True
        self.min_length = 0
        self.start = 0
        self.length = 0

    def prepare(self):
        offset = 0
        start = None
        for letter in self.pattern:
            if letter.__class__ == int:
                offset += letter
            else:
                offset += 1
                if start is None:
                    start = offset
                self.indexes[offset - start] = letter
                self.placed_count[letter] += 1
                self.placed.add(letter)
        self.start = start
        self.length = offset

    def __repr__(self):
        return f"<{self.offset} {self.pattern}>"

    def __add__(self, other):
        return Block(self.offset, self.pattern[:-1] + other.pattern)

    def compile(self):
        self.length = sum(letter if letter.__class__ == int else 1 for letter in self.pattern)
        self.min_length = self.length
        try:
            self.min_length -= self.pattern[-1]
        except:
            self.min_length -= 1
        try:
            self.min_length -= self.pattern[0]
        except:
            self.min_length -= 1
        self.pattern = re.compile(''.join(
            ('.*' if offset > 13 else f".{{{'' if self.is_fixed or i and i != len(self.pattern) - 1 else ','}{offset}}}") if offset.__class__ == int else offset
            for i, offset in enumerate(self.pattern)
        ))


MAX_LETTERS_COUNT = {
    'A': 5,
    'B': 3,
    'C': 4,
    'D': 3,
    'E': 6,
    'F': 4,
    'G': 3,
    'H': 3,
    'I': 6,
    'J': 2,
    'K': 3,
    'L': 4,
    'M': 4,
    'N': 5,
    'O': 5,
    'P': 3,
    'Q': 2,
    'R': 4,
    'S': 7,
    'T': 5,
    'U': 4,
    'V': 3,
    'W': 2,
    'X': 2,
    'Y': 2,
    'Z': 3,
}

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

    if any(MAX_LETTERS_COUNT[letter] > n for letter, n in deck.items()):
        if debug:
            removed = len(WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED)
            start = time()

        WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED = list(filter(
            lambda m: all(deck[letter] >= n for letter, n in m[1]),
            WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED.items()
        ))

        if debug:
            total = round(time() - start, 5)
            color_mode = Back if total > 1 else Fore
            removed -= len(WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED)
            print(f"[{Fore.RED}DELETE{Fore.RESET}]    removed {Fore.CYAN}{removed}{Fore.RESET} words in {color_mode.RED}{total}{color_mode.RESET}s")

    word, _ = WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED[0]
    place(50, 50, word, deck, grid, orientation=HORIZONTAL, debug=debug)
    remaining -= len(word)

    rotation = 1
    while remaining:
        mode, other = (VERTICAL, HORIZONTAL)[::rotation]
        ix, iy = orientations[mode]
        parsed = set()
        valid_positions = positions[other]

        if debug:
            print(f"[{Fore.BLUE}POSITIONS{Fore.RESET}] found {Fore.CYAN}{len(valid_positions)}{Fore.RESET} valid positions in {['HORIZONTAL', 'VERTICAL'][mode]} mode")

        for i in range(len(valid_positions)): #############################
            if i >= len(valid_positions):     # TODO: all this code could #
                break                         # TODO: be optimized        #
            x, y = list(valid_positions)[i]   #############################
            if (x, y) in parsed:
                continue
            pattern = []
            startx, starty = x, y
            previous = None
            while starty >= 0 and startx >= 0:
                current = grid[starty][startx]
                if current == WALL:
                    break
                if (startx - ix, starty - iy) in positions[other]:
                    try: pattern.pop()
                    except: pass
                    break
                if current:
                    parsed.add((startx, starty))
                    pattern.append(current)
                    previous = str
                elif previous == int:
                    pattern[-1] += 1
                else:
                    pattern.append(1)
                    previous = int
                startx -= ix
                starty -= iy
            startx += ix
            starty += iy
            pattern.reverse()
            endx, endy = x + ix, y + iy
            previous = None
            while endy < len(grid) and endx < len(grid[endy]):
                current = grid[endy][endx]
                if current == WALL:
                    break
                if (endx + ix, endy + iy) in positions[mode]: # ??
                    pattern.pop()
                    break
                if current:
                    parsed.add((endx, endy))
                    pattern.append(current)
                    previous = str
                elif previous == int:
                    pattern[-1] += 1
                else:
                    pattern.append(1)
                    previous = int
                endx += ix
                endy += iy

            if not pattern:
                positions.remove((x, y))
                continue

            start = starty if mode == VERTICAL else startx
            for block in get_subblocks(start, pattern):
                block_start = time()
                for i, (word, count) in enumerate(WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED):
                    if len(word) > block.length:
                        continue
                    for letter, n in count:
                        if deck[letter] + block.placed_count[letter] < n:
                            break
                    else:
                        word_length = len(word)
                        for offset in range(word_length):
                            for pos, letter in block.indexes.items():
                                if offset + pos >= word_length or word[offset + pos] != letter or word_length - offset + block.start > block.offset + block.length:
                                    break
                            else:
                                for letter, n in block.placed_count.items():
                                    deck[letter] += n
                                place(x - ix * offset, y - iy * offset, word, deck, grid, orientation=mode, debug=debug)
                                remaining = sum(deck.values())
                                if i:
                                    # FIXIT: this cannot work
                                    # TODO: could cache those results (cache pattern: i)
                                    if debug:
                                        start = time()

                                    # WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED = WORDS_LETTERS_COUNT_BY_POINTS_OPTIMIZED[i:]

                                    if debug:
                                        total = round(time() - start, 5)
                                        color_mode = Back if total > 1 else Fore
                                        print(f"[{Fore.RED}DELETE{Fore.RESET}]    removed {Fore.CYAN}{i}{Fore.RESET} words in {color_mode.RED}{total}{color_mode.RESET}s")

                                break
                        else:
                            continue
                        break
                else:
                    # TODO: cache impossible
                    if debug:
                        total = round(time() - block_start, 5)
                        color_mode = Back if total > 1 else Fore
                        print(f"[{Fore.CYAN}PATTERN{Fore.RESET}]   impossible pattern {Fore.GREEN}{block}{Fore.RESET} checked in {color_mode.RED}{total}{color_mode.RESET}s\n            { { letter: n for letter, n in deck.items() if n } }\n            { { letter: n for letter, n in block.placed_count.items() if n } }") # TODO: compare placed & word & deck
                    continue
                if debug:
                    total = round(time() - block_start, 5)
                    color_mode = Back if total > 1 else Fore
                    print(f"[{Fore.CYAN}PATTERN{Fore.RESET}]   pattern {Fore.GREEN}{block}{Fore.RESET} checked in {color_mode.RED}{total}{color_mode.RESET}s")
                break
            if not remaining:
                break

        if not positions[HORIZONTAL] and not positions[VERTICAL]: # FIXIT: or grid didnt change twice
            if debug:
                print(f"[{Fore.CYAN}POSITIONS{Fore.RESET}] no valid positions remaining")
            break
        rotation -= rotation * 2

    if debug:
        total = round(time() - startup, 5)
        color_mode = Back if total > 1 else Fore
        print(f"[{Fore.LIGHTGREEN_EX}FINISH{Fore.RESET}]    finished in {color_mode.RED}{total}{color_mode.RESET}s")

    minx = miny = maxx = maxy = None
    for y, line in enumerate(grid):
        for x, letter in enumerate(line):
            if letter is not None and letter != '%':
                if not miny:
                    miny = y
                if not minx or minx > x:
                    minx = x
                if not maxx or maxx < x:
                    maxx = x
                maxy = y
    return [
        [
            ' ' if letter is None or letter == '%' else letter
            for letter in line[minx - 1:maxx + 2]
        ]
        for line in grid[miny - 1:maxy + 2]
    ]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Deobfuscates useless javascript forswitches.")
    parser.add_argument("letters", type=str, help="The available letters.")
    parser.add_argument("-v", "--version", action="version", version="0.0.2", help="Show script version and exit.")
    parser.add_argument("-d", "--debug", action="store_true", help="Starts the script in debug mode.")
    args = parser.parse_args()

    with cProfile.Profile() as pr:
        grid = solve(args.letters, debug=args.debug)
        pr.dump_stats('stats.prof')

    print(Fore.LIGHTGREEN_EX)
    for line in grid:
        print(''.join(line))
    print(Fore.RESET)


if __name__ == '__main__':
    main()
