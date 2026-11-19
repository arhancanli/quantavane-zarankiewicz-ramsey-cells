"""bounds.py: recompute every elementary step of the upper bounds (standard library only).

Reads cells.tsv (one line per cell: m n s t value route input witness cert). For each cell of this repository:
  D    deletion bound from the previous cell of the row:  value == floor(n * z(m,n-1) / (n-1));
  R    deletion bound from the previous row:              value == floor(m * z(m-1,n) / (m-1));
  S    certified SAT case split: the deletion bound from the previous cell is value + 1 (so it does not suffice),
       the counting bound is larger than value, and the cert records every case as VERIFIED UNSAT;
  C+S  upper bound credited to Collins et al. 2016, confirmed by a certified SAT case split;
  cnt  the counting bound (Guy's argument A, tools/ubound.py) equals value.
Every cell must also satisfy value <= counting bound. Then the finite facts of the row theorem for z(8,n;4,4)
(Lemmas 3.1 and 3.3 of the paper), the packings, and the counting step for the two star Ramsey values.
Usage: python3 -I tools/bounds.py        (run from the zarankiewicz/ folder); prints OK lines, exit 1 on any failure."""
import csv
import os
import sys
from itertools import combinations
from math import comb

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ubound import ub  # noqa: E402

bad = []


def need(cond, msg):
    if not cond:
        bad.append(msg)


def roman(m, n, s, t):
    """Roman's bound, minimum over p (Tan 2022, Theorem 2.2), in exact integer arithmetic."""
    best = None
    for p in range(s - 1, m + 1):
        num = (t - 1) * comb(m, s) * s + (p + 1) * (s - 1) * n * comb(p, s - 1)
        v = num // (comb(p, s - 1) * s)
        best = v if best is None else min(best, v)
    return best


val, rows = {}, []
for r in csv.DictReader((l for l in open("cells.tsv") if not l.startswith("#")), delimiter="\t"):
    key = (int(r["m"]), int(r["n"]), int(r["s"]), int(r["t"]))
    val[key] = int(r["value"])
    if r["route"] != "published":
        rows.append((key, r))

for (m, n, s, t), r in rows:
    v, route = val[(m, n, s, t)], r["route"]
    U = ub(m, n, s, t)
    need(v <= U, f"z({m},{n};{s},{t}) = {v} exceeds the counting bound {U}")
    prev = val.get((m, n - 1, s, t))
    delc = n * prev // (n - 1) if prev is not None else None
    cert = open(r["cert"]).read()
    if route == "D":
        need(delc == v, f"z({m},{n};{s},{t}): deletion from {prev} gives {delc}, not {v}")
    elif route == "R":
        up = val[(m - 1, n, s, t)]
        need(m * up // (m - 1) == v, f"z({m},{n};{s},{t}): row deletion from {up} gives {m * up // (m - 1)}")
        if prev is not None:
            need(delc == v, f"z({m},{n};{s},{t}): column deletion from {prev} gives {delc}")
    elif route in ("S", "C+S"):
        if route == "S":
            need(delc == v + 1, f"z({m},{n};{s},{t}): deletion gives {delc}, expected value + 1 = {v + 1}")
        need(U > v, f"z({m},{n};{s},{t}): the counting bound already gives {U}")
        need("VERIFIED UNSAT" in cert, f"z({m},{n};{s},{t}): no verified case recorded in {r['cert']}")
        if (m, n, s) == (9, 18, 5):
            need(18 * val[(9, 17, 5, 5)] // 17 == v, "z(9,18;5): Collins's bound is the deletion bound from 121")
    elif route == "cnt":
        need(U == v, f"z({m},{n};{s},{t}): counting bound {U} != {v}")
    else:
        need(False, f"unknown route {route}")
    print(f"  z({m},{n};{s},{t}) = {v:3d}  route {route:3s}  counting {U:3d}  Roman {roman(m, n, s, t):3d}"
          + (f"  deletion {delc}" if delc is not None else ""))

# ---- the row theorem for z(8,n;4,4) ----
z8 = {n: val[(8, n, 4, 4)] for n in range(18, 63)}
for k in range(9):
    need(4 * k - 15 <= comb(k, 4) and k - 3 <= comb(k, 4) and 10 * k - 45 <= comb(k, 4), f"Roman tangent at k={k}")
for B in range(1, 32):
    need((210 + 45 * B) // 10 <= 4 * B + 36, f"(F) by Roman p=5 at B={B}")
for B in range(32, 43):
    need(z8[B] <= 4 * B + 36, f"(F) at B={B}")
for n in range(33, 63):
    need(z8[n] == 4 * n + 36, f"z(8,{n}) != 4n+36")
for n in range(38, 1001):
    need(n * (4 * n + 32) // (n - 1) == 4 * n + 36, f"deletion induction at n={n}")
for n in range(63, 67):
    need(4 * n + 36 == (210 + 15 * n) // 4, f"Lemmas 3.1 and 3.3 disagree at n={n}")
need((210 + 15 * 66) // 4 == 300 and (210 + 15 * 210) // 4 == 840 == 3 * 210 + 210, "formula joins at 66 and 210")
for n in range(1, 1001):
    need(((210 + 15 * n) // 4 <= 3 * n + 210) == (n <= 211), f"min switch at n={n}")
for n in range(19, 1001):
    need(roman(8, n, 4, 4) == min((210 + 15 * n) // 4, 3 * n + 210, (210 + 45 * n) // 10), f"Roman p in 3,4,5 at n={n}")


def max_load(fam):
    load = {Q: 0 for Q in combinations(range(8), 4)}
    for f in fam:
        for Q in combinations(sorted(f), 4):
            load[Q] += 1
    return max(load.values())


sig = {0: 1, 1: 2, 2: 0, 3: 4, 4: 5, 5: 3, 6: 7, 7: 6}
tan = set()
for b in ["01236", "01345", "01346", "01356", "01456", "03467", "03567", "04567"]:
    x = frozenset(int(c) for c in b)
    for _ in range(6):
        tan.add(x)
        x = frozenset(sig[i] for i in x)
need(len(tan) == 36 and max_load(tan) == 3, "Tan's T_{4,4}(8) packing")
lab = [frozenset(map(int, l.split())) for l in open("witnesses/pack5_8_36.txt") if l.strip()]
need(len(lab) == 36 and all(len(f) == 5 for f in lab) and max_load(lab) <= 3, "witnesses/pack5_8_36.txt")

# ---- the two star Ramsey values: 2 ex(N,C4) + floor(N(t-1)/2) < C(N,2) ----
for N, t, ex in ((23, 13, 56), (24, 14, 59)):
    need(2 * ex + N * (t - 1) // 2 < comb(N, 2), f"counting for R(C4,C4,K1,{t}) <= {N}")

if bad:
    for b in bad:
        print("FAIL", b)
    sys.exit(1)
print(f"bounds: {len(rows)} cells, the row-theorem facts, the packings and the star counting all OK")
