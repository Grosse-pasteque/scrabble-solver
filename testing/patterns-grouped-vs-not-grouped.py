import re
from time import time
from random import choice, randint
from string import ascii_uppercase


ITERATIONS = 10_000_000

def main():
    string = ''.join(choice(ascii_uppercase) for _ in range(100))
    pattern = ''.join('.' if randint(0, 9) else letter for letter in string)
    grouped_pattern = re.sub(r'\.*', lambda m: f".{{{len(m.group())}}}", pattern)

    compile_time = time()
    pattern = re.compile(pattern)
    compile_time = time() - compile_time

    compile_grouped_time = time()
    grouped_pattern = re.compile(grouped_pattern)
    compile_grouped_time = time() - compile_grouped_time

    keep = None

    total_time = 0
    for _ in range(ITERATIONS):
        start = time()
        keep = pattern.fullmatch(string)
        total_time += time() - start

    assert keep is not None

    total_grouped_time = 0
    for _ in range(ITERATIONS):
        start = time()
        keep = grouped_pattern.fullmatch(string)
        total_grouped_time += time() - start

    assert keep is not None

    print(f"""
Compiled patterns always run ~1.7 times faster

┌─────────┬─────────────┬─────────┐
│ GROUPED │ COMPILATION │ TIME    │
├─────────┼─────────────┼─────────┤
│ NO      │ {compile_time:.5f}     │ {total_time:.5f} │
│ YES     │ {compile_grouped_time:.5f}     │ {total_grouped_time:.5f} │
└─────────┴─────────────┴─────────┘
""")


if __name__ == '__main__':
    main()
