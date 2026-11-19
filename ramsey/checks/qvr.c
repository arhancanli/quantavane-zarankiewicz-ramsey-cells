/* qvr.c: checks for the Ramsey computations, written apart from the search code (tools/cegar.py, tools/sgfind.c).
   Build: cc -O2 -o qvr qvr.c
   Modes:
     qvr check COLFILE P0,P1[,P2...]
        COLFILE: first line "n k", then n rows of n characters ('0'..'9' = colour of the edge, '-' on the diagonal).
        Prints PASS when no colour c contains a copy (not necessarily induced) of pattern P_c; otherwise FAIL with
        a copy. Also checks the matrix is symmetric and every off-diagonal entry is a colour < k.
     qvr validate CNF n P0,P1[,..] SBMODE COLSWAP NBASE
        Second encoder for the CEGAR CNFs: regenerates (own code) the one-hot and lex-leader clauses from the
        written scheme and requires them to equal the first NBASE clauses of CNF, in order; then requires every
        later clause to be a blocking clause "not all of these edges have colour c" whose edge set contains a copy
        of P_c. Prints VALID or the first bad clause.
   Pattern names: Kk, Kk-e, Ck, Pk, Wn (n vertices), Bn (K2 + nK1), Fn (K1 + nK2), Ka,b. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 64
#define MAXH 32

typedef struct { int h; int adj[MAXH][MAXH]; int deg[MAXH]; char name[32]; } Pat;

static void addE(Pat *p, int a, int b) { p->adj[a][b] = p->adj[b][a] = 1; }

static int parse_pat(const char *s, Pat *p) {
  memset(p, 0, sizeof *p);
  strncpy(p->name, s, 31);
  int a, b; char tail[8] = {0};
  if (sscanf(s, "K%d,%d", &a, &b) == 2) {
    p->h = a + b;
    for (int i = 0; i < a; i++) for (int j = 0; j < b; j++) addE(p, i, a + j);
  } else if (s[0] == 'K' && strstr(s, "-e")) {
    sscanf(s, "K%d", &a); p->h = a;
    for (int i = 0; i < a; i++) for (int j = i + 1; j < a; j++) if (!(i == 0 && j == 1)) addE(p, i, j);
  } else if (sscanf(s, "K%d%7s", &a, tail) >= 1 && s[0] == 'K' && tail[0] == 0) {
    p->h = a;
    for (int i = 0; i < a; i++) for (int j = i + 1; j < a; j++) addE(p, i, j);
  } else if (s[0] == 'C') {
    a = atoi(s + 1); p->h = a;
    for (int i = 0; i < a; i++) addE(p, i, (i + 1) % a);
  } else if (s[0] == 'P') {
    a = atoi(s + 1); p->h = a;
    for (int i = 0; i + 1 < a; i++) addE(p, i, i + 1);
  } else if (s[0] == 'W') {
    a = atoi(s + 1); p->h = a;                       /* hub a-1, rim 0..a-2 */
    for (int i = 0; i < a - 1; i++) { addE(p, a - 1, i); addE(p, i, (i + 1) % (a - 1)); }
  } else if (s[0] == 'B') {
    a = atoi(s + 1); p->h = a + 2;                   /* spine 0,1 */
    addE(p, 0, 1);
    for (int i = 2; i < a + 2; i++) { addE(p, 0, i); addE(p, 1, i); }
  } else if (s[0] == 'F') {
    a = atoi(s + 1); p->h = 2 * a + 1;               /* hub 2a */
    for (int i = 0; i < a; i++) { addE(p, 2 * a, 2 * i); addE(p, 2 * a, 2 * i + 1); addE(p, 2 * i, 2 * i + 1); }
  } else return 0;
  if (p->h > MAXH || p->h < 2) return 0;
  for (int i = 0; i < p->h; i++) for (int j = 0; j < p->h; j++) p->deg[i] += p->adj[i][j];
  return 1;
}

/* containment: does graph g (n vertices, matrix) contain pattern p? order H vertices by degree (desc). */
static int G[MAXN][MAXN], GN;
static int ord[MAXH], mapv[MAXH], usedv[MAXN];
static const Pat *PP;

/* twins (19 Nov): pattern vertices x, y with the same neighbours apart from each other; swapping them is an
   automorphism of the pattern, so if a copy exists, one exists with images increasing in index order inside each twin
   class. The search keeps only those (still an embedding search; for K2,12 it removes the 12! leaf orders). */
static int TW[MAXH][MAXH];
static void twins(const Pat *p) {
  for (int x = 0; x < p->h; x++) for (int y = 0; y < p->h; y++) {
    int t = (x != y);
    for (int z = 0; z < p->h && t; z++) if (z != x && z != y && p->adj[x][z] != p->adj[y][z]) t = 0;
    TW[x][y] = t;
  }
}

