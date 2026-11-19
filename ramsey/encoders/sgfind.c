/* sgfind.c: monochromatic copies of a small pattern H in a graph G on n <= 64 vertices (search side only).
   Build: cc -O3 -shared -fPIC -o sgfind.so sgfind.c
   find_copies(n, adj, h, pre, maxout, percap, start, out): G given by adjacency bitsets adj[0..n-1];
   H given in a vertex order 0..h-1 where pre[i] is the bitmask of earlier positions adjacent to position i.
   Writes up to maxout monomorphisms (images of positions 0..h-1) into out, at most percap per root vertex,
   roots tried from 'start' cyclically. Returns the number written. */
#include <stdint.h>

static int N, H, MAXOUT, PERCAP, cnt, rootcnt;
static const uint64_t *ADJ;
static const uint32_t *PRE;
static int *OUT;
static int img[64];

static int rec(int i, uint64_t used) {
  if (i == H) {
    for (int k = 0; k < H; k++) OUT[cnt * H + k] = img[k];
    cnt++; rootcnt++;
    return (cnt >= MAXOUT || rootcnt >= PERCAP);
  }
  uint64_t cand = (N == 64 ? ~0ULL : ((1ULL << N) - 1)) & ~used;
  uint32_t p = PRE[i];
  for (int j = 0; j < i; j++) if (p >> j & 1) cand &= ADJ[img[j]];
  while (cand) {
    int v = __builtin_ctzll(cand);
    cand &= cand - 1;
    img[i] = v;
    if (rec(i + 1, used | (1ULL << v))) return 1;
  }
  return 0;
}

int find_copies(int n, const uint64_t *adj, int h, const uint32_t *pre, int maxout, int percap, int start, int *out) {
  /* start < 0: only root -start-1 */
  N = n; H = h; ADJ = adj; PRE = pre; MAXOUT = maxout; PERCAP = percap; OUT = out; cnt = 0;
  int nroots = n;
  if (start < 0) { start = -start - 1; nroots = 1; }
  for (int t = 0; t < nroots && cnt < maxout; t++) {
    int r = (start + t) % n;
    rootcnt = 0;
    img[0] = r;
    rec(1, 1ULL << r);
  }
  return cnt;
}
