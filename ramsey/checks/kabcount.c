/* kabcount.c: second colouring checker for complete bipartite and book patterns, written apart from
   checks/check_char.py and from the search code. For colour c and pattern Ka,b (a <= b; C4 = K2,2) it computes, with
   64-bit adjacency masks and popcounts, the largest number of common colour-c neighbours over all a-sets S (vertices
   outside S); the colour is free of Ka,b iff that maximum is < b. Book Bk: the largest number of common colour-c
   neighbours over pairs uv that are themselves colour-c edges; free iff < k. Star K1,t is Ka,b with a = 1.
   Also checks: square, symmetric, '-' on the diagonal, entries 0..k-1.
   Build: cc -O2 -o kabcount kabcount.c       Usage: kabcount COLFILE P0/P1[/P2]      prints PASS or FAIL */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static int n, k;
static uint64_t adj[8][64];

static int maxcommon(int c, int a, int book, int *witness) {
  int best = -1, S[8];
  for (int i = 0; i < a; i++) S[i] = i;
  if (a > n) return -1;
  for (;;) {
    uint64_t m = ~0ULL;
    if (n < 64) m = (1ULL << n) - 1;
    for (int i = 0; i < a; i++) { m &= adj[c][S[i]]; m &= ~(1ULL << S[i]); }
    int ok = 1;
    if (book) ok = (adj[c][S[0]] >> S[1]) & 1;
    if (ok) { int cnt = __builtin_popcountll(m); if (cnt > best) { best = cnt; for (int i = 0; i < a; i++) witness[i] = S[i]; } }
    int t = a - 1;
    while (t >= 0 && S[t] == n - a + t) t--;
    if (t < 0) break;
    S[t]++;
    for (int u = t + 1; u < a; u++) S[u] = S[u - 1] + 1;
  }
  return best;
}

int main(int argc, char **argv) {
  if (argc != 3) { fprintf(stderr, "usage: kabcount COLFILE P0/P1[/P2]\n"); return 2; }
  FILE *f = fopen(argv[1], "r"); if (!f) { perror(argv[1]); return 2; }
  if (fscanf(f, "%d %d", &n, &k) != 2 || n < 2 || n > 64 || k < 1 || k > 8) { printf("FAIL header\n"); return 1; }
  char row[80]; int M[64][64];
  for (int i = 0; i < n; i++) {
    if (fscanf(f, "%70s", row) != 1 || (int)strlen(row) != n) { printf("FAIL row %d\n", i); return 1; }
    for (int j = 0; j < n; j++) {
      if (i == j) { if (row[j] != '-') { printf("FAIL diagonal %d\n", i); return 1; } M[i][j] = -1; continue; }
      int c = row[j] - '0'; if (c < 0 || c >= k) { printf("FAIL entry %d %d\n", i, j); return 1; }
      M[i][j] = c;
    }
  }
  fclose(f);
  for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (M[i][j] != M[j][i]) { printf("FAIL asymmetric %d %d\n", i, j); return 1; }
  memset(adj, 0, sizeof adj);
  for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (i != j) adj[M[i][j]][i] |= 1ULL << j;
  char pats[256]; snprintf(pats, sizeof pats, "%s", argv[2]);
  int c = 0, bad = 0;
  for (char *tok = strtok(pats, "/"); tok; tok = strtok(NULL, "/"), c++) {
    if (c >= k) { printf("FAIL more patterns than colours\n"); return 1; }
    int a, b, book = 0, x, y;
    if (!strcmp(tok, "C4")) { a = 2; b = 2; }
    else if (tok[0] == 'B') { a = 2; b = atoi(tok + 1); book = 1; }
    else if (sscanf(tok, "K%d,%d", &x, &y) == 2) { a = x < y ? x : y; b = x < y ? y : x; }
    else { printf("FAIL unknown pattern %s\n", tok); return 1; }
    int w[8], e = 0;
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) e += (M[i][j] == c);
    int best = maxcommon(c, a, book, w);
    if (best >= b) { printf("colour %d (%d edges): contains %s (an %s with %d common neighbours)\n", c, e, tok, book ? "edge" : "a-set", best); bad = 1; }
    else printf("colour %d (%d edges): no %s (max common neighbours %d)\n", c, e, tok, best);
  }
  if (c != k) { printf("FAIL %d patterns for %d colours\n", c, k); return 1; }
  printf(bad ? "FAIL\n" : "PASS n=%d\n", n);
  return bad;
}
