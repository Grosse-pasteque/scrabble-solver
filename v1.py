import re
import json
from time import time
from colorama import init, Fore, Back
init()

to_set_struture = lambda data: {
    letter: [set(before), set(after)]
    for letter, (before, after) in data.items()
}

# https://github.com/dolph/dictionary/blob/master/ospd.txt
# /usr/share/dict/words
with open('ODS9.txt') as file: # french
    ALL_WORDS = file.read().split('\n')
with open('cache/word-points.json') as file:
    ALL_WORDS_BY_POINTS = json.load(file)
with open('cache/word-points-length.json') as file:
    ALL_WORDS_BY_POINTS_BY_LENGTH = json.load(file)
with open('cache/possible-before-after.json') as file:
    CACHE_POSSIBLE_BEFORE_AFTER = json.load(file)
with open('cache/impossible-before-after.json') as file:
    CACHE_IMPOSSIBLE_BEFORE_AFTER = to_set_struture(json.load(file))
with open('cache/words-letters-count.json') as file:
    CACHE_ALL_WORDS_LETTERS_COUNT = json.load(file)
with open('cache/two-letters-words-possible-before-after.json') as file:
    CACHE_TWO_LETTERS_WORDS_POSSIBLE_BEFORE_AFTER = to_set_struture(json.load(file))

TWO_LETTER_WORDS = [[0, [[2, ['AA', 'AH', 'AI', 'AN', 'AS', 'AU', 'AY', 'BA', 'BE', 'BI', 'BU', 'CA', 'CE', 'CI', 'DA', 'DE', 'DO', 'DU', 'EH', 'EN', 'ES', 'ET', 'EU', 'EX', 'FA', 'FI', 'GO', 'HA', 'HE', 'HI', 'HO', 'IF', 'IL', 'IN', 'JE', 'KA', 'LA', 'LE', 'LI', 'LU', 'MA', 'ME', 'MI', 'MU', 'NA', 'NE', 'NI', 'NO', 'NU', 'OC', 'OH', 'OM', 'ON', 'OR', 'OS', 'OU', 'PI', 'PU', 'QI', 'RA', 'RE', 'RI', 'RU', 'SA', 'SE', 'SI', 'SU', 'TA', 'TE', 'TO', 'TU', 'UD', 'UN', 'US', 'UT', 'VA', 'VE', 'VS', 'VU', 'WU', 'XI']]]]]
ABC = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

WORDS_BY_LENGTH = {}
for word in ALL_WORDS:
    WORDS_BY_LENGTH.setdefault(len(word), []).append(word)
WORDS_BY_LENGTH = sorted(WORDS_BY_LENGTH.items(), key=lambda x: x[0], reverse=True)

UNDERLINE = '\x1b[4m'
NO_UNDERLINE = '\x1b[24m'
LEGEND_TEXT = f"                 {UNDERLINE}Legend{NO_UNDERLINE}"
LEGEND_BLOCK = '       '
LEGEND = {
    'Pattern': f'a letter can be placed there ({Fore.RED}horizontaly{Fore.RESET})',
    'Impossible': 'empty pattern so nothing can be placed',
    'Blocked': 'nothing can be placed there',
}
LETTER_COLORS = {
    'PATTERN': Back.LIGHTYELLOW_EX,
    'BLOCKED': Back.RED,
    'IMPOSSIBLE': Back.LIGHTRED_EX,
}

BLOCKED = '%'
ANY = '.'

PATTERN_STR = LETTER_COLORS['PATTERN'] + ' ' + Back.RESET
BLOCKED_STR = LETTER_COLORS['BLOCKED'] + ' ' + Back.RESET
IMPOSSIBLE_STR = LETTER_COLORS['IMPOSSIBLE'] + ' ' + Back.RESET

for name, description in LEGEND.items():
    block = LETTER_COLORS[name.upper()] + LEGEND_BLOCK + Back.RESET
    LEGEND_TEXT += f'\n  {block}\n  {block}   {name}, {description}\n  {block}\n '