static int bt(int t) {
  if (t == PP->h) return 1;
  int x = ord[t];
  for (int v = 0; v < GN; v++) {
    if (usedv[v]) continue;
    int ok = 1;
    for (int s = 0; s < t && ok; s++) if (PP->adj[x][ord[s]] && !G[v][mapv[ord[s]]]) ok = 0;
    for (int s = 0; s < t && ok; s++) {
      int y = ord[s];
      if (TW[x][y] && ((y < x && mapv[y] > v) || (y > x && mapv[y] < v))) ok = 0;
    }
    if (!ok) continue;
    usedv[v] = 1; mapv[x] = v;
    if (bt(t + 1)) return 1;
    usedv[v] = 0;
  }
  return 0;
}

static int contains(const Pat *p) {
  PP = p; twins(p);
  for (int i = 0; i < p->h; i++) ord[i] = i;
  for (int i = 0; i < p->h; i++) for (int j = i + 1; j < p->h; j++)
    if (p->deg[ord[j]] > p->deg[ord[i]]) { int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
  memset(usedv, 0, sizeof usedv);
  return bt(0);
}

static int split_pats(char *arg, Pat *pats) {
  /* patterns separated by '/' (needed for Ka,b); a list without '/' is split on ',' */
  int k = 0; const char *sep = strchr(arg, '/') ? "/" : ",";
  for (char *tok = strtok(arg, sep); tok; tok = strtok(NULL, sep)) {
    if (!parse_pat(tok, &pats[k])) { fprintf(stderr, "bad pattern %s\n", tok); exit(2); }
    k++;
  }
  return k;
}

static int do_check(const char *file, char *patarg) {
  Pat pats[10]; int k = split_pats(patarg, pats);
  FILE *f = fopen(file, "r"); if (!f) { perror(file); return 2; }
  int n, kk; if (fscanf(f, "%d %d", &n, &kk) != 2 || n > MAXN) { printf("FAIL header\n"); return 1; }
  if (kk != k) { printf("FAIL colours %d vs %d patterns\n", kk, k); return 1; }
  static char row[MAXN + 8]; static int M[MAXN][MAXN];
  for (int i = 0; i < n; i++) {
    if (fscanf(f, "%70s", row) != 1 || (int)strlen(row) != n) { printf("FAIL row %d\n", i); return 1; }
    for (int j = 0; j < n; j++) {
      if (i == j) { if (row[j] != '-') { printf("FAIL diagonal %d\n", i); return 1; } M[i][j] = -1; continue; }
      int c = row[j] - '0'; if (c < 0 || c >= k) { printf("FAIL entry %d %d\n", i, j); return 1; }
      M[i][j] = c;
    }
  }
  fclose(f);
  for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) if (M[i][j] != M[j][i]) { printf("FAIL asym %d %d\n", i, j); return 1; }
  GN = n;
  int bad = 0;
  for (int c = 0; c < k; c++) {
    int ecount = 0;
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { G[i][j] = (i != j && M[i][j] == c); ecount += G[i][j]; }
    if (contains(&pats[c])) {
      printf("FAIL colour %d contains %s:", c, pats[c].name);
      for (int t = 0; t < pats[c].h; t++) printf(" %d", mapv[t]);
      printf("\n"); bad = 1;
    } else printf("colour %d (%d edges): no %s\n", c, ecount / 2, pats[c].name);
  }
  printf(bad ? "FAIL\n" : "PASS n=%d\n", n);
  return bad;
}

/* ---- validate ---- */
static int n_, k_, E_, V_, top_;
static int eidx[MAXN][MAXN], eu[MAXN * MAXN], ev[MAXN * MAXN];
static int vnum(int u, int v, int c) { int e = eidx[u][v]; return k_ == 2 ? e + 1 : e * k_ + c + 1; }

typedef struct { int *l; int len; } Cl;
static Cl *gen; static int ngen, capgen;
static void emit(int *l, int len) {
  if (ngen == capgen) { capgen = capgen ? 2 * capgen : 1024; gen = realloc(gen, capgen * sizeof(Cl)); }
  gen[ngen].l = malloc(len * sizeof(int)); memcpy(gen[ngen].l, l, len * sizeof(int)); gen[ngen].len = len; ngen++;
}

static void lexleader(int *s) {
  int *pos = malloc((V_ + 1) * sizeof(int)), np = 0;
  for (int p = 1; p <= V_; p++) if (s[p] != p) pos[np++] = p;
  int y = 0;
  for (int t = 0; t < np; t++) {
    int a = pos[t], b = s[a], buf[5], L = 0;
    if (y) buf[L++] = -y;
    buf[L] = -a; buf[L + 1] = b; emit(buf, L + 2);
    if (t == np - 1) break;
    int yn = ++top_;
    buf[L] = -a; buf[L + 1] = -b; buf[L + 2] = yn; emit(buf, L + 3);
    buf[L] = a; buf[L + 1] = b; buf[L + 2] = yn; emit(buf, L + 3);
    y = yn;
  }
  free(pos);
}

