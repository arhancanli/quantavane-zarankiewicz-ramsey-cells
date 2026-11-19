/* zsizes2.c (second enumerator for the size-profile split, written apart from tools/zsizes.py): depth-first over
   k = s, s+1, ..., m (ascending, the opposite order of zsizes.py), choosing b_k in [0, min((t-1)C(m,k), n)], pruning
   on the partial weight sum (<= R), column count (<= n) and coverage (<= (t-1) C(m,s)); keeps profiles with
   sum (k-s+1) b_k = R exactly. Prints comma lists b_s..b_m; the caller sorts and compares.
   Optional CMIN (deletion pruning, see tools/zsizes.py): b_k forced to 0 for k < CMIN, and if CMIN > s-1 the profile
   must have exactly n columns.  Usage: zsizes2 m n s t K [CMIN] */
#include <stdio.h>
#include <stdlib.h>
static long C(int a, int k) { if (k < 0 || a < k) return 0; long r = 1; for (int i = 0; i < k; i++) r = r * (a - i) / (i + 1); return r; }
static int m, n, s, t, cmin = 0; static long R, B; static long b[64];
static void go(int k, long w, long cols, long cov) {
  if (k > m) {
    if (w == R && (cmin <= s - 1 || cols == n)) { for (int j = s; j <= m; j++) printf(j > s ? ",%ld" : "%ld", b[j]); printf("\n"); }
    return;
  }
  long cap = (long)(t - 1) * C(m, k); if (cap > n) cap = n; if (k < cmin) cap = 0;
  for (long x = 0; x <= cap; x++) {
    long w2 = w + (long)(k - s + 1) * x, c2 = cols + x, v2 = cov + C(k, s) * x;
    if (w2 > R || c2 > n || v2 > B) break;
    b[k] = x; go(k + 1, w2, c2, v2);
  }
  b[k] = 0;
}
int main(int argc, char **argv) {
  m = atoi(argv[1]); n = atoi(argv[2]); s = atoi(argv[3]); t = atoi(argv[4]); long K = atol(argv[5]);
  if (argc > 6) cmin = atoi(argv[6]);
  R = K - (long)(s - 1) * n; B = (long)(t - 1) * C(m, s);
  if (R < 0) return 0;
  go(s, 0, 0, 0);
  return 0;
}
