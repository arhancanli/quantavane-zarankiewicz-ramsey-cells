"""check_char.py: second colouring checker, written apart from checks/qvr.c and from the search code.
It tests each colour class for the pattern through a characterisation of the pattern, not a generic embedding:
  Kk      a k-clique (recursive common-neighbourhood extension)
  Kk-e    a pair u, v whose common neighbourhood holds a (k-2)-clique
  Ck      a cycle of length k (depth-first search over simple paths from their smallest vertex)
  Pk      a path on k vertices
  Wn      a vertex whose neighbourhood graph holds a cycle of length n-1
  Bn      an edge whose ends have at least n common neighbours
  Fn      a vertex whose neighbourhood graph has a matching of size n
  Ka,b    a set of a vertices (a <= b) with at least b common neighbours
Usage: python3 -I check_char.py COLFILE P0/P1[/P2...]     prints PASS or FAIL (exit code 0 / 1)
"""
import re
import sys
from itertools import combinations


def read_col(path):
    with open(path) as f:
        n, k = map(int, f.readline().split())
        rows = [f.readline().strip() for _ in range(n)]
    for i, r in enumerate(rows):
        assert len(r) == n, "row length"
        assert r[i] == "-", "diagonal"
    for i in range(n):
        for j in range(n):
            if i != j:
                assert rows[i][j] == rows[j][i], "symmetry"
                assert 0 <= int(rows[i][j]) < k, "colour range"
    return n, k, rows


def has_clique(cands, N, size):
    if size == 0:
        return True
    cands = list(cands)
    for i, v in enumerate(cands):
        if has_clique(set(cands[i + 1:]) & N[v], N, size - 1):
            return True
    return False


def has_cycle(verts, N, L):
    verts = sorted(verts)
    vs = set(verts)
    for s in verts:
        allowed = {v for v in vs if v > s}

        def dfs(v, depth, seen):
            if depth == L:
                return s in N[v]
            for w in N[v] & allowed:
                if w not in seen:
                    seen.add(w)
                    if dfs(w, depth + 1, seen):
                        return True
                    seen.discard(w)
            return False
        if dfs(s, 1, {s}):
            return True
    return False


def has_path(verts, N, L):
    for s in verts:
        def dfs(v, depth, seen):
            if depth == L:
                return True
            for w in N[v]:
                if w not in seen:
                    seen.add(w)
                    if dfs(w, depth + 1, seen):
                        return True
                    seen.discard(w)
            return False
        if dfs(s, 1, {s}):
            return True
    return False


def matching_at_least(verts, N, m):
    verts = sorted(verts)
    if m == 0:
        return True
    if len(verts) < 2 * m:
        return False
    u, rest = verts[0], verts[1:]
    # u unmatched
    if matching_at_least(rest, N, m):
        return True
    for w in N[u]:
        if w in rest:
            if matching_at_least([x for x in rest if x != w], N, m - 1):
                return True
    return False


def contains(name, n, N):
    V = range(n)
    m = re.fullmatch(r"K(\d+),(\d+)", name)
    if m:
        a, b = sorted((int(m.group(1)), int(m.group(2))))
        for A in combinations(V, a):
            C = set(V)
            for x in A:
                C &= N[x]
            if len(C) >= b:
                return True
        return False
    m = re.fullmatch(r"K(\d+)-e", name)
    if m:
        k = int(m.group(1))
        for u, v in combinations(V, 2):
            if has_clique(N[u] & N[v], N, k - 2):
                return True
        return False
    m = re.fullmatch(r"K(\d+)", name)
    if m:
        return has_clique(set(V), N, int(m.group(1)))
    m = re.fullmatch(r"C(\d+)", name)
    if m:
        return has_cycle(V, N, int(m.group(1)))
    m = re.fullmatch(r"P(\d+)", name)
    if m:
        return has_path(V, N, int(m.group(1)))
    m = re.fullmatch(r"W(\d+)", name)
    if m:
        r = int(m.group(1)) - 1
        for v in V:
            sub = N[v]
            Nsub = {x: N[x] & sub for x in sub}
            NN = [set() for _ in V]
            for x in sub:
                NN[x] = Nsub[x]
            if has_cycle(sub, NN, r):
                return True
        return False
    m = re.fullmatch(r"B(\d+)", name)
    if m:
        b = int(m.group(1))
        return any(len(N[u] & N[v]) >= b for u, v in combinations(V, 2) if v in N[u])
    m = re.fullmatch(r"F(\d+)", name)
    if m:
        f = int(m.group(1))
        for v in V:
            sub = N[v]
            NN = [N[x] & sub for x in V]
            if matching_at_least(sub, NN, f):
                return True
        return False
    raise ValueError(name)


def main():
    path, pats = sys.argv[1], sys.argv[2]
    names = pats.split("/") if "/" in pats else pats.split(",")
    n, k, rows = read_col(path)
    assert k == len(names), "colours vs patterns"
    bad = False
    for c in range(k):
        N = [set(j for j in range(n) if j != i and int(rows[i][j]) == c) for i in range(n)]
        ne = sum(len(x) for x in N) // 2
        if contains(names[c], n, N):
            print(f"colour {c} ({ne} edges): CONTAINS {names[c]}")
            bad = True
        else:
            print(f"colour {c} ({ne} edges): no {names[c]}")
    print("FAIL" if bad else f"PASS n={n}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
