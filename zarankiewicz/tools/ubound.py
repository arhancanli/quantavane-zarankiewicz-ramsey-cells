"""ubound.py: counting upper bound for z(m,n;s,t) (Guy's argument A applied to columns and to rows).
Column sums c_j: each column with c ones holds C(c,s) s-sets of rows, and each s-set of rows lies in at most t-1
columns, so sum_j C(c_j, s) <= (t-1) C(m, s).  Row sums r_i: sum_i C(r_i, t) <= (s-1) C(n, t).  By convexity the
largest total W allowed by one inequality is attained by the most balanced sums, so UB = min over the two sides of
max{W : balanced split of W into n parts (each <= m) satisfies the column inequality}, and likewise for rows.
Usage: python3 -I ubound.py m n s t"""
import sys
from math import comb


def side(parts, cap, k, budget):
    best = 0
    for W in range(parts * cap + 1):
        q, r = divmod(W, parts)
        if r * comb(q + 1, k) + (parts - r) * comb(q, k) <= budget:
            best = W
    return best


def ub(m, n, s, t):
    return min(side(n, m, s, (t - 1) * comb(m, s)), side(m, n, t, (s - 1) * comb(n, t)))


if __name__ == "__main__":
    m, n, s, t = map(int, sys.argv[1:5])
    print(ub(m, n, s, t))
