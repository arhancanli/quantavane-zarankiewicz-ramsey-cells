"""cegar.py (encoder A): is there a k-colouring of the edges of K_n with no colour-c copy of H_c (c = 0..k-1)?

Variables: k = 2: x_e = var e+1 (true = colour 0, false = colour 1). k >= 3: x_{e,c} = var e*k+c+1, one-hot
(at least one colour per edge; pairwise at most one). Edges e = (u, v), u < v, in row-major order.

Clauses: (1) one-hot clauses (k >= 3); (2) lex-leader symmetry breaking, x <=_lex sigma(x) for the variable
permutation sigma induced by each vertex transposition (i j) (and, with --colswap, each swap of two colours whose
patterns are equal), all in the variable order 1..V (sound for any subset of the symmetry group: the lex-least
solution of each orbit satisfies every such constraint; see README.md); (3) blocking clauses "not every edge
of this copy has colour c", one per monochromatic copy found, added lazily (CEGAR): solve, search the model for
monochromatic copies, add their clauses, repeat. Copies are never removed, so the final CNF is a subset of the
full encoding plus (2): UNSAT of the final CNF implies UNSAT of the full problem.

Usage: python -I cegar.py --n 17 --pats F3,F4 --tag r_f3f4_n17 [--sb all|adj|none] [--colswap] [--full 0,1]
       [--maxadd 4000] [--tl 3600] [--solver cadical195]
Writes runs/<tag>.cnf (final clause set, UNSAT or SAT), runs/<tag>.json, and runs/<tag>.col when SAT.
"""
import argparse, ctypes, hashlib, json, os, sys, time
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pat import pattern, bfs_order  # noqa: E402
from pysat.solvers import Solver  # noqa: E402

LIB = ctypes.CDLL(os.path.join(HERE, "sgfind.so"))
LIB.find_copies.restype = ctypes.c_int


def edge_index(n):
    idx = {}
    e = 0
    for u in range(n):
        for v in range(u + 1, n):
            idx[(u, v)] = e
            e += 1
    return idx