def get_best_initial_word(deck, debug=False):
    global ALL_WORDS_BY_POINTS
    # 125975x performance improvement
    for i, (points, words) in enumerate(ALL_WORDS_BY_POINTS):
        for j, word in enumerate(words):
            count = CACHE_ALL_WORDS_LETTERS_COUNT[word]
            for letter in set(word):
                if deck.get(letter, 0) < count.get(letter, 0):
                    break
            else:
                # ~2.8x performance improvement (highly depends on the best word)
                ALL_WORDS_BY_POINTS = ALL_WORDS_BY_POINTS[i:]
                ALL_WORDS_BY_POINTS[0][1] = ALL_WORDS_BY_POINTS[0][1][j:]
                if debug:
                    a = len(ALL_WORDS)
                    t = sum(len(l) for l in ALL_WORDS_BY_POINTS[:i])
                    print(f"{Back.MAGENTA}FILTER{Back.RESET}: {Fore.LIGHTMAGENTA_EX}{a}{Fore.RESET} => {Fore.LIGHTMAGENTA_EX}{a - t - j}{Fore.RESET}")
                return word
    return []

def rotate(matrix):
    return [list(col) for col in zip(*matrix)]


class Letter:
    is_done = False
    all = []

    def __init__(self, value='.'):
        self.is_blocked = False
        self.is_any = True
        self.is_pattern = False
        self._value = None
        self.other = value
        self.value = value
        self.points = 1
        Letter.all.append(self)

    def __str__(self):
        if self.is_blocked:
            return BLOCKED_STR
        elif self.is_pattern:
            if self.value:
                return PATTERN_STR
            return IMPOSSIBLE_STR
        return self._value

    def __repr__(self):
        return self.__str__()

    def regex(self, deck): # intersec with deck to reduce letters -> which reduces patterns count
        if self.is_pattern:
            p = ''.join(self._value & deck)
            if p:
                return '[' + p + ']'
            return BLOCKED
        return self._value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        self.points = 1
        self._value = value
        self.is_blocked = value == BLOCKED
        self.is_any = value == ANY

        # Better than type(value) == set or isinstance(value, set)
        # 1.2x performance improvement
        self.is_pattern = value.__class__ == set
        if not self.is_pattern and not self.is_any or self.is_blocked:
            self.other = value

    def __iand__(self, other: set):
        if self.is_pattern:
            self._value &= other
            self.points += 1
            # if not self._value:
            #     self.value = BLOCKED # -> may prevent some letters to be placed
        elif self.is_any:
            other = set(other) # copy
            if self.other.__class__ == set:
                self.other &= other
                self.value = self.other
            else:
                self.value = other

    @classmethod
    def rotate(cls):
        for letter in cls.all:
            tmp = letter.value
            letter.value = letter.other
            letter.other = tmp


def print_grid(grid, title='Grid'):
    minx = miny = maxx = maxy = None
    for y, line in enumerate(grid):
        for x, letter in enumerate(line):
            if not letter.is_any:
                if not miny:
                    miny = y
                if not minx or minx > x:
                    minx = x
                if not maxx or maxx < x:
                    maxx = x
                maxy = y
    print('\n' + '=' * 20 + '[ ' + Fore.YELLOW + str(title) + Fore.RESET + ' ]' + '=' * 20)
    for y, line in enumerate(grid[miny:maxy + 1]):
        line = ''.join(str(letter) for letter in line[minx:maxx + 1]).replace('.', ' ')
        if line.strip():
            print(f'{y + miny:<3}', line)
    print('=' * (44 + len(str(title))) + '\n')

def ensure_grid_buffer(x, y, grid): # TODO: optimize -> wastes 0.026
    """
    Ensures there is a 15-cell buffer around the edges of the placed word.
    Dynamically expands the grid as needed.
    """
    buffer = 15

    # Calculate required size
    width = len(grid[0]) if grid else 0
    height = len(grid)

    # Expand vertically (top and bottom)
    while y < buffer:
        grid.insert(0, [Letter() for _ in range(width)])
        y += 1
    while y >= len(grid) - buffer:
        grid.append([Letter() for _ in range(width)])

    # Recalculate height (grid may have been expanded)
    height = len(grid)

    # Expand horizontally (left and right)
    while x < buffer:
        for row in grid:
            row.insert(0, Letter())
        x += 1
    while x >= len(grid[0]) - buffer:
        for row in grid:
            row.append(Letter())

    return x, y

def place_letter(x, y, letter, deck, grid):
    grid[y][x].value = letter
    if letter != BLOCKED:
        # propagates the allowed letters on empty slots
        before = grid[y - 1][x] # FIXIT: depend du rotate mode
        after = grid[y + 1][x]
        pattern_before, pattern_after = CACHE_TWO_LETTERS_WORDS_POSSIBLE_BEFORE_AFTER[letter]
        before &= pattern_before
        after &= pattern_after
        deck[letter] -= 1
        if deck[letter] < 0:
            raise ValueError(deck)