static int do_validate(const char *cnf, int n, char *patarg, const char *sbmode, int colswap, int nbase) {
  Pat pats[10]; k_ = split_pats(patarg, pats); n_ = n;
  E_ = 0;
  for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) { eidx[u][v] = eidx[v][u] = E_; eu[E_] = u; ev[E_] = v; E_++; }
  V_ = (k_ == 2) ? E_ : E_ * k_; top_ = V_;
  /* one-hot */
  if (k_ >= 3) for (int e = 0; e < E_; e++) {
    int buf[16]; for (int c = 0; c < k_; c++) buf[c] = e * k_ + c + 1; emit(buf, k_);
    for (int a = 0; a < k_; a++) for (int b = a + 1; b < k_; b++) { int t[2] = {-(e * k_ + a + 1), -(e * k_ + b + 1)}; emit(t, 2); }
  }
  int *s = malloc((V_ + 1) * sizeof(int));
  if (strcmp(sbmode, "none")) {
    for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) {
      if (!strcmp(sbmode, "adj") && j != i + 1) continue;
      for (int u = 0; u < n; u++) for (int v = u + 1; v < n; v++) {
        int a = u == i ? j : (u == j ? i : u), b = v == i ? j : (v == j ? i : v);
        for (int c = 0; c < (k_ == 2 ? 1 : k_); c++) s[vnum(u, v, c)] = vnum(a, b, c);
      }
      lexleader(s);
    }
  }
  if (colswap && k_ >= 3) for (int c1 = 0; c1 < k_; c1++) for (int c2 = c1 + 1; c2 < k_; c2++) {
    if (strcmp(pats[c1].name, pats[c2].name)) continue;
    for (int e = 0; e < E_; e++) for (int c = 0; c < k_; c++) {
      int cc = c == c1 ? c2 : (c == c2 ? c1 : c); s[e * k_ + c + 1] = e * k_ + cc + 1;
    }
    lexleader(s);
  }
  if (ngen != nbase) { printf("INVALID: regenerated %d base clauses, CNF says %d\n", ngen, nbase); return 1; }
  FILE *f = fopen(cnf, "r"); if (!f) { perror(cnf); return 2; }
  char line[1 << 16]; int hv = -1, hc = -1, idx = 0, nbad = 0; long nblock = 0;
  static int lits[4096];
  while (fgets(line, sizeof line, f)) {
    if (line[0] == 'c') continue;
    if (line[0] == 'p') { sscanf(line, "p cnf %d %d", &hv, &hc); continue; }
    int L = 0; char *q = line; int x, off;
    while (sscanf(q, "%d%n", &x, &off) == 1) { q += off; if (x == 0) break; lits[L++] = x; }
    if (idx < nbase) {
      if (L != gen[idx].len || memcmp(lits, gen[idx].l, L * sizeof(int))) { printf("INVALID base clause %d differs\n", idx); return 1; }
    } else {
      /* blocking clause */
      int c = -1, ok = 1; GN = n; memset(G, 0, sizeof G);
      for (int t = 0; t < L && ok; t++) {
        int l = lits[t], v = l > 0 ? l : -l, cc, e;
        if (v < 1 || v > V_) { ok = 0; break; }
        if (k_ == 2) { e = v - 1; cc = l < 0 ? 0 : 1; }
        else { if (l > 0) { ok = 0; break; } e = (v - 1) / k_; cc = (v - 1) % k_; }
        if (c == -1) c = cc; else if (c != cc) ok = 0;
        G[eu[e]][ev[e]] = G[ev[e]][eu[e]] = 1;
      }
      if (!ok || c < 0 || !contains(&pats[c])) { printf("INVALID blocking clause %d (index %d)\n", idx - nbase, idx); nbad++; if (nbad > 5) return 1; }
      nblock++;
    }
    idx++;
  }
  fclose(f);
  if (hc != idx) { printf("INVALID header clause count %d vs %d\n", hc, idx); return 1; }
  if (hv != top_) { printf("INVALID header var count %d vs %d\n", hv, top_); return 1; }
  if (nbad) { printf("INVALID\n"); return 1; }
  printf("VALID n=%d k=%d base=%d blocking=%ld vars=%d\n", n, k_, nbase, nblock, top_);
  return 0;
}

int main(int argc, char **argv) {
  if (argc >= 4 && !strcmp(argv[1], "check")) return do_check(argv[2], argv[3]);
  if (argc >= 8 && !strcmp(argv[1], "validate"))
    return do_validate(argv[2], atoi(argv[3]), argv[4], argv[5], atoi(argv[6]), atoi(argv[7]));
  fprintf(stderr, "usage: qvr check COLFILE PATS | qvr validate CNF n PATS SBMODE COLSWAP NBASE\n");
  return 2;
}
