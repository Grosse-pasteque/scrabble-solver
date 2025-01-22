from time import time


ITERATIONS = 100_000

def main():
    keep = []

    reverse_time = 0
    for i in range(ITERATIONS):
        start = time()
        keep.append(i)
        reverse_time += time() - start
    start = time()
    keep.reverse()
    reverse_time += time() - start

    assert keep[0] == ITERATIONS - 1
    keep = []

    insert_0 = 0
    for i in range(ITERATIONS):
        start = time()
        keep.insert(0, i)
        insert_0 += time() - start

    assert keep[0] == ITERATIONS - 1

    print(f"""
┌──────────┬──────────┐
│ REVERSE  │ INSERT 0 │
├──────────┼──────────┤
│ {reverse_time:.5f}  │ {insert_0:.5f}  │
└──────────┴──────────┘
""")


if __name__ == '__main__':
    main()