def place(x, y, word, deck, grid):
    x, y = ensure_grid_buffer(x, y, grid)
    for i, letter in enumerate(BLOCKED + word + BLOCKED):
        place_letter(x + i - 1, y, letter, deck, grid)
    ensure_grid_buffer(x, y, grid)

def print_times(times, warn=1, indent=1):
    if not times:
        return
    if times.__class__ == dict:
        l = len(max(times, key=len))
        times = times.items()
    else:
        l = len(str(len(times)))
        times = enumerate(times, start=1)
    for name, data in times:
        title = f"{indent * ' '}- {Fore.LIGHTBLACK_EX}{name}{Fore.RESET}: "
        title += ' ' * (l - len(str(name)))
        if data.__class__ in (float, int):
            mode = Back if data > warn else Fore
            print(f"{title}{mode.RED}{data:.5f}{mode.RESET}")
        else:
            print(f"{title}{Fore.GREEN}{len(data)}{Fore.RESET}")
            print_times(data, warn, indent + 2)

def get_subblocks(x, y, pattern):
    """
    [14, '[|]', 'F', '[|]', 1, '[|]', 'F', '[|]', 3, '[|]', 'K', '[|]', 26]):


    [14, '[|]', 'F', '[|]', 0]
    [0, '[|]', 'F', '[|]', 2]
    [2, '[|]', 'K', '[|]', 26]

    [14, '[|]', 'F', '[|]', 1, '[|]', 'F', '[|]', 2]
    [13, '[|]', 'F', '[|]', 1, '[|]', 'F', '[|]', 3, '[|]', 'K', '[|]', 26]
    [0, '[|]', 'F', '[|]', 3, '[|]', 'K', '[|]', 26]
    """
    current = Block(x, y, [], [])
    subpatterns = [current]
    for i, part in enumerate(pattern):
        if part.__class__ == int:
            if current.placed:
                if i < len(pattern) - 1:
                    subpatterns.append(Block(x + 1, y, [part], []))
            x += part
        else:
            x += 1
            if len(part) == 1:
                current.placed.append(part)
        current.compiled.append(part)
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
                block.compiled[-1] -= 1
            if i:
                block.compiled[0] -= 1
        extended += inner_extended
    for i, block in enumerate(subpatterns):
        if i < len(subpatterns) - 1:
            block.compiled[-1] -= 1
        if i:
            block.compiled[0] -= 1
    return subpatterns + extended


class Block:
    def __init__(self, raw: list[Letter], compiled: re.Pattern):
        # self.start = start
        # self.end = end
        # self.line = line
        # self.is_start = start == 0
        # self.is_end = end == len(grid[line])
        self.compiled = compiled
        self.raw = raw

    def __repr__(self):
        return f"Block({self.compiled})"

    def compile(self):
        compiled,
        line[offset:x],

    @property
    def size(self):
        return self.end - self.start

    @classmethod
    def make(cls, raw: list[Letter], pattern: list[int | str]):
        compiled = ''
        raw = grid[y][start:end]
        any_counter = 0
        for offset, x in enumerate(raw, start=start):
            # if x.is_any:
            #     any_counter += 1
            # elif any_counter:
            #     compiled.append(any_counter)
            #     any_counter = 0
            # if x.
            if x.__class__ == int:
                if x > 13:
                    compiled += '.*'
                else:
                    compiled += '.{'
                    if start == 0 and offset in (0, end):
                        compiled += ','
                    compiled += str(x) + '}'
            else:
                compiled += str(x)
        if start == 0:
            compiled = re.sub(r'^\.+', '.*', compiled)
        if end == len:
            compiled = re.sub(r'^\.+', '.*', compiled)
        return [Block(raw, compiled)]


