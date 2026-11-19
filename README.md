# The row z(8,n;4,4), twenty further Zarankiewicz numbers, and seven small Ramsey numbers

**Status: verified by two independent programs and an internal referee; not yet peer reviewed.**

Author: Arhan Canli (Quantavane, arhan@quantavane.com). On the use of AI, see
[Authorship and the role of AI](#authorship-and-the-role-of-ai).

## The results

z(m,n;s,t) is the largest number of ones in an m × n (0,1)-matrix with no all-ones submatrix formed by s rows and t
columns (s refers to rows, t to columns; every cell here has s = t, so z(m,n;s,s) = z(n,m;s,s)). Guy and the OEIS
record k = z + 1.

**(A) The whole row z(8,n;4,4).** For n ≤ 18 the values are known: 8n for n ≤ 3; 27, 33, 39, 45 for n = 4..7; and
51, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99 for n = 8..18 (Tan 2022, Table 4; Collins et al. 2016, Table 5). Further:

| n | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| z(8,n;4,4) | 104 | 109 | 114 | 118 | 123 | 127 | 132 | 136 | 141 | 145 | 150 | 154 | 159 | 163 | 168 |

and

- z(8,n;4,4) = 4n + 36 for 33 ≤ n ≤ 66;
- z(8,n;4,4) = ⌊(210 + 15n)/4⌋ for 66 ≤ n ≤ 210;
- z(8,n;4,4) = 3n + 210 for n ≥ 210.

The values for 19 ≤ n ≤ 62 are new. For n = 19, 20, 21, Tan's table prints these cells as open (Roman's bounds 106,
111, 115), but their upper bounds follow from Tan's exact z(8,18;4,4) = 99 by the deletion bound, so what is new there
is the constructions. For n ≥ 66 the value is Roman's theorem as stated by Tan (Theorem 2.2, with T₄,₄(8) = 36 from his
Table 1), and for n ≥ 210 it is Čulík's theorem. Tan's statement also lowers Roman's threshold by 3 when the packing
is not perfect, as it is here (36 < 42), which covers n = 63, 64, 65 as well. The new ingredient for 33 ≤ n ≤ 66 is the bound z(8,n;4,4) ≤ 4n + 36 for every n (Lemma 3.3 of the paper,
below).

**(B) Twenty table cells.** "Earlier" is the best published upper bound: R = Roman's bound (as printed by Tan, or
computed from Roman's theorem), C = Collins et al. 2016 (italic = computed bound; plain = bound from their lemmas),
DGH = Davies, Gill and Horsley 2026. Upper-bound routes: D = deletion bound from the neighbouring cell; S = SAT case
split with LRAT proofs checked by cake_lpr; cnt = counting bound. "New": L = the construction, and so the exact value;
U = the upper bound.

| cell | earlier | value | upper bound | new |
|---|---|---|---|---|
| z(8,19;4,4) | 106 R | 104 | D from Tan's z(8,18;4,4) = 99 | L |
| z(8,20;4,4) | 111 R | 109 | D from 104 | L |
| z(8,21;4,4) | 115 R | 114 | D from 109 | L |
| z(9,18;4,4) | 113 R; *109* C | 109 | Collins et al.'s computed bound (credited); S confirms | L |
| z(9,19;4,4) | 118 R | 114 | S | L, U |
| z(9,20;4,4) | 123 R | 120 | D from 114 | L, U |
| z(9,21;4,4) | 129 R | 126 | D from 120 | L, U |
| z(10,19;4,4) | 131 R; 130 DGH | 126 | D from Collins et al.'s exact z(10,18;4,4) = 120; also D (rows) from z(9,19) = 114 | L |
| z(9,18;5,5) | 128 C | 128 | Collins et al.'s bound (credited); S, independent of their values, confirms | L |
| z(9,19;5,5) | 135 DGH | 134 | S | L, U |
| z(9,20;5,5) | 141 DGH | 140 | S | L, U |
| z(9,21;5,5) | 147 DGH | 146 | S | L, U |
| z(9,22;5,5) | 153 DGH | 152 | D from 146 | L, U |
| z(9,23;5,5) | 159 DGH | 158 | D from 152 | L, U |
| z(8,18;5,5) | 115 C, R | 115 | cnt | L |
| z(8,19;5,5) | 121 R | 120 | S | L, U |
| z(8,20;5,5) | 126 R | 126 | cnt | L |
| z(8,21;5,5) | 132 R | 132 | cnt | L |
| z(8,22;5,5) | 138 R | 137 | S | L, U |
| z(8,23;5,5) | 143 R | 143 | cnt | L |

