/* kabcard.c (encoder B for tools/kab_card.py): writes, from its own code, the CNF "2-colouring of K_n with no
   colour-0 K_{a0,b0} and no colour-1 K_{a1,b1}" in the exact form documented in tools/kab_card.py, so that the two
   files can be compared byte for byte (SHA-256).
   Build: cc -O2 -o kabcard kabcard.c      Usage: kabcard N P0/P1 OUT.cnf     (P = Ka,b, C4 or Bk = K2 + kK1)
   Layout: edge variables 1..E (row-major u < v; true = colour 0); lex-leader comparator clauses for every vertex
   transposition (i j), i < j row-major, scheme x <=_lex sigma(x) over the variables 1..E in order (for each moved
   position p in increasing order with q = sigma(p): [-y, -p, q], and unless p is the last moved position,
   new y': [-y, -p, -q, y'], [-y, p, q, y'], where "-y" is absent before the first position); then per colour c
   and per a-set S (lexicographic) the AND auxiliaries and a Sinz "at most b-1" counter. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int N, E, TOP;
static int VID[64][64];
static FILE *OUT;
static long NCL;
static int PASS; /* 0 = count only, 1 = write */

static void put(const int *l, int len) {
  NCL++;
  if (!PASS) return;
  for (int i = 0; i < len; i++) fprintf(OUT, "%d ", l[i]);
  fprintf(OUT, "0\n");
}
static void put2(int a, int b) { int l[2] = {a, b}; put(l, 2); }
static void put3(int a, int b, int c) { int l[3] = {a, b, c}; put(l, 3); }

static int BOOK[2];
static void ab(const char *s, int *a, int *b, int *book) {
  *book = 0;
  if (!strcmp(s, "C4")) { *a = 2; *b = 2; return; }
  if (s[0] == 'B') { *a = 2; *b = atoi(s + 1); *book = 1; if (*b < 1) { fprintf(stderr, "bad pattern %s\n", s); exit(2); } return; }
  int x, y;
  if (sscanf(s, "K%d,%d", &x, &y) != 2) { fprintf(stderr, "bad pattern %s\n", s); exit(2); }
  *a = x < y ? x : y; *b = x < y ? y : x;
}

static void lexleader_transposition(int i, int j) {
  /* sigma on edge variables induced by swapping vertices i and j */
  int moved = 0, y = 0;
  int *perm = malloc((E + 1) * sizeof(int));
  for (int u = 0; u < N; u++)
    for (int v = u + 1; v < N; v++) {
      int pu = (u == i) ? j : (u == j) ? i : u, pv = (v == i) ? j : (v == j) ? i : v;
      perm[VID[u][v]] = VID[pu][pv];
    }
  int last = 0;
  for (int p = 1; p <= E; p++) if (perm[p] != p) last = p;
  for (int p = 1; p <= E; p++) {
    if (perm[p] == p) continue;
    int q = perm[p];
    if (y) put3(-y, -p, q); else put2(-p, q);
    if (p == last) break;
    int yn = ++TOP;
    if (y) { int l1[4] = {-y, -p, -q, yn}, l2[4] = {-y, p, q, yn}; put(l1, 4); put(l2, 4); }
    else { put3(-p, -q, yn); put3(p, q, yn); }
    y = yn;
    moved++;
  }
  free(perm);
}