class Block:
    def __init__(self, x, y, compiled, placed):
        self.x = x
        self.y = y
        self.compiled = compiled
        self.placed = placed
        self.is_fixed = True
        self.min_length = 0
        self.length = 0

    def __repr__(self):
        return f"<({self.x}, {self.y}) {self.compiled}>"

    def __add__(self, other: Block):
        return Block(self.x, self.y, self.compiled[:-1] + other.compiled, self.placed + other.placed)

    def compile(self):
        self.length = sum(p if p.__class__ == int else 1 for p in self.compiled)
        self.min_length = self.length
        try:
            self.min_length -= self.compiled[-1]
        except:
            self.min_length -= 1
        try:
            self.min_length -= self.compiled[0]
        except:
            self.min_length -= 1
        self.compiled = re.compile(''.join(
            ('.*' if x > 13 else f".{{{'' if self.is_fixed or i and i != len(self.compiled) - 1 else ','}{x}}}") if x.__class__ == int else x
            for i, x in enumerate(self.compiled)
        ))


def solver(deck, debug=False):
    if debug:
        startup = time()
    deck = { letter: deck.count(letter) for letter in set(deck) }
    remaining = not not deck

    rotate_mode = 0
    grid = []

    word = get_best_initial_word(deck, debug=debug) # TODO: preprocess all possible words with deck ?
    if debug:
        iterations = 0
        print(f"CHOSEN WORD:       {Fore.MAGENTA}{word}{Fore.RESET}")
        print(f"REMAINING LETTERS: {Fore.LIGHTMAGENTA_EX}{sum(deck.values())} {Fore.LIGHTYELLOW_EX}{''.join(n * letter for letter, n in deck.items())}{Fore.RESET}")

    place(0, 0, word, deck, grid)
    if debug:
        print_grid(grid)
        patterns_test = {}

    grid = rotate(grid)
    rotate_mode = not rotate_mode
    Letter.rotate()
    cached_patterns = {}

    end = 0
    while remaining:
        str_deck = ''.join(n * letter for letter, n in deck.items())
        remaining = len(str_deck)
        set_deck = set(str_deck)
        blocks = []
        if debug:
            times = {}
            start = time()
        for y, line in enumerate(grid):
            placed_letters = []
            has_letters = has_holes = False
            offset = 0
            blocks_of_line = []
            pattern = []
            for x, letter in enumerate(line):
                if letter.is_any: # or letter.is_pattern:
                    if pattern and pattern[-1].__class__ == int:
                        pattern[-1] += 1
                    else:
                        pattern.append(1)
                    if not has_holes:
                        has_holes = True
                else:
                    s = letter.regex(set_deck)
                    if s == BLOCKED:
                        if has_holes and has_letters and pattern:
                            blocks_of_line += get_subblocks(offset, y, pattern)
                        placed_letters = []
                        has_letters = has_holes = False
                        pattern = []
                        offset = x + 1
                    else:
                        pattern.append(s)
                        if not letter.is_pattern:
                            placed_letters.append(letter.value)
                            if not has_letters:
                                has_letters = True
                        elif not has_holes:
                            has_holes = True
            if has_holes and has_letters and pattern:
                blocks_of_line += get_subblocks(offset, y, pattern)
            if blocks_of_line:
                # first and lasts arent fixed
                blocks_of_line[0].is_fixed = blocks_of_line[-1].is_fixed = False
                blocks += blocks_of_line

        blocks.sort(key=lambda block: sum(-1 if x.__class__ == int else 10 for x in block.compiled))
        """

        >>> pattern = [., ., ., [VU], A, I, ., A, I, ., ., ., ., ., .]
        >>> text = "AIMER"
        >>> 
        >>> matches = []
        >>> for i in range(len(pattern) - len(text) + 1)
        >>>     subpattern = ''
        >>>     valid = False
        >>>     for p in pattern[i:i + len(text)]:
        >>>         if p.is_valid:
        >>>             valid = True
        >>>         subpattern += p
        >>>     if valid and re.match(subpattern, text):
        >>>         matches.append(i)

        """
        for block in blocks:
            block.compile() # TODO: can preprocess this ?
        if debug:
            times['PATTERN'] = time() - start

        max_points = 0
        max_block = None
        max_word = None

        if debug:
            times['FETCH'] = {}
        for i, block in enumerate(blocks):
            if debug:
                start = time()
                patterns_test.setdefault(block.compiled.pattern, 0)

            available = dict(deck)
            for letter in block.placed:
                available[letter] += 1
            total_available = sum(available.values())

            # directly implementing opti_word_points_cached to prevent
            # looping over words with less points then max_points
            found = set()
            cache = cached_patterns.get(block.compiled.pattern) # 3.7x performance improvement
            if end < 2 and cache is not None:
                if debug:
                    if cache:
                        print(f"{Back.CYAN}CACHE-GET{Back.RESET}:    {Fore.LIGHTBLACK_EX}{block.compiled.pattern!r}{Fore.RESET} -> {{ {', '.join(Fore.GREEN + word + Fore.RESET for _, _, word in cache) if len(cache) < 100 else Fore.GREEN + '...' + Fore.RESET} }}")
                    else:
                        print(f"{Back.WHITE}CACHE-IGNORE{Back.RESET}: {Fore.LIGHTBLACK_EX}{block.compiled.pattern!r}{Fore.RESET}")
                for points, length, word in cache:
                    # if max_points > get_total_points(word):
                    #     continue
                    if length > block.length or length < block.min_length or length > total_available: # ~3.2x performance improvement
                        continue
                    count = CACHE_ALL_WORDS_LETTERS_COUNT[word] # sort by points for faster access
                    for letter in set(word):
                        if available.get(letter, 0) < count.get(letter, 0):
                            break
                    else:
                        found.add((points, length, word))
                        if max_points < points:
                            max_points = points
                            max_word = word
                            max_block = block
                if cache:
                    cached_patterns[block.compiled.pattern] = found
                    if debug:
                        print(f"{Back.BLUE}CACHE-SET{Back.RESET}:    {Fore.LIGHTBLACK_EX}{block.compiled.pattern!r}{Fore.RESET} -> ", end="")
                        if not found:
                            print("∅")
                        elif len(found) > 100:
                            print('{', Fore.GREEN + '...' + Fore.RESET, '}')
                        else:
                            print('{', ', '.join(Fore.GREEN + word + Fore.RESET for _, _, word in found), '}')
            else:
                for points, words_by_length in ALL_WORDS_BY_POINTS_BY_LENGTH if end < 2 else TWO_LETTER_WORDS: # ~2.7x performance improvement
                    # OPTION: sort-mode=TOTAL_POINTS_V2
                    # if points > total_available: # 26x performance improvement
                    #    continue

                    # OPTION: best-word=False
                    if points < max_points:
                       break
                    for length, words in words_by_length:
                        if length > block.length or length < block.min_length or length > total_available:
                            continue
                        for word in words:
                            count = CACHE_ALL_WORDS_LETTERS_COUNT[word] # sort by points for faster access
                            for letter in set(word):
                                """ 3x performance improvement
                                list.count  ~7.3e-7
                                str.count   ~2.9e-7
                                dict.get    ~2e-7
                                """
                                if available.get(letter, 0) < count.get(letter, 0):
                                    break
                            else:
                                if re.fullmatch(block.compiled, word):
                                    found.add((points, length, word))
                                    if max_points < points:
                                        max_word = word
                                        max_points = points
                                        max_block = block
                                        # OPTION: best-word=False
                                        break
                        # OPTION: best-word=False
                        if found:
                            break
                    # OPTION: best-word=False
                    if found:
                        break
                cached_patterns[block.compiled.pattern] = found
                if debug:
                    print(f"{Back.BLUE}CACHE-SET{Back.RESET}:    {Fore.LIGHTBLACK_EX}{block.compiled.pattern!r}{Fore.RESET} -> ", end="")
                    if not found:
                        print("∅")
                    elif len(found) > 100:
                        print('{', Fore.GREEN + '...' + Fore.RESET, '}')
                    else:
                        print('{', ', '.join(Fore.GREEN + word + Fore.RESET for _, _, word in found), '}')
            if debug:
                res = times['FETCH'][f'BLOCK-{i}'] = time() - start
                patterns_test[block.compiled.pattern] += res
            # OPTION: best-word=False
            if found:
                break

        if max_word:
            if debug:
                start = time()

            # TODO: can be optimized
            word_offset = 0
            raw_line = grid[max_block.y][max_block.x:max_block.x + max_block.length]

            for word_offset in range(len(raw_line) - len(max_word) + 1): # fixed +1
                to_remove = [pattern for pattern in raw_line[word_offset:] if not pattern.is_any]
                for i, letter in enumerate(max_word):
                    other = raw_line[word_offset + i]
                    if letter in other.value:
                        try:
                            to_remove.remove(other)
                            if not to_remove:
                                break
                        except:
                            pass
                if not to_remove:
                    break
            """
            positions = { i: letter for i, letter in enumerate(raw_pattern[:-len(max_word) + 1]) if letter != '.' }
            for i in range(len(max_word)):
                for word_offset, letter in positions.items():
                    if letter == max_word[i + word_offset - min(positions)]:
                        try:
                            to_remove.remove(letter)
                            if not to_remove:
                                break
                        except:
                            pass
                else:
                    if not to_remove:
                        break
            """

            for letter in max_block.placed:
                deck[letter] += 1
                remaining += 1

            place(max_block.x + word_offset, max_block.y, max_word, deck, grid)
            remaining -= len(max_word)
            if debug:
                times['INDEX'] = time() - start

        if debug:
            print("TIMES:")
            print_times(times)
            print(f"GRID SIZE:              {Fore.CYAN}{len(grid[0])}{Fore.RESET} x {Fore.CYAN}{len(grid)}{Fore.RESET}")
            print(f"REMAINING LETTERS:      {Fore.LIGHTMAGENTA_EX}{sum(deck.values())} {Fore.LIGHTYELLOW_EX}{''.join(n * letter for letter, n in deck.items())}{Fore.RESET}")
            if max_word:
                print(f"CHOSEN WORD:            {Fore.MAGENTA}{max_word}{Fore.RESET}")
                print(f"ALREADY PLACED LETTERS: [ {', '.join(Fore.GREEN + letter + Fore.RESET for letter in max_block.placed)} ]")
                print(f"USED LETTERS:           {Fore.BLUE}{len(max_word) - len(max_block.placed)}{Fore.RESET}")
                print(f"MATCH:                  {Fore.GREEN}{max_block.compiled.pattern!r}{Fore.RESET} AT {Fore.BLUE}{word_offset}{Fore.RESET}")
        if max_word:
            if debug:
                print_grid(grid, f"{iterations} : {Fore.CYAN}{[0, 90][rotate_mode]}°")
            end = 0
        elif end > 2: # no solutions in both orientations
            break
        else:
            end += 1
            if end > 1 and debug:
                print("""{0}{2}{1}\n{0}{3}Entering 2 letters mode{3}{1}\n{0}{2}{1}""".format(Back.LIGHTRED_EX, Back.RESET, ' ' * 35, ' ' * 6))
            # OPTION: force-rotate=True
            # grid = rotate(grid)
            # rotate_mode = not rotate_mode
            # Letter.rotate()

        # OPTION: force-rotate=True
        grid = rotate(grid)
        rotate_mode = not rotate_mode
        Letter.rotate()
        if debug:
            iterations += 1

    if debug:
        print("TIMES:")
        print_times(patterns_test)
        print_grid(grid, f"FINAL : {Fore.CYAN}{[0, 90][rotate_mode]}°")
        print(LEGEND_TEXT)
        print(f"GRID SIZE:              {Fore.CYAN}{len(grid[0])}{Fore.RESET} x {Fore.CYAN}{len(grid)}{Fore.RESET}")
        print(f"REMAINING LETTERS:      {Fore.LIGHTMAGENTA_EX}{sum(deck.values())} {Fore.LIGHTYELLOW_EX}{''.join(n * letter for letter, n in deck.items())}{Fore.RESET}")
        print(f"{Back.YELLOW}{Fore.BLACK}TOTAL TIME: {(time() - startup):.5f}s{Fore.RESET}{Back.RESET}")

    # shrinks back
    minx = miny = maxx = maxy = None
    for y, line in enumerate(grid):
        for x, letter in enumerate(line):
            if not letter.is_any and not letter.is_pattern and not letter.is_blocked:
                if not miny:
                    miny = y
                if not minx or minx > x:
                    minx = x
                if not maxx or maxx < x:
                    maxx = x
                maxy = y
    return [
        [
            '.' if letter.is_blocked or letter.is_any or letter.is_pattern else letter.value
            for letter in line[minx:maxx + 1]
        ]
        for line in grid[miny:maxy + 1]
    ]


def main():
    from sys import argv
    if len(argv) < 2:
        return
    if '-d' in argv:
        argv.remove('-d')
        debug = True
    elif '--debug' in argv:
        argv.remove('--debug')
        debug = True
    else:
        debug = False
    if len(argv) < 2:
        return
    deck = argv.pop()
    import cProfile
    with cProfile.Profile() as pr:
        grid = solver(deck, debug=debug)
        pr.dump_stats('stats.prof')

    for line in grid:
        print(''.join(' ' if c == '.' else Fore.LIGHTGREEN_EX + c + Fore.RESET for c in line))


if __name__ == '__main__':
    main()
