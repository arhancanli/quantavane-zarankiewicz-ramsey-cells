"""plant.py (red controls): from a good matrix write controls that both checkers must refuse.
  ctrl A: rows 0..S-1 and the T columns with most ones among them set to all-ones (a planted S x T block);
  ctrl B: a random S-set of rows and T-set of columns set to all-ones (seeded);
  ctrl C: the block planted on the last S rows and the last T columns.
Usage: python3 -I plant.py MAT S T OUTPREFIX SEED"""
import random
import sys

path, S, T, pre, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], int(sys.argv[5])
A = [[c for c in line.strip() if c in "01"] for line in open(path) if line.strip()]
m, n = len(A), len(A[0])


def write(B, tag):
    with open(f"{pre}.{tag}.mat", "w") as f:
        for r in B:
            f.write("".join(r) + "\n")


def plant(rows, cols):
    B = [r[:] for r in A]
    for i in rows:
        for j in cols:
            B[i][j] = "1"
    return B


rows = list(range(S))
cols = sorted(range(n), key=lambda j: -sum(A[i][j] == "1" for i in rows))[:T]
write(plant(rows, sorted(cols)), "ctrlA")
rnd = random.Random(seed)
write(plant(sorted(rnd.sample(range(m), S)), sorted(rnd.sample(range(n), T))), "ctrlB")
write(plant(list(range(m - S, m)), list(range(n - T, n))), "ctrlC")
