/* ztype.c (encoder B, column-type form): writes the CNF specified in tools/ztype.py's header from its own code.
   Usage: ztype m n s t K OUT.cnf [pts|none [SP]] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int *buf; static long blen, bcap, ncl, top;
static void push(int v) { if (blen == bcap) { bcap = bcap ? 2 * bcap : 1 << 20; buf = realloc(buf, bcap * sizeof(int)); if (!buf) exit(2); } buf[blen++] = v; }
static void endc(void) { push(0); ncl++; }

/* at most Kp of lits[0..L-1] (Sinz), registers from top+1 */
static void atmost(const int *lits, long L, long Kp) {
  if (L <= Kp) return;
  long rb = top + 1;
#define RG(a, b) ((int)(rb + (long)(a) * Kp + (b)))
  push(-lits[0]); push(RG(0, 0)); endc();
  for (long b = 1; b < Kp; b++) { push(-RG(0, b)); endc(); }
  for (long a = 1; a <= L - 2; a++) {
    push(-lits[a]); push(RG(a, 0)); endc();
    push(-RG(a - 1, 0)); push(RG(a, 0)); endc();
    for (long b = 1; b < Kp; b++) {
      push(-lits[a]); push(-RG(a - 1, b - 1)); push(RG(a, b)); endc();
      push(-RG(a - 1, b)); push(RG(a, b)); endc();
    }
    push(-lits[a]); push(-RG(a - 1, Kp - 1)); endc();
  }
  push(-lits[L - 1]); push(-RG(L - 2, Kp - 1)); endc();
  top += (L - 1) * Kp;
#undef RG
}

