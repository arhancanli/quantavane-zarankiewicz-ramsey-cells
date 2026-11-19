"""zsizes.py: case split for the type form by size profile. Lists every (b_s, ..., b_m) (b_k = number of big
columns of size k) with sum_k (k-s+1) b_k = K - (s-1) n, sum_k b_k <= n, sum_k C(k,s) b_k <= (t-1) C(m,s) and
b_k <= (t-1) C(m,k). One comma list per line, recursion from k = m down to k = s.
Optional 6th argument CMIN (deletion pruning): if CMIN > s-1, every column has at least CMIN ones, so b_k = 0 for k < CMIN
and sum_k b_k = n (no columns of size s-1). Sound when CMIN <= K - Z' for an upper bound Z' >= z(m,n-1;s,t): a matrix
with exactly K ones and a column of fewer than K - Z' ones would leave more than Z' ones after deleting that column.
Usage: python3 -I zsizes.py m n s t K [CMIN]"""
import sys
from math import comb
m, n, s, t, K = map(int, sys.argv[1:6])
CMIN = int(sys.argv[6]) if len(sys.argv) > 6 else 0
R, B = K - (s - 1) * n, (t - 1) * comb(m, s)
out, b = [], {}


def rec(k, rem, cols, cov):
    if k < s:
        if rem == 0 and (CMIN <= s - 1 or cols == n):
            out.append(",".join(str(b[j]) for j in range(s, m + 1)))
        return
    w = k - s + 1
    hi = min((t - 1) * comb(m, k), rem // w, n - cols) if k >= CMIN else 0
    for x in range(0, hi + 1):
        c = cov + comb(k, s) * x
        if c > B:
            break
        b[k] = x
        rec(k - 1, rem - w * x, cols + x, c)


if R >= 0:
    rec(m, R, 0, 0)
if out:
    print("\n".join(out))
