"""ztype.py (encoder A, column-type form): is there a multiset of n subsets of [m] ("columns") in which every
s-subset of [m] lies in at most t-1 members, with total size >= K?  This is z(m,n;s,t) >= K: a 0/1 m x n matrix is
the multiset of its column supports; it has no all-ones s x t block (s rows by t columns) iff every s-set of rows
lies in at most t-1 column supports; columns of size < s are unconstrained, so in an optimal matrix they have size
exactly s-1 (s-1 <= m). Hence, writing B for the number of columns of size >= s ("big"),
   ones = (s-1)(n - B) + sum_big |col|,   and z(m,n;s,t) >= K iff some admissible multiset of big types with
   B <= n has sum_big (|col| - s + 1) >= R := K - (s-1) n.
A big type (support of size >= s) contains an s-set, so its multiplicity is <= t-1.
Usage: python3 -I ztype.py m n s t K OUT.cnf [pts|none [SP [RMIN]]]   SP = "b_s,b_{s+1},...,b_m"; RMIN = row minimum

Exact CNF (checks/ztype.c writes the same file from its own code; SHA-256 must agree):
 Types: the bitmasks 0 .. 2^m - 1 in increasing order with popcount >= s, indexed tau = 0, 1, ...; D = t - 1.
 (1) Variables u(tau,k) = tau*D + k, k = 1..D  (u(tau,k) = "multiplicity of type tau is >= k"); top = (#types)*D.
     If D >= 2: clauses [-u(tau,k+1), u(tau,k)] for tau ascending, k = 1..D-1.
 (2) For each s-set Q of [m] (bitmasks with popcount s, increasing): the list L_Q = u(tau,k) over types tau containing
     Q (tau ascending, k ascending); "at most D of L_Q" by the Sinz counter of tools/zcard.py (4) with K' = D over
     the literal list (registers numbered from top+1, top advanced by (len-1)*D; the K' = 0 case cannot occur, t >= 2).
 (3) If (#types)*D > n: "at most n of all u, in variable order" by the same Sinz counter with K' = n.
 (4) If R > 0: the weighted list W = for tau ascending, for k = 1..D: the literal u(tau,k) repeated |tau|-s+1 times;
     "at least R of W" by the counter of tools/zcard.py (5): g(p,q), p = 0..len-1, q = 1..min(p+1,R), numbered from
     top+1 p-major; clauses [-g(p,q), g(p-1,q), W_p] (q <= p, else [-g(p,q), W_p]), [-g(p,q), g(p-1,q-1)] (q >= 2);
     unit [g(len-1,R)].  If R > len the CNF is the single empty clause after (1)-(3) (written as "0").
Soundness: a matrix with >= K ones and no block gives multiplicities m(tau) <= D, the unary bits u, the counters at
their running values: (1)-(4) hold. A model gives multiplicities with every s-set covered <= D times, B <= n big
columns and weighted sum >= R; adding n - B columns of size s-1 gives an m x n matrix with >= K ones and no block.
 (5) Only with the optional argument "pts": point symmetry breaking. For each transposition sigma = (i j) of [m],
     0 <= i < j < m in lexicographic order: sigma acts on types by swapping bits i and j, and on variables by
     u(tau,k) -> u(sigma tau, k). Positions p = 1 .. #types*D in increasing order with p < sigma(p) give pairs
     (a_t, b_t) = (p, sigma(p)), t = 0..L-1; the chain "a <=_lex b" with prefix variables y_1..y_{L-1} (top+1..):
       t = 0: [-a_0, b_0]; if L > 1: [-a_0, -b_0, y_1], [a_0, b_0, y_1];
       t >= 1: [-y_t, -a_t, b_t]; if t < L-1: [-y_t, -a_t, -b_t, y_{t+1}], [-y_t, a_t, b_t, y_{t+1}].
     This is x <=_lex sigma(x) on the u-vector (positions fixed by sigma compare equal; at a position q = sigma(p) > p
     the comparison repeats the pair at p, so the first difference, if any, is at some p < sigma(p)).
     Soundness: point permutations map admissible multisets to admissible multisets with the same sizes, so the
     u-vector of a solution's orbit has a lex-least member, which satisfies x <=_lex sigma(x) for every sigma in the
     group (Crawford-Ginsberg-Luks-Roy 1996); the counters of (2)-(4) depend only on cardinalities, so that member
     with its counters satisfies the CNF.  Without "pts" no symmetry breaking is used.
     "ptsr": the same chains with x >=_lex sigma(x) instead, i.e.
     the first clause of each step is [-y_t, a_t, -b_t] (resp. [a_0, -b_0]); the lex-GREATEST member of an orbit
     satisfies every such constraint, so soundness is unchanged.
 (3'),(4') Only with a size profile SP = (b_s, ..., b_m): (3) and (4) are replaced by, for each size k = s..m in
     order, "exactly b_k big columns of size k": the list of u-bits of the size-k types (tau ascending, k ascending);
     if b_k = 0 the units [-u]; else "at most b_k" (Sinz as in (2), skipped when the list is not longer than b_k)
     followed by "at least b_k" (the counter of (4) with unit weights; the empty clause if b_k exceeds the list).
     (5) follows unchanged.  Case split (tools/zsizes.py, second enumerator checks/zsizes2.c): any admissible
     multiset with total >= K contains one with total exactly K (delete points from big columns; a column that
     falls below size s becomes a filler of size s-1), whose size profile satisfies sum_k (k-s+1) b_k = K-(s-1)n,
     sum_k b_k <= n and sum_k C(k,s) b_k <= (t-1) C(m,s); so UNSAT for every such profile proves z <= K-1.
 (6) Only with RMIN > 0 (allowed only together with SP with sum_k b_k = n, i.e. no filler columns): for each point
     p = 0..m-1 in order, "at least RMIN of the u-bits of the types containing p" (tau ascending, k ascending), by the
     upward counter of (4); the empty clause if RMIN exceeds the list. Written after (5). Soundness (deletion pruning on
     rows): if Z'' >= z(m-1,n;s,t), a matrix with exactly K ones has every row of size >= K - Z'' (deleting a lighter
     row would leave more than Z'' ones), and with no fillers a row's size is its point's multiplicity-weighted degree.
"""
import sys
from itertools import combinations