int main(int argc, char **argv) {
  if (argc < 7) { fprintf(stderr, "usage: ztype m n s t K OUT\n"); return 2; }
  int m = atoi(argv[1]), n = atoi(argv[2]), s = atoi(argv[3]), t = atoi(argv[4]); long K = atol(argv[5]);
  int D = t - 1;
  int *types = malloc(sizeof(int) << m); int nt = 0;
  for (int x = 0; x < (1 << m); x++) if (__builtin_popcount(x) >= s) types[nt++] = x;
  top = (long)nt * D;
  for (int tau = 0; tau < nt; tau++) for (int k = 1; k < D; k++) { push(-(tau * D + k + 1)); push(tau * D + k); endc(); }
  int *L = malloc(sizeof(int) * (long)nt * D + 8);
  for (int Q = 0; Q < (1 << m); Q++) {
    if (__builtin_popcount(Q) != s) continue;
    long len = 0;
    for (int tau = 0; tau < nt; tau++) if ((types[tau] & Q) == Q) for (int k = 1; k <= D; k++) L[len++] = tau * D + k;
    atmost(L, len, D);
  }
  long nu = (long)nt * D;
  const char *sps = argc > 8 ? argv[8] : "-";
  if (!strcmp(sps, "-")) {
  if (nu > n) { for (long i = 0; i < nu; i++) L[i] = (int)(i + 1); atmost(L, nu, n); }
  long R = K - (long)(s - 1) * n;
  if (R > 0) {
    long wl = 0;
    for (int tau = 0; tau < nt; tau++) wl += (long)(__builtin_popcount(types[tau]) - s + 1) * D;
    int *W = malloc(sizeof(int) * (wl + 1)); long p = 0;
    for (int tau = 0; tau < nt; tau++) { int w = __builtin_popcount(types[tau]) - s + 1; for (int k = 1; k <= D; k++) for (int r = 0; r < w; r++) W[p++] = tau * D + k; }
    if (R > wl) { endc(); }
    else {
      long *gs = malloc(sizeof(long) * (wl + 1));
      for (long q = 0; q < wl; q++) { gs[q] = top + 1; top += (q + 1 < R) ? q + 1 : R; }
#define G(pp, qq) ((int)(gs[pp] + (qq) - 1))
      for (long pp = 0; pp < wl; pp++) {
        long w = (pp + 1 < R) ? pp + 1 : R;
        for (long qq = 1; qq <= w; qq++) {
          int g = G(pp, qq);
          if (qq <= pp) { push(-g); push(G(pp - 1, qq)); push(W[pp]); endc(); } else { push(-g); push(W[pp]); endc(); }
          if (qq >= 2) { push(-g); push(G(pp - 1, qq - 1)); endc(); }
        }
      }
      push(G(wl - 1, R)); endc();
#undef G
    }
  }
  } else {
    /* (3'),(4') size profile: exactly b_k u-bits among the types of size k, k = s..m */
    const char *pp = sps;
    for (int size = s; size <= m; size++) {
      long bk = strtol(pp, (char **)&pp, 10); if (*pp == ',') pp++;
      long len = 0;
      for (int tau = 0; tau < nt; tau++) if (__builtin_popcount(types[tau]) == size) for (int k = 1; k <= D; k++) L[len++] = tau * D + k;
      if (bk == 0) { for (long i = 0; i < len; i++) { push(-L[i]); endc(); } continue; }
      atmost(L, len, bk);
      if (bk > len) { endc(); continue; }
      long *gs = malloc(sizeof(long) * (len + 1));
      for (long q = 0; q < len; q++) { gs[q] = top + 1; top += (q + 1 < bk) ? q + 1 : bk; }
#define G2(p2, q2) ((int)(gs[p2] + (q2) - 1))
      for (long p2 = 0; p2 < len; p2++) {
        long w = (p2 + 1 < bk) ? p2 + 1 : bk;
        for (long q2 = 1; q2 <= w; q2++) {
          int g = G2(p2, q2);
          if (q2 <= p2) { push(-g); push(G2(p2 - 1, q2)); push(L[p2]); endc(); } else { push(-g); push(L[p2]); endc(); }
          if (q2 >= 2) { push(-g); push(G2(p2 - 1, q2 - 1)); endc(); }
        }
      }
      push(G2(len - 1, bk)); endc();
#undef G2
      free(gs);
    }
  }
  int pts = argc > 7 && (!strcmp(argv[7], "pts") || !strcmp(argv[7], "ptsr"));
  int rev = argc > 7 && !strcmp(argv[7], "ptsr");
  if (pts) {
    int *pos = malloc(sizeof(int) << m); for (int x = 0; x < (1 << m); x++) pos[x] = -1;
    for (int tau = 0; tau < nt; tau++) pos[types[tau]] = tau;
    long *pa = malloc(sizeof(long) * (nu + 1)), *pb = malloc(sizeof(long) * (nu + 1));
    for (int i = 0; i < m; i++) for (int j = i + 1; j < m; j++) {
      long L2 = 0;
      for (int tau = 0; tau < nt; tau++) {
        int x = types[tau], y = x;
        if (((x >> i) & 1) != ((x >> j) & 1)) y = x ^ (1 << i) ^ (1 << j);
        int st = pos[y];
        for (int k = 1; k <= D; k++) { long p = (long)tau * D + k, q = (long)st * D + k; if (p < q) { pa[L2] = p; pb[L2] = q; L2++; } }
      }
      if (L2 == 0) continue;
      long y0 = top; top += L2 - 1;   /* y_t = y0 + t, t = 1..L2-1 */
      for (long t2 = 0; t2 < L2; t2++) {
        int a = (int)pa[t2], b = (int)pb[t2];
        if (t2 == 0) { if (rev) { push(a); push(-b); } else { push(-a); push(b); } endc(); if (L2 > 1) { push(-a); push(-b); push((int)(y0 + 1)); endc(); push(a); push(b); push((int)(y0 + 1)); endc(); } }
        else {
          int yt = (int)(y0 + t2);
          push(-yt); if (rev) { push(a); push(-b); } else { push(-a); push(b); } endc();
          if (t2 < L2 - 1) { push(-yt); push(-a); push(-b); push((int)(y0 + t2 + 1)); endc(); push(-yt); push(a); push(b); push((int)(y0 + t2 + 1)); endc(); }
        }
      }
    }
  }
  long rmin = argc > 9 ? atol(argv[9]) : 0;
  if (rmin > 0) {
    long *Lp = malloc(sizeof(long) * (nu + 1));
    for (int pt = 0; pt < m; pt++) {
      long len = 0;
      for (int tau = 0; tau < nt; tau++) if ((types[tau] >> pt) & 1) for (int k = 1; k <= D; k++) Lp[len++] = (long)tau * D + k;
      if (rmin > len) { endc(); continue; }
      long *gs = malloc(sizeof(long) * (len + 1));
      for (long q = 0; q < len; q++) { gs[q] = top + 1; top += (q + 1 < rmin) ? q + 1 : rmin; }
#define G3(p3, q3) ((int)(gs[p3] + (q3) - 1))
      for (long p3 = 0; p3 < len; p3++) {
        long w = (p3 + 1 < rmin) ? p3 + 1 : rmin;
        for (long q3 = 1; q3 <= w; q3++) {
          int g = G3(p3, q3);
          if (q3 <= p3) { push(-g); push(G3(p3 - 1, q3)); push((int)Lp[p3]); endc(); } else { push(-g); push((int)Lp[p3]); endc(); }
          if (q3 >= 2) { push(-g); push(G3(p3 - 1, q3 - 1)); endc(); }
        }
      }
      push(G3(len - 1, rmin)); endc();
#undef G3
      free(gs);
    }
  }
  FILE *f = fopen(argv[6], "w"); if (!f) return 2;
  fprintf(f, "c ztype m=%d n=%d s=%d t=%d K=%ld%s%s%s", m, n, s, t, K, pts ? (rev ? " sb=ptsr" : " sb=pts") : "", strcmp(sps, "-") ? " sp=" : "", strcmp(sps, "-") ? sps : "");
  if (rmin > 0) fprintf(f, " rmin=%ld", rmin);
  fprintf(f, "\n");
  fprintf(f, "p cnf %ld %ld\n", top, ncl);
  for (long i = 0; i < blen;) {
    int first = 1;
    while (buf[i] != 0) { fprintf(f, first ? "%d" : " %d", buf[i]); first = 0; i++; }
    fprintf(f, first ? "0\n" : " 0\n"); i++;
  }
  fclose(f);
  printf("types=%d vars=%ld clauses=%ld\n", nt, top, ncl);
  return 0;
}