**(C) Seven Ramsey numbers.** R(G₁, …, G_k) is the least N such that every colouring of the edges of K_N with colours
1..k has a copy of G_i in colour i for some i (Radziszowski, DS1). K_{a,b} is the complete bipartite graph, C₄ = K_{2,2}
and K_{1,t} the star with t leaves.

| value | before | lower bound | upper bound |
|---|---|---|---|
| R(K_{2,12}, K_{2,3}) = 23 | 23–24 (ramsey-cells) | our colouring of K₂₂ (and theirs) | K₂₃: SAT, LRAT checked by cake_lpr (new) |
| R(K_{2,13}, K_{2,3}) = 25 | 25–26 (ramsey-cells) | our colouring of K₂₄ (and theirs) | K₂₅: SAT (new) |
| R(K_{2,14}, K_{2,3}) = 26 | 26–27 (ramsey-cells) | our colouring of K₂₅ (and theirs) | K₂₆: SAT (new) |
| R(K_{2,12}, K_{2,4}) = 27 | 26–27 (ramsey-cells) | our colouring of K₂₆ (new) | K₂₇: SAT (confirms ramsey-cells) |
| R(C₄, K_{3,11}) = 22 | 22–24 (DS1) | R(C₄, K_{3,10}) = 22 (Lortz); our colouring of K₂₁ | K₂₂: SAT (new) |
| R(C₄, C₄, K_{1,13}) = 23 | 22–24 | our colouring of K₂₂ (new) | counting with ex(23, C₄) = 56 |
| R(C₄, C₄, K_{1,14}) = 24 | 22–25 | our colouring of K₂₃ (new) | counting with ex(24, C₄) = 59 |

For the star values, the earlier lower bound 22 is R(C₄, C₄, K_{1,12}) = 22 with monotonicity, and the earlier upper
bounds are the general bound n + 3 + ⌈√(4n+5)⌉ of Zhang, Chen and Cheng. In a good colouring of K_N the two C₄ classes have at most ex(N, C₄) edges each and the star
class has maximum degree at most t − 1, so 2·56 + ⌊23·12/2⌋ = 250 < 253 = C(23,2) and 2·59 + ⌊24·13/2⌋ = 274 < 276 =
C(24,2). The second inequality has no slack: it needs ex(24, C₄) ≤ 59 exactly.

## Caveat for the twelve (5,5) cells

L.-X. Wang and X. Zhang, *Bipartite Turán problem on complete bipartite graphs*, Acta Math. Appl. Sinica (Engl. Ser.)
42 (2026) 1280–1290 (doi:10.1007/s10255-026-0114-1), give closed formulas for z(m,n;s,t) under conditions on the
parameters. We have not read the paper itself. As a search summary states its conditions, one of them (m ≤ s + t − 1)
would include every (5,5) cell above, but the formula given in that summary exceeds the counting bound in these cells
(for example 121 at z(8,18;5,5), whose counting bound is 115), so the summary cannot be the complete statement. Until
the exact statement has been read, whether any of the twelve (5,5) values is already covered by that paper is open.
Their correctness does not depend on it.

## The earlier work this builds on

- K. Zarankiewicz (1951) posed the problem; P. Kővári, V. T. Sós and P. Turán (1954) and I. Reiman (1958) gave general
  bounds; K. Čulík (1956) the exact value for large n; S. Roman (1975) a general upper bound with conditions for
  equality; R. K. Guy (1967, 1969) the first tables (k = z + 1); T. Héger (2013) found an error in them.