def sinz_atmost(lits, Kp, top, cls):
    L = len(lits)
    if L <= Kp:
        return top
    r = lambda a, b: top + 1 + a * Kp + b
    cls.append([-lits[0], r(0, 0)])
    for b in range(1, Kp):
        cls.append([-r(0, b)])
    for a in range(1, L - 1):
        cls.append([-lits[a], r(a, 0)])
        cls.append([-r(a - 1, 0), r(a, 0)])
        for b in range(1, Kp):
            cls.append([-lits[a], -r(a - 1, b - 1), r(a, b)])
            cls.append([-r(a - 1, b), r(a, b)])
        cls.append([-lits[a], -r(a - 1, Kp - 1)])
    cls.append([-lits[L - 1], -r(L - 2, Kp - 1)])
    return top + (L - 1) * Kp


def build(m, n, s, t, K, pts=False, sp=None, rmin=0, rev=False):
    D = t - 1
    types = [x for x in range(1 << m) if bin(x).count("1") >= s]
    u = lambda tau, k: tau * D + k
    top = len(types) * D
    cls = []
    for tau in range(len(types)):
        for k in range(1, D):
            cls.append([-u(tau, k + 1), u(tau, k)])
    for Q in range(1 << m):
        if bin(Q).count("1") != s:
            continue
        L = [u(tau, k) for tau, x in enumerate(types) if x & Q == Q for k in range(1, D + 1)]
        top = sinz_atmost(L, D, top, cls)
    if sp is None:
        allu = list(range(1, len(types) * D + 1))
        if len(allu) > n:
            top = sinz_atmost(allu, n, top, cls)
        R = K - (s - 1) * n
        if R > 0:
            W = []
            for tau, x in enumerate(types):
                w = bin(x).count("1") - s + 1
                for k in range(1, D + 1):
                    W.extend([u(tau, k)] * w)
            if R > len(W):
                cls.append([])
            else:
                g = {}
                for p in range(len(W)):
                    for q in range(1, min(p + 1, R) + 1):
                        top += 1
                        g[(p, q)] = top
                for p in range(len(W)):
                    for q in range(1, min(p + 1, R) + 1):
                        v = g[(p, q)]
                        cls.append([-v, g[(p - 1, q)], W[p]] if q <= p else [-v, W[p]])
                        if q >= 2:
                            cls.append([-v, g[(p - 1, q - 1)]])
                cls.append([g[(len(W) - 1, R)]])
    else:
        # (3'), (4') size profile: for k = s..m, exactly sp[k-s] of the u-bits of types of size k (tau ascending,
        # k ascending): "at most" by sinz_atmost, then "at least" by the upward counter (as in (4), unit weights)
        for size in range(s, m + 1):
            b = sp[size - s]
            Lk = [u(tau, k) for tau, x in enumerate(types) if bin(x).count("1") == size for k in range(1, D + 1)]
            top = sinz_atmost(Lk, b, top, cls) if b > 0 else top
            if b == 0:
                cls.extend([[-v] for v in Lk])
                continue
            if b > len(Lk):
                cls.append([])
                continue
            g = {}
            for p in range(len(Lk)):
                for q in range(1, min(p + 1, b) + 1):
                    top += 1
                    g[(p, q)] = top
            for p in range(len(Lk)):
                for q in range(1, min(p + 1, b) + 1):
                    v = g[(p, q)]
                    cls.append([-v, g[(p - 1, q)], Lk[p]] if q <= p else [-v, Lk[p]])
                    if q >= 2:
                        cls.append([-v, g[(p - 1, q - 1)]])
            cls.append([g[(len(Lk) - 1, b)]])
    if pts:
        idx = {x: tau for tau, x in enumerate(types)}
        for i in range(m):
            for j in range(i + 1, m):
                def sw(x):
                    bi, bj = x >> i & 1, x >> j & 1
                    return x if bi == bj else x ^ (1 << i) ^ (1 << j)
                pairs = []
                for tau, x in enumerate(types):
                    st = idx[sw(x)]
                    for k in range(1, D + 1):
                        p, q = u(tau, k), u(st, k)
                        if p < q:
                            pairs.append((p, q))
                L = len(pairs)
                if L == 0:
                    continue
                y = [None] + [top + t2 for t2 in range(1, L)]
                top += L - 1
                for t2, (a, b) in enumerate(pairs):
                    pre = [] if t2 == 0 else [-y[t2]]
                    cls.append(pre + ([a, -b] if rev else [-a, b]))
                    if t2 < L - 1:
                        cls.append(pre + [-a, -b, y[t2 + 1]])
                        cls.append(pre + [a, b, y[t2 + 1]])
    if rmin > 0:
        assert sp is not None and sum(sp) == n
        for pt in range(m):
            Lp = [u(tau, k) for tau, x in enumerate(types) if x >> pt & 1 for k in range(1, D + 1)]
            if rmin > len(Lp):
                cls.append([])
                continue
            g = {}
            for p in range(len(Lp)):
                for q in range(1, min(p + 1, rmin) + 1):
                    top += 1
                    g[(p, q)] = top
            for p in range(len(Lp)):
                for q in range(1, min(p + 1, rmin) + 1):
                    v = g[(p, q)]
                    cls.append([-v, g[(p - 1, q)], Lp[p]] if q <= p else [-v, Lp[p]])
                    if q >= 2:
                        cls.append([-v, g[(p - 1, q - 1)]])
            cls.append([g[(len(Lp) - 1, rmin)]])
    return top, cls, types


def main():
    m, n, s, t, K = map(int, sys.argv[1:6])
    pts = len(sys.argv) > 7 and sys.argv[7] in ("pts", "ptsr")
    rev = len(sys.argv) > 7 and sys.argv[7] == "ptsr"
    sps = sys.argv[8] if len(sys.argv) > 8 else "-"
    sp = None if sps == "-" else [int(a) for a in sps.split(",")]
    assert sp is None or len(sp) == m - s + 1
    rmin = int(sys.argv[9]) if len(sys.argv) > 9 else 0
    top, cls, types = build(m, n, s, t, K, pts, sp, rmin, rev)
    with open(sys.argv[6], "w") as f:
        f.write(f"c ztype m={m} n={n} s={s} t={t} K={K}{(' sb=ptsr' if rev else ' sb=pts') if pts else ''}{' sp=' + sps if sp is not None else ''}{' rmin=' + str(rmin) if rmin > 0 else ''}\n")
        f.write(f"p cnf {top} {len(cls)}\n")
        for c in cls:
            f.write((" ".join(map(str, c)) + " 0\n") if c else "0\n")
    print(f"types={len(types)} vars={top} clauses={len(cls)}")


if __name__ == "__main__":
    main()
