"""plant.py: red controls. From a good colouring, write one colouring per colour c in which a copy of P_c is
planted (all edges of a copy of P_c on random vertices recoloured to c). Every checker must refuse each control.
Usage: python3 -I plant.py COLFILE P0/P1[/..] OUTPREFIX [seed]   -> OUTPREFIX_c<c>.col
"""
import random
import re
import sys


def pat_edges(s):
    m = re.fullmatch(r"K(\d+),(\d+)", s)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return a + b, [(i, a + j) for i in range(a) for j in range(b)]
    m = re.fullmatch(r"K(\d+)-e", s)
    if m:
        k = int(m.group(1))
        return k, [(i, j) for i in range(k) for j in range(i + 1, k) if (i, j) != (0, 1)]
    m = re.fullmatch(r"K(\d+)", s)
    if m:
        k = int(m.group(1))
        return k, [(i, j) for i in range(k) for j in range(i + 1, k)]
    t, x = s[0], int(s[1:])
    if t == "C":
        return x, [(i, (i + 1) % x) for i in range(x)]
    if t == "P":
        return x, [(i, i + 1) for i in range(x - 1)]
    if t == "W":
        return x, [(0, i) for i in range(1, x)] + [(1 + i, 1 + (i + 1) % (x - 1)) for i in range(x - 1)]
    if t == "B":
        return x + 2, [(0, 1)] + [(0, i) for i in range(2, x + 2)] + [(1, i) for i in range(2, x + 2)]
    if t == "F":
        return 2 * x + 1, [e for i in range(x) for e in ((0, 2 * i + 1), (0, 2 * i + 2), (2 * i + 1, 2 * i + 2))]
    raise ValueError(s)


def main():
    path, pats, outp = sys.argv[1], sys.argv[2], sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    names = pats.split("/") if "/" in pats else pats.split(",")
    lines = open(path).read().split()
    n, k = int(lines[0]), int(lines[1])
    rows = [list(r) for r in lines[2:2 + n]]
    rnd = random.Random(seed)
    for c, name in enumerate(names):
        R = [r[:] for r in rows]
        h, E = pat_edges(name)
        vs = rnd.sample(range(n), h)
        changed = 0
        for a, b in E:
            u, v = vs[a], vs[b]
            if R[u][v] != str(c):
                changed += 1
            R[u][v] = R[v][u] = str(c)
        with open(f"{outp}_c{c}.col", "w") as f:
            f.write(f"{n} {k}\n" + "".join("".join(r) + "\n" for r in R))
        print(f"control colour {c}: planted {name} on {vs}, {changed} edges recoloured")


if __name__ == "__main__":
    main()