- A. F. Collins, A. W. N. Riasanovsky, J. C. Wallace and S. P. Radziszowski, *Zarankiewicz numbers and bipartite
  Ramsey numbers*, J. Algorithms Comput. 47 (2016) 63–78, arXiv:1604.01257: Tables 4–7 for z(m,n;s,s), 3 ≤ s ≤ 6,
  m, n ≤ 18. We credit their bounds z(9,18;4,4) ≤ 109, z(9,18;5,5) ≤ 128 and z(8,18;5,5) ≤ 115, and use their exact
  z(10,18;4,4) = 120, z(9,17;4,4) = 104 and z(9,17;5,5) = 121.
- J. Tan, *An attack on Zarankiewicz's problem through SAT solving*, arXiv:2203.02283 (2022), and his repository
  github.com/Parcly-Taxel/Kyoto: Table 4 (z(m,n;4,4)), Theorem 2.2 (Roman's bound and its equality case), Corollary
  2.1 (Čulík) and Table 1 (T₄,₄(8) = 36, the packing used in the constructions).
- S. Davies, P. Gill and D. Horsley, *Improved upper bounds on Zarankiewicz numbers*, Discrete Math. 349 (2026)
  114924, arXiv:2411.18842: Tables 5 and 7.
- C. Balbuena, P. García-Vázquez, X. Marcote and J. C. Valenzuela, *Extremal K_(s,t)-free bipartite graphs*, DMTCS
  10(3) (2008) 35–48: exact values in a dense regime; none of the cells here satisfies its conditions.
- S. P. Radziszowski, *Small Ramsey numbers*, Electron. J. Combin. Dynamic Survey DS1, revision 18 (24 April 2026):
  Table IVc (R(K_{2,n}, K_{2,m}) for n ≤ 11), Section 3.3(g) (R(C₄, K_{3,n}) for n = 6..10 by Lortz and n = 12 by
  Shao), Section 6.3.3(b,c) (R(C₄, C₄, K_{1,n})).
- Lortz and I. Mengersen, *Off-diagonal and asymptotic results on the Ramsey number r(K_{2,m}, K_{2,n})*, J. Graph
  Theory 43 (2003) 252–268; Lortz, *A note on the Ramsey number of K_{2,2} versus K_{3,n}*, Discrete Math. 306 (2006)
  2976–2982; S. Van Overberghe's construction files, github.com/Steven-VO/circulant-Ramsey.
- The repository github.com/alejandrozarco/ramsey-cells (2026; produced with AI tools and not peer reviewed; Zenodo
  doi:10.5281/zenodo.23196590): the windows 23–24, 25–26, 26–27, 26–27 for the four K_{2,n} cells, their colourings for
  the lower ends, and evaluations of Lemmas 2.2/2.3 of Lortz and Mengersen for the upper ends.
- R(C₄, C₄, K_{1,n}): J. Arste, K. Klamroth and I. Mengersen (n ≤ 3); Zhang, Chen and Cheng, Discrete Math. (2019),
  doi:10.1016/j.disc.2018.09.030 (n = 4, 5, 6, the general bound n + 3 + ⌈√(4n+5)⌉, and R(C₄, C₄, K_{1,12}) = 22);
  Liu Min and Zhang Xuemei, Advances in Applied Mathematics (Hans) 8(11) (2019) 1870–1879 (n = 7..10).
- ex(N, C₄): C. R. J. Clapham, A. Flockhart and J. Sheehan, J. Graph Theory 13 (1989) 29–47 (N ≤ 21); Yuansheng
  and P. Rowlinson, Utilitas Math. (1992) (up to N = 31); N. Afzaly and B. D. McKay's exhaustive computation, listed on
  McKay's page *Extremal graphs and Turán numbers* (N ≤ 40).
- CaDiCaL (A. Biere and others) and cake_lpr (Y. K. Tan, M. J. H. Heule, M. O. Myreen) for the proofs.

## How the upper bounds are proved

- **Deletion bound.** A matrix with N ones has a column with at most N/n ones, so
  z(m,n) ≤ ⌊n·z(m,n−1)/(n−1)⌋ (and the same for rows).
- **Counting bound** (Guy's argument A): every s-set of rows lies in at most t − 1 columns, so
  Σⱼ C(cⱼ, s) ≤ (t − 1)·C(m, s).
- **SAT case split.** A matrix is the multiset of its column supports. If z(m,n;s,t) ≥ K, deleting ones gives an
  admissible matrix with exactly K ones; its size profile (b_s, …, b_m) satisfies three counting conditions; and
  with U ≥ z(m,n−1;s,t), every column has at least K − U ones. Each allowed profile becomes one formula (column types
  in unary, Sinz counters, lex-leader constraints for the transpositions of the rows; soundness in the header of
  `zarankiewicz/tools/ztype.py`). Each formula was refuted by CaDiCaL 3.0.1 with a binary LRAT proof, and each proof
  was checked by cake_lpr.
- **Ramsey formulas.** A graph contains K_{a,b} (a ≤ b) exactly when some a-set of vertices has b common
  neighbours. The formula uses one variable per edge, an "AND" variable per (a-set, outside vertex), a Sinz counter
  "at most b − 1", and lex-leader constraints for the vertex transpositions (soundness in the header of
  `ramsey/encoders/kab_card.py`).
- **Row theorem** (paper, Lemmas 3.1 and 3.3). Roman's bounds with p = 3, 4, 5 give z(8,n;4,4) ≤ 3n + 210,
  ⌊(210 + 15n)/4⌋ and ⌊(210 + 45n)/10⌋. If an admissible 8 × n matrix had more than 4n + 36 ones, its columns of
  size ≥ 5 would form an 8 × B matrix with at least 4B + 37 ones and B ≤ 42; that contradicts z(8,B;4,4) ≤ 4B + 36
  for B ≤ 42 (Roman with p = 5 for B ≤ 31, the certified values for 32 ≤ B ≤ 42). Tan's 36 five-sets plus four-set
  columns attain the bounds.

The SAT proofs are not in this repository (the largest is 1.12 GB uncompressed). Their SHA-256
hashes and sizes, and those of every formula, are recorded in `zarankiewicz/records/proofs.tsv` and
`ramsey/records/proofs.tsv`. CaDiCaL 3.0.1 is deterministic, so with the same version and options each proof can be regenerated from its formula.

## Checking it: one command

    sh check.sh        # a few minutes on one core; needs cc and python3 (standard library only)

`check.sh` checks the file hashes; runs both Zarankiewicz checkers on all 61 matrices (the 20 cells and the row
n = 19..62) with the exact number of ones, and three planted blocks per matrix, each refused by both; recomputes every
deletion and counting step and the finite facts of the row theorem (`zarankiewicz/tools/bounds.py`); builds the
constructions of the row theorem for n = 36..67, 80, 100, 150, 209, 210, 211, 250 and checks them; regenerates every
recorded case list with two enumerators and every recorded case formula with two encoders, and compares them with the
recorded hashes; runs three checkers on the seven Ramsey colourings, with one planted copy per colour refused by all
three; and regenerates the five Ramsey formulas and compares their hashes. With `cadical` and `cake_lpr` on PATH it
also re-solves two small cases and checks their proofs. It ends with `ALL CHECKS PASSED` or stops at the first
failure.

- **Zarankiewicz checkers** (written apart from the encoders and from each other): `zarankiewicz/checks/zcheck.c`
  (every s-set of rows, AND of 64-bit column masks, popcount) and `zarankiewicz/checks/zcheck2.py` (every t-set of
  columns inside each row's support, counted over rows); red controls by `zarankiewicz/checks/plant.py`.
- **Ramsey checkers**: `ramsey/checks/qvr.c` (search for an embedded copy), `ramsey/checks/check_char.py`
  (characterisations, e.g. an a-set with b common neighbours) and `ramsey/checks/kabcount.c` (bitset common-neighbour
  counts); red controls by `ramsey/checks/plant.py`.
- **Encoders and enumerators** (two separately written programs each, which produce byte-identical files):
  `zarankiewicz/tools/ztype.py` and `zarankiewicz/checks/ztype.c`; `zarankiewicz/tools/zsizes.py` and
  `zarankiewicz/checks/zsizes2.c`; `ramsey/encoders/kab_card.py` (needs python-sat and `sgfind.c` compiled as
  `sgfind.so`) and `ramsey/encoders/kabcard.c`.
- **Internal referee.** A separately run agent that had not seen our notes wrote its own checkers, profile enumerator
  and encoders (totalizer counters, a different variable order and a different symmetry-breaking order), re-ran
  cake_lpr on our stored proofs, and re-proved the SAT and deletion upper bounds of (B) and of the row for
  19 ≤ n ≤ 42 without using any neighbouring value (for z(10,19;4,4) it checked both deletion routes); for n ≥ 43 the
  row's upper bound is Lemma 3.3, which it checked line by line, as it did the constructions. For the Ramsey
  values it also checked every colouring with two programs of its own and re-solved every SAT instance with its own
  encoding. Its programs are not in this repository.

## Not yet done

- Outside review: none yet.
- Lean 4: not yet; a kernel-checked version is planned and its status will be added here.
- Paper: a paper is in preparation.
- The exact statement of Wang and Zhang 2026 (see the caveat above) has not been read.
- Every SAT upper bound for the Ramsey values uses lex-leader symmetry breaking. A run without it, for
  R(K_{2,13}, K_{2,3}) at K₂₅, did not finish in 7,201 s. For the Zarankiewicz cells, proofs without symmetry
  breaking exist for 8 × 19, 8 × 20 and 8 × 21 only.

## Layout

| path | contents |
| --- | --- |
| `zarankiewicz/cells.tsv` | every value with its upper-bound route, witness and record (plus the four published values used as inputs) |
| `zarankiewicz/witnesses/` | the 61 matrices (rows of 0/1) and the packing `pack5_8_36.txt` |
| `zarankiewicz/certs/` | the per-cell records (checker outputs, case lists, formula and proof hashes) |
| `zarankiewicz/records/` | `proofs.tsv` (41 case formulas and their proofs, as recorded) and `caselists.tsv` |
| `zarankiewicz/checks/` | `zcheck.c`, `zcheck2.py`, `plant.py`, `ztype.c` (encoder B), `zsizes2.c` (enumerator B) |
| `zarankiewicz/tools/` | `ztype.py` (encoder A), `zsizes.py` (enumerator A), `ubound.py` (counting bound), `bounds.py`, `row8_construct.py` |
| `ramsey/witnesses/` | the seven colourings (`.col`: first line `n k`, then the colour matrix) with their recorded check outputs |
| `ramsey/witnesses.tsv` | claims, graphs and edge counts per colour |
| `ramsey/records/proofs.tsv` | the five unsatisfiable formulas and their LRAT proofs, as recorded |
| `ramsey/checks/` | `qvr.c`, `check_char.py`, `kabcount.c`, `plant.py` |
| `ramsey/encoders/` | `kab_card.py` with `cegar.py`, `pat.py`, `sgfind.c` (encoder A) and `kabcard.c` (encoder B) |
| `tools/sha256check.py` | hash check (standard library) |

In the records, `<archive>/` and `runs/` refer to the archive where the proofs and run logs are kept; they are not
part of this repository. The records in `zarankiewicz/certs/` are the per-cell records of our runs, with internal
process notes removed; every hash and checker output in them is as recorded.

## Authorship and the role of AI

Author and maintainer: Arhan Canli (Quantavane, https://quantavane.com), who takes responsibility for the results.

The searches, the constructions, the checkers and this text were written and carried out by AI agents (Claude, by
Anthropic) working for Quantavane under Arhan Canli's direction. Programs described as written separately share no
code but were written with the same AI system. No mathematician outside Quantavane has reviewed this repository; the
witnesses can be checked by anyone with the programs here or with their own.

## Licence and citation

The matrices, colourings, records and text are under CC BY 4.0 (`LICENSE`); the code is under the MIT licence
(`LICENSE-CODE`). Please cite as: Arhan Canli, *The row z(8,n;4,4), twenty further Zarankiewicz numbers, and seven
small Ramsey numbers*, https://github.com/arhancanli/quantavane-zarankiewicz-ramsey-cells (2026), together with the
tables these values complete (Tan 2022; Collins, Riasanovsky, Wallace and Radziszowski 2016; Davies, Gill and Horsley
2026; Radziszowski's DS1).
