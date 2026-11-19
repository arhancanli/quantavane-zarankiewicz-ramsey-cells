"""kab_card.py (encoder A, cardinality form): is there a 2-colouring of the edges of K_n with no colour-0 copy of
K_{a0,b0} and no colour-1 copy of K_{a1,b1}?

Fact used: a graph contains K_{a,b} (a <= b, not necessarily induced) iff some a-set S of vertices has at least b
common neighbours (they lie outside S). So for each colour c and each a-set S we add one auxiliary y per vertex x
outside S, forced true when every edge xs (s in S) has colour c, and say "at most b - 1 of these y are true".

Exact CNF (checks/kabcard.c writes the same file from its own code; the SHA-256 must agree):
  Variables 1..E: edge e = (u, v), u < v, row-major; true = colour 0, false = colour 1 (as tools/cegar.py, k = 2).
  Base: the lex-leader clauses of tools/cegar.py (Enc.sb("all", False): x <=_lex sigma(x) for every vertex
  transposition (i j), i < j row-major, comparator variables E+1..top). No colour swap (the patterns differ).
  Then for c = 0, 1 with (a, b) = (min, max) of the sides of pattern c, for every a-set S in lexicographic order:
    X = vertices not in S, increasing; m = |X|; y_t = top+1+t (t = 0..m-1); top += m;
    for t: clause  y_t OR (OR over s in S of NOT[edge X[t]s has colour c]);
    at most K = b - 1 of y_0..y_{m-1} (Sinz sequential counter): if K = 0: clause -y_t for each t; else registers
    r(i, j) = top+1+i*K+j (i = 0..m-2, j = 0..K-1), top += (m-1)*K, clauses in this order:
      [-y_0, r(0,0)];  [-r(0,j)] for j = 1..K-1;
      for i = 1..m-2: [-y_i, r(i,0)]; [-r(i-1,0), r(i,0)];
                      for j = 1..K-1: [-y_i, -r(i-1,j-1), r(i,j)], [-r(i-1,j), r(i,j)];
                      [-y_i, -r(i-1,K-1)];
      [-y_{m-1}, -r(m-2,K-1)].
Soundness (UNSAT => no good colouring): from a good colouring take the lex-least colouring of its orbit under vertex
permutations (also good; it satisfies every lex-leader constraint, Crawford et al. 1996), set y = the AND of its
edges (at most K true per S, since S has at most b - 1 common neighbours) and the counter registers to the running
sums: all clauses hold. Conversely a model decodes to a good colouring (a copy would force b of the y of one S).
Patterns: Ka,b, or C4 (= K2,2), or Bk (book K2 + kK1: an edge uv of colour c with >= k common colour-c neighbours;
same layout with a = 2, b = k, and the literal NOT[uv has colour c] appended to the counter's overflow clauses
[-y_i, -r(i-1,K-1)] and [-y_{m-1}, -r(m-2,K-1)], or to the clauses -y_t when K = 0).
Usage: python -I kab_card.py N P0/P1 OUT.cnf [nosb]   (nosb: omit the lex-leader block; edge variables 1..E only)
"""
import os, sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def sides(name):
    """(a, b, book): C4 = K2,2; Ka,b; Bk = K2 + kK1 (book: an edge uv of colour c with >= k common colour-c
    neighbours; encoded as a = 2, b = k with the activation literal "uv has colour c" on the overflow clauses)."""
    if name == "C4":
        return 2, 2, False
    if name.startswith("B"):
        return 2, int(name[1:]), True
    a, b = name[1:].split(",")
    a, b = int(a), int(b)
    return min(a, b), max(a, b), False


def main():
    n, patarg, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
    nosb = len(sys.argv) > 4 and sys.argv[4] == "nosb"   # optional: no symmetry-breaking clauses (confirmation runs)
    pats = patarg.split("/")
    assert len(pats) == 2
    from cegar import Enc  # noqa: E402  (base clauses: the validated lex-leader scheme)
    enc = Enc(n, pats)
    base = enc.onehot() + ([] if nosb else enc.sb("all", False))
    top = enc.top if not nosb else n * (n - 1) // 2
    E = n * (n - 1) // 2
    assert enc.k == 2 and len(enc.onehot()) == 0
    eid = {}
    for u in range(n):
        for v in range(u + 1, n):
            eid[(u, v)] = len(eid) + 1
    var = lambda u, v: eid[(min(u, v), max(u, v))]
    cls = []
    for c in (0, 1):
        a, b, book = sides(pats[c])
        K = b - 1
        lit = (lambda u, v: var(u, v)) if c == 0 else (lambda u, v: -var(u, v))   # "edge uv has colour c"
        for S in combinations(range(n), a):
            X = [x for x in range(n) if x not in S]
            m = len(X)
            y = [top + 1 + t for t in range(m)]
            top += m
            for t in range(m):
                cls.append([y[t]] + [-lit(X[t], s) for s in S])
            act = [-lit(S[0], S[1])] if book else []   # book: the bound applies only when edge S has colour c
            if K == 0:
                cls.extend([[-y[t]] + act for t in range(m)])
                continue
            r = lambda i, j, base_=top: base_ + 1 + i * K + j
            top += (m - 1) * K
            cls.append([-y[0], r(0, 0)])
            for j in range(1, K):
                cls.append([-r(0, j)])
            for i in range(1, m - 1):
                cls.append([-y[i], r(i, 0)])
                cls.append([-r(i - 1, 0), r(i, 0)])
                for j in range(1, K):
                    cls.append([-y[i], -r(i - 1, j - 1), r(i, j)])
                    cls.append([-r(i - 1, j), r(i, j)])
                cls.append([-y[i], -r(i - 1, K - 1)] + act)
            cls.append([-y[m - 1], -r(m - 2, K - 1)] + act)
    allc = base + cls
    with open(out, "w") as f:
        f.write(f"c ramsey-exact kab_card n={n} pats={patarg} base={len(base)} E={E}\n")
        f.write(f"p cnf {top} {len(allc)}\n")
        for cl in allc:
            f.write(" ".join(map(str, cl)) + " 0\n")
    print(f"n={n} pats={patarg} vars={top} clauses={len(allc)} base={len(base)}")


if __name__ == "__main__":
    main()
