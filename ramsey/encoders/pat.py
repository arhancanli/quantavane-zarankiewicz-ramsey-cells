"""Pattern graphs for the ramsey-exact search side (encoder A).

Names: Kk, Kk-e, Ck, Pk (k vertices), Wn (n vertices: hub + C_{n-1}), Bn (K_2 + nK_1, n+2 vertices),
Fn (K_1 + nK_2, 2n+1 vertices), Km,n (complete bipartite), K1,n (star).
Returns (h, edges) with vertices 0..h-1. The checkers in checks/ parse names on their own.
"""
import re


def pattern(name):
    s = name.strip()
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
    m = re.fullmatch(r"C(\d+)", s)
    if m:
        k = int(m.group(1))
        return k, [(i, (i + 1) % k) for i in range(k)]
    m = re.fullmatch(r"P(\d+)", s)
    if m:
        k = int(m.group(1))
        return k, [(i, i + 1) for i in range(k - 1)]
    m = re.fullmatch(r"W(\d+)", s)
    if m:
        n = int(m.group(1))
        r = n - 1
        return n, [(0, i) for i in range(1, n)] + [(1 + i, 1 + (i + 1) % r) for i in range(r)]
    m = re.fullmatch(r"B(\d+)", s)
    if m:
        n = int(m.group(1))
        return n + 2, [(0, 1)] + [(0, i) for i in range(2, n + 2)] + [(1, i) for i in range(2, n + 2)]
    m = re.fullmatch(r"F(\d+)", s)
    if m:
        n = int(m.group(1))
        e = []
        for i in range(n):
            a, b = 1 + 2 * i, 2 + 2 * i
            e += [(0, a), (0, b), (a, b)]
        return 2 * n + 1, e
    raise ValueError("unknown pattern " + name)


def bfs_order(h, edges):
    """Order H's vertices so that each vertex after the first has a neighbour earlier (when connected),
    choosing the highest-degree vertex first and then the vertex with most earlier neighbours."""
    adj = [set() for _ in range(h)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    order = [max(range(h), key=lambda v: len(adj[v]))]
    rest = set(range(h)) - set(order)
    while rest:
        v = max(rest, key=lambda u: (len(adj[u] & set(order)), len(adj[u])))
        order.append(v)
        rest.discard(v)
    return order, adj