class Enc:
    def __init__(self, n, pats):
        self.n, self.k = n, len(pats)
        self.idx = edge_index(n)
        self.E = len(self.idx)
        self.V = self.E if self.k == 2 else self.E * self.k
        self.top = self.V
        self.pats = []
        for name in pats:
            h, edges = pattern(name)
            order, adj = bfs_order(h, edges)
            pos = {v: i for i, v in enumerate(order)}
            pre = []
            for i, v in enumerate(order):
                m = 0
                for w in adj[v]:
                    if pos[w] < i:
                        m |= 1 << pos[w]
                pre.append(m)
            # edges in position coordinates
            pedges = [(pos[a], pos[b]) for a, b in edges]
            self.pats.append(dict(name=name, h=h, pre=pre, pedges=pedges))

    def var(self, u, v, c):
        if u > v:
            u, v = v, u
        e = self.idx[(u, v)]
        return e + 1 if self.k == 2 else e * self.k + c + 1

    def lit_block(self, u, v, c):
        """literal that is true when edge uv does NOT have colour c"""
        if self.k == 2:
            return -(self.idx[(min(u, v), max(u, v))] + 1) if c == 0 else (self.idx[(min(u, v), max(u, v))] + 1)
        return -self.var(u, v, c)

    def onehot(self):
        cl = []
        if self.k == 2:
            return cl
        for e in range(self.E):
            vs = [e * self.k + c + 1 for c in range(self.k)]
            cl.append(vs)
            for a, b in combinations(vs, 2):
                cl.append([-a, -b])
        return cl

    def sigma_vertex(self, i, j):
        """variable permutation induced by the vertex transposition (i j), as a list s[1..V]"""
        n, k = self.n, self.k
        s = [0] * (self.V + 1)
        def t(x):
            return j if x == i else (i if x == j else x)
        for (u, v), e in self.idx.items():
            a, b = t(u), t(v)
            for c in range(1 if k == 2 else k):
                s[self.var(u, v, c)] = self.var(a, b, c)
        return s

    def sigma_colour(self, c1, c2):
        s = [0] * (self.V + 1)
        for (u, v), e in self.idx.items():
            for c in range(self.k):
                cc = c2 if c == c1 else (c1 if c == c2 else c)
                s[self.var(u, v, c)] = self.var(u, v, cc)
        return s

    def lex_leader(self, s, maxlen=None):
        """CNF for x <=_lex sigma(x): positions p = 1..V in order, a_p = x_p, b_p = x_{s[p]}; fixed positions skipped."""
        pos = [p for p in range(1, self.V + 1) if s[p] != p]
        if maxlen:
            pos = pos[:maxlen]
        cl = []
        y = None  # y = 'prefix equal so far' (None means true)
        for t, p in enumerate(pos):
            a, b = p, s[p]
            pre = [] if y is None else [-y]
            cl.append(pre + [-a, b])
            if t == len(pos) - 1:
                break
            self.top += 1
            yn = self.top
            cl.append(pre + [-a, -b, yn])
            cl.append(pre + [a, b, yn])
            y = yn
        return cl

    def sb(self, mode, colswap):
        cl = []
        if mode != "none":
            pairs = [(i, i + 1) for i in range(self.n - 1)] if mode == "adj" else list(combinations(range(self.n), 2))
            for i, j in pairs:
                cl += self.lex_leader(self.sigma_vertex(i, j))
        # k = 2: complementation is not a variable permutation and is not used (fixing a colour would clash
        # with the lex-least choice); only colour swaps for k >= 3 are used.
        if colswap and self.k >= 3:
            for c1, c2 in combinations(range(self.k), 2):
                if self.pats[c1]["name"] == self.pats[c2]["name"]:
                    cl += self.lex_leader(self.sigma_colour(c1, c2))
        return cl

    def adjbits(self, model_set):
        n, k = self.n, self.k
        adj = [[0] * n for _ in range(k)]
        for (u, v), e in self.idx.items():
            if k == 2:
                c = 0 if (e + 1) in model_set else 1
            else:
                c = next(c for c in range(k) if (e * k + c + 1) in model_set)
            adj[c][u] |= 1 << v
            adj[c][v] |= 1 << u
        return adj

    def colour_matrix(self, model_set):
        n, k = self.n, self.k
        M = [["-"] * n for _ in range(n)]
        for (u, v), e in self.idx.items():
            if k == 2:
                c = 0 if (e + 1) in model_set else 1
            else:
                c = next(c for c in range(k) if (e * k + c + 1) in model_set)
            M[u][v] = M[v][u] = str(c)
        return M

    def copies(self, adj, c, maxout, percap, start):
        P = self.pats[c]
        n, h = self.n, P["h"]
        A = (ctypes.c_uint64 * n)(*adj)
        pre = (ctypes.c_uint32 * h)(*P["pre"])
        out = (ctypes.c_int * (maxout * h))()
        m = LIB.find_copies(n, A, h, pre, maxout, percap, start, out)
        res = []
        for t in range(m):
            img = out[t * h:(t + 1) * h]
            res.append(tuple(sorted(self.lit_block(img[a], img[b], c) for a, b in P["pedges"])))
        return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--pats", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--sb", default="all")
    ap.add_argument("--colswap", action="store_true")
    ap.add_argument("--full", default="")
    ap.add_argument("--maxadd", type=int, default=4000)
    ap.add_argument("--percap", type=int, default=50)
    ap.add_argument("--tl", type=float, default=3600)
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--rundir", default=os.path.join(os.path.dirname(HERE), "runs"))
    a = ap.parse_args()
    pats = a.pats.split("/") if "/" in a.pats else a.pats.split(",")
    enc = Enc(a.n, pats)
    t0 = time.time()
    base = enc.onehot() + enc.sb(a.sb, a.colswap)
    nbase = len(base)
    seen = set()
    blocks = []
    full_cols = [int(c) for c in a.full.split(",") if c != ""]
    allones = (1 << a.n) - 1
    import re as _re
    for c in [c for c in full_cols if _re.fullmatch(r"K1,(\d+)", enc.pats[c]["name"])]:
        t = int(_re.fullmatch(r"K1,(\d+)", enc.pats[c]["name"]).group(1))
        for v in range(a.n):              # a star K_{1,t}: a centre and a t-set of leaves (no automorphism images)
            for leaves in combinations([u for u in range(a.n) if u != v], t):
                cl = tuple(sorted(enc.lit_block(v, u, c) for u in leaves))
                if cl not in seen:
                    seen.add(cl)
                    blocks.append(list(cl))
    full_cols = [c for c in full_cols if not _re.fullmatch(r"K1,(\d+)", enc.pats[c]["name"])]
    for c in [c for c in full_cols if _re.fullmatch(r"K(\d+),(\d+)", enc.pats[c]["name"])]:
        ka, kb = map(int, _re.fullmatch(r"K(\d+),(\d+)", enc.pats[c]["name"]).groups())
        for A in combinations(range(a.n), ka):   # K_{ka,kb}, ka >= 2: a ka-set A and a kb-set B off A; every
            rest = [u for u in range(a.n) if u not in A]   # copy is the complete bipartite edge set A x B
            for B in combinations(rest, kb):
                if ka == kb and B[0] < A[0]:
                    continue                      # A x B = B x A: count each copy once
                cl = tuple(sorted(enc.lit_block(u, v, c) for u in A for v in B))
                if cl not in seen:
                    seen.add(cl)
                    blocks.append(list(cl))
    full_cols = [c for c in full_cols if not _re.fullmatch(r"K(\d+),(\d+)", enc.pats[c]["name"])]
    for c in full_cols:
        adj = [allones & ~(1 << v) for v in range(a.n)]
        h = enc.pats[c]["h"]
        per_root = 1
        for i in range(1, h):
            per_root *= (a.n - i)          # monomorphisms with a fixed root
        for r in range(a.n):               # one root at a time keeps the buffer small
            for cl in enc.copies(adj, c, per_root, per_root, -r - 1):
                if cl not in seen:
                    seen.add(cl)
                    blocks.append(list(cl))
    S = Solver(name=a.solver, bootstrap_with=base + blocks)
    it = 0
    status = None
    log = open(os.path.join(a.rundir, a.tag + ".log"), "a")
    print(f"START {a.tag} n={a.n} pats={pats} sb={a.sb} colswap={a.colswap} base={nbase} full={len(blocks)} "
          f"{time.strftime('%F %T')}", file=log, flush=True)
    model_set = None
    while True:
        if time.time() - t0 > a.tl:
            status = "TIMEOUT"
            break
        ok = S.solve()
        it += 1
        if not ok:
            status = "UNSAT"
            break
        model = S.get_model()
        model_set = set(l for l in model if l > 0)
        adj = enc.adjbits(model_set)
        new = 0
        for c in range(enc.k):
            for cl in enc.copies(adj[c], c, a.maxadd, a.percap, it % a.n):
                if cl not in seen:
                    seen.add(cl)
                    blocks.append(list(cl))
                    S.add_clause(list(cl))
                    new += 1
        if it % 50 == 0 or new == 0:
            print(f"it={it} blocks={len(blocks)} new={new} t={time.time()-t0:.1f}", file=log, flush=True)
        if new == 0:
            status = "SAT"
            break
    dt = time.time() - t0
    cnf = os.path.join(a.rundir, a.tag + ".cnf")
    allcl = base + blocks
    with open(cnf, "w") as f:
        f.write(f"c ramsey-exact cegar n={a.n} pats={a.pats} sb={a.sb} colswap={a.colswap} base={nbase} "
                f"blocks={len(blocks)} status={status}\n")
        f.write(f"p cnf {enc.top} {len(allcl)}\n")
        for cl in allcl:
            f.write(" ".join(map(str, cl)) + " 0\n")
    sha = hashlib.sha256(open(cnf, "rb").read()).hexdigest()
    info = dict(tag=a.tag, n=a.n, pats=pats, k=enc.k, sb=a.sb, colswap=a.colswap, nvars=enc.top, nbase=nbase,
                nblocks=len(blocks), iterations=it, status=status, seconds=round(dt, 1), cnf_sha256=sha,
                solver=a.solver)
    if status == "SAT":
        M = enc.colour_matrix(model_set)
        col = os.path.join(a.rundir, a.tag + ".col")
        with open(col, "w") as f:
            f.write(f"{a.n} {enc.k}\n")
            for row in M:
                f.write("".join(row) + "\n")
        info["col_sha256"] = hashlib.sha256(open(col, "rb").read()).hexdigest()
    json.dump(info, open(os.path.join(a.rundir, a.tag + ".json"), "w"), indent=1)
    print(f"END {json.dumps(info)}", file=log, flush=True)
    print(json.dumps(info))


if __name__ == "__main__":
    main()
