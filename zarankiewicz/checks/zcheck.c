/* zcheck.c (witness checker 1, written apart from the encoders): reads an m x n 0/1 matrix (one row per line,
   characters '0'/'1', other characters ignored, blank lines ignored) and S T. Reports the number of ones and
   whether some S rows have T or more common columns (an S x T all-ones submatrix, S rows by T columns), by
   enumerating every S-set of rows with 64-bit column masks (n <= 64) and popcount of the AND.
   Usage: zcheck FILE S T [K]   -> prints "PASS m n ones" if no S x T block (and ones >= K when K given), else FAIL. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static uint64_t rowm[256]; static int m = 0, n = -1;
static int S, T; static long bad = 0; static int badrows[16]; static uint64_t badmask;

static void rec(int start, int depth, uint64_t acc) {
  if (bad) return;
  if (__builtin_popcountll(acc) < T) return;           /* prune: fewer than T common columns already */
  if (depth == S) { bad = 1; badmask = acc; return; }
  for (int i = start; i < m; i++) { badrows[depth] = i; rec(i + 1, depth + 1, acc & rowm[i]); if (bad) return; }
}

int main(int argc, char **argv) {
  if (argc < 4) { fprintf(stderr, "usage: zcheck FILE S T [K]\n"); return 2; }
  FILE *f = fopen(argv[1], "r"); if (!f) { perror("open"); return 2; }
  S = atoi(argv[2]); T = atoi(argv[3]); long K = argc > 4 ? atol(argv[4]) : -1;
  char line[4096]; long ones = 0;
  while (fgets(line, sizeof line, f)) {
    int len = 0; uint64_t mask = 0;
    for (char *p = line; *p; p++) {
      if (*p == '0' || *p == '1') { if (len >= 64) { fprintf(stderr, "n > 64\n"); return 2; } if (*p == '1') { mask |= 1ULL << len; ones++; } len++; }
    }
    if (len == 0) continue;
    if (n < 0) n = len; else if (len != n) { printf("FAIL ragged row %d\n", m); return 1; }
    if (m >= 256) { fprintf(stderr, "m > 256\n"); return 2; }
    rowm[m++] = mask;
  }
  fclose(f);
  uint64_t all = (n == 64) ? ~0ULL : ((1ULL << n) - 1);
  rec(0, 0, all);
  if (bad) {
    printf("FAIL %dx%d block: rows", S, T);
    for (int a = 0; a < S; a++) printf(" %d", badrows[a]);
    printf(" columns");
    for (int j = 0; j < n; j++) if (badmask >> j & 1) printf(" %d", j);
    printf("\n"); return 1;
  }
  if (K >= 0 && ones < K) { printf("FAIL ones=%ld < K=%ld\n", ones, K); return 1; }
  printf("PASS m=%d n=%d ones=%ld no %dx%d all-ones block\n", m, n, ones, S, T);
  return 0;
}