static void colour_part(int c, int a, int b) {
  int K = b - 1, S[8], X[64], lits[16];
  for (int t = 0; t < a; t++) S[t] = t;
  for (;;) {
    int m = 0;
    for (int x = 0; x < N; x++) { int in = 0; for (int t = 0; t < a; t++) in |= (S[t] == x); if (!in) X[m++] = x; }
    int y0 = TOP + 1; TOP += m;
    for (int t = 0; t < m; t++) {
      int L = 0; lits[L++] = y0 + t;
      for (int s = 0; s < a; s++) { int e = VID[X[t]][S[s]]; lits[L++] = (c == 0) ? -e : e; }  /* NOT colour c */
      put(lits, L);
    }
    /* book: the counter's overflow clauses also carry NOT[edge S0 S1 has colour c] */
    int act = BOOK[c] ? ((c == 0) ? -VID[S[0]][S[1]] : VID[S[0]][S[1]]) : 0;
    if (K == 0) { for (int t = 0; t < m; t++) { if (act) put2(-(y0 + t), act); else { int l = -(y0 + t); put(&l, 1); } } }
    else {
      int r0 = TOP + 1; TOP += (m - 1) * K;
#define R(i, j) (r0 + (i) * K + (j))
#define Y(t) (y0 + (t))
      put2(-Y(0), R(0, 0));
      for (int j = 1; j < K; j++) { int l = -R(0, j); put(&l, 1); }
      for (int i = 1; i <= m - 2; i++) {
        put2(-Y(i), R(i, 0));
        put2(-R(i - 1, 0), R(i, 0));
        for (int j = 1; j < K; j++) { put3(-Y(i), -R(i - 1, j - 1), R(i, j)); put2(-R(i - 1, j), R(i, j)); }
        if (act) put3(-Y(i), -R(i - 1, K - 1), act); else put2(-Y(i), -R(i - 1, K - 1));
      }
      if (act) put3(-Y(m - 1), -R(m - 2, K - 1), act); else put2(-Y(m - 1), -R(m - 2, K - 1));
#undef R
#undef Y
    }
    /* next a-subset in lexicographic order */
    int t = a - 1;
    while (t >= 0 && S[t] == N - a + t) t--;
    if (t < 0) break;
    S[t]++;
    for (int u = t + 1; u < a; u++) S[u] = S[u - 1] + 1;
  }
}

static int NOSB = 0;
static void build(int a0, int b0, int a1, int b1) {
  TOP = E; NCL = 0;
  if (!NOSB) for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) lexleader_transposition(i, j);
  int nbase = (int)NCL;
  colour_part(0, a0, b0);
  colour_part(1, a1, b1);
  (void)nbase;
}

int main(int argc, char **argv) {
  if (argc != 4 && !(argc == 5 && !strcmp(argv[4], "nosb"))) { fprintf(stderr, "usage: kabcard N P0/P1 OUT.cnf [nosb]\n"); return 2; }
  NOSB = (argc == 5);
  N = atoi(argv[1]);
  char p0[32], p1[32]; const char *sl = strchr(argv[2], '/');
  if (!sl || N < 4 || N > 64) { fprintf(stderr, "bad args\n"); return 2; }
  snprintf(p0, sizeof p0, "%.*s", (int)(sl - argv[2]), argv[2]); snprintf(p1, sizeof p1, "%s", sl + 1);
  int a0, b0, a1, b1; ab(p0, &a0, &b0, &BOOK[0]); ab(p1, &a1, &b1, &BOOK[1]);
  E = 0;
  for (int u = 0; u < N; u++) for (int v = u + 1; v < N; v++) { VID[u][v] = VID[v][u] = ++E; }
  PASS = 0; build(a0, b0, a1, b1);                       /* count base clauses, total clauses and variables */
  long total = NCL; int top = TOP;
  PASS = 0; TOP = E; NCL = 0;
  if (!NOSB) for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) lexleader_transposition(i, j);
  long nbase = NCL;
  OUT = fopen(argv[3], "w"); if (!OUT) { perror(argv[3]); return 2; }
  fprintf(OUT, "c ramsey-exact kab_card n=%d pats=%s base=%ld E=%d\n", N, argv[2], nbase, E);
  fprintf(OUT, "p cnf %d %ld\n", top, total);
  PASS = 1; build(a0, b0, a1, b1);
  fclose(OUT);
  printf("n=%d pats=%s vars=%d clauses=%ld base=%ld\n", N, argv[2], top, total, nbase);
  return 0;
}
