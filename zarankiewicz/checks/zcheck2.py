"""zcheck2.py (witness checker 2, written apart from zcheck.c and the encoders): transposed characterisation.
An m x n 0/1 matrix has an S x T all-ones submatrix (S rows, T columns) iff some T-set of COLUMNS is contained
in at least S rows. For each T-set of columns we count the rows whose support contains it (rows stored as Python
sets; the T-sets are enumerated only inside each row's support, and counted in a dictionary).
Usage: python3 -I zcheck2.py FILE S T [K]   -> PASS / FAIL with the offending block.
"""
import sys
from collections import defaultdict
from itertools import combinations


def main():
    path, S, T = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    K = int(sys.argv[4]) if len(sys.argv) > 4 else None
    rows = []
    for line in open(path):
        bits = [c for c in line if c in "01"]
        if bits:
            rows.append(bits)
    m = len(rows)
    n = len(rows[0])
    if any(len(r) != n for r in rows):
        print("FAIL ragged")
        return 1
    supp = [frozenset(j for j, c in enumerate(r) if c == "1") for r in rows]
    ones = sum(len(s) for s in supp)
    cnt = defaultdict(list)
    for i, s in enumerate(supp):
        for C in combinations(sorted(s), T):
            cnt[C].append(i)
    for C, rs in cnt.items():
        if len(rs) >= S:
            print(f"FAIL {S}x{T} block: rows {rs[:S]} columns {list(C)}")
            return 1
    if K is not None and ones < K:
        print(f"FAIL ones={ones} < K={K}")
        return 1
    print(f"PASS m={m} n={n} ones={ones} no {S}x{T} all-ones block (checked {len(cnt)} column {T}-sets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
