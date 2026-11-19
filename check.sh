#!/bin/sh
# One command:  sh check.sh     (a few minutes on one core; needs cc and python3, standard library only)
# With cadical and cake_lpr on PATH it also re-solves two small cases and checks their LRAT proofs (seconds).
# With the python-sat package it also runs the Python Ramsey encoder (encoders/kab_card.py) next to the C one.
set -eu
cd "$(dirname "$0")"
PY=${PYTHON:-python3}
export PYTHONDONTWRITEBYTECODE=1
fail() { echo "CHECK FAILED: $*"; exit 1; }
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
TAB=$(printf '\t')
sha() { "$PY" -c 'import hashlib,sys; h=hashlib.sha256(); f=open(sys.argv[1],"rb"); [h.update(c) for c in iter(lambda: f.read(1<<20), b"")]; print(h.hexdigest())' "$1"; }
sorted_sha() { LC_ALL=C sort "$1" > "$1.s"; sha "$1.s"; }

echo "1. File hashes"
"$PY" -I tools/sha256check.py SHA256SUMS || fail "file hashes"

echo "2. Build the C programs"
cc -O2 -o "$T/zcheck" zarankiewicz/checks/zcheck.c
cc -O2 -o "$T/ztype" zarankiewicz/checks/ztype.c
cc -O2 -o "$T/zsizes2" zarankiewicz/checks/zsizes2.c
cc -O2 -o "$T/qvr" ramsey/checks/qvr.c
cc -O2 -o "$T/kabcount" ramsey/checks/kabcount.c
cc -O2 -o "$T/kabcard" ramsey/encoders/kabcard.c
echo "   done"

cd zarankiewicz
grep -v '^#' cells.tsv | tail -n +2 | grep -v "${TAB}published${TAB}" > "$T/cells"

echo "3. Zarankiewicz witnesses: two checkers, exact number of ones, three red controls each"
nw=0
while IFS="$TAB" read -r m n s t v route inp w cert; do
  "$T/zcheck" "$w" "$s" "$t" "$v" | grep -q "^PASS m=$m n=$n ones=$v " || fail "zcheck on $w"
  "$PY" -I checks/zcheck2.py "$w" "$s" "$t" "$v" | grep -q "^PASS m=$m n=$n ones=$v " || fail "zcheck2 on $w"
  "$PY" -I checks/plant.py "$w" "$s" "$t" "$T/ctl" 1
  for c in "$T"/ctl.ctrl*.mat; do
    "$T/zcheck" "$c" "$s" "$t" | grep -q "^PASS" && fail "zcheck accepted a planted block ($w)"
    "$PY" -I checks/zcheck2.py "$c" "$s" "$t" | grep -q "^PASS" && fail "zcheck2 accepted a planted block ($w)"
  done
  rm -f "$T"/ctl.ctrl*.mat
  nw=$((nw + 1))
done < "$T/cells"
echo "   $nw witnesses PASS (both checkers, exact counts); $((3 * nw)) red controls refused by both"

echo "4. Deletion and counting bounds, the finite facts of the row theorem, the packings"
"$PY" -I tools/bounds.py > "$T/bounds.txt" || { cat "$T/bounds.txt"; fail "bounds"; }
tail -1 "$T/bounds.txt" | sed 's/^/   /'

echo "5. The constructions of Lemmas 3.1 and 3.3 for z(8,n;4,4) (written as n x 8 transposes)"
for n in 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65 66 67 80 100 150 209 210 211 250; do
  r=$("$PY" -I tools/row8_construct.py "$n" "$T/r.mat")
  v=$(echo "$r" | sed 's/.*formula=//')
  echo "$r" | grep -q "ones=$v formula" || fail "construction n=$n: $r"
  "$T/zcheck" "$T/r.mat" 4 4 "$v" | grep -q "^PASS m=$n n=8 ones=$v " || fail "zcheck on construction n=$n"
  "$PY" -I checks/zcheck2.py "$T/r.mat" 4 4 "$v" | grep -q "^PASS m=$n n=8 ones=$v " || fail "zcheck2 on construction n=$n"
done
echo "   n = 36..67, 80, 100, 150, 209, 210, 211, 250: the number of ones equals the formula; both checkers PASS"

echo "6. Case lists: two separately written enumerators against the recorded hashes"
grep -v '^#' records/caselists.tsv | tail -n +2 > "$T/cl"
ncl=0
while IFS="$TAB" read -r m n s t K cmin how h; do
  "$PY" -I tools/zsizes.py "$m" "$n" "$s" "$t" "$K" "$cmin" > "$T/a.txt"
  "$T/zsizes2" "$m" "$n" "$s" "$t" "$K" "$cmin" > "$T/b.txt"
  [ "$(sorted_sha "$T/a.txt")" = "$(sorted_sha "$T/b.txt")" ] || fail "the enumerators differ at z($m,$n;$s,$t) >= $K"
  if [ "$how" = sorted ]; then x=$(sorted_sha "$T/a.txt"); else x=$(sha "$T/a.txt"); fi
  [ "$x" = "$h" ] || fail "case list hash at z($m,$n;$s,$t) >= $K"
  ncl=$((ncl + 1))
done < "$T/cl"
echo "   $ncl case lists identical from both enumerators and equal to the records"

echo "7. Case formulas: two separately written encoders (Python and C) against the recorded hashes"
grep -v '^#' records/proofs.tsv | tail -n +2 > "$T/pr"
nf=0
while IFS="$TAB" read -r m n s t K cmin cs sp h l16 gb gh; do
  "$PY" -I tools/ztype.py "$m" "$n" "$s" "$t" "$K" "$T/a.cnf" pts "$sp" > /dev/null
  "$T/ztype" "$m" "$n" "$s" "$t" "$K" "$T/b.cnf" pts "$sp" > /dev/null
  ha=$(sha "$T/a.cnf"); hb=$(sha "$T/b.cnf")
  [ "$ha" = "$hb" ] || fail "the encoders differ at z($m,$n;$s,$t) >= $K profile $sp"
  case "$ha" in "$h"*) ;; *) fail "formula hash at z($m,$n;$s,$t) >= $K profile $sp";; esac
  nf=$((nf + 1))
done < "$T/pr"
rm -f "$T/a.cnf" "$T/b.cnf"
echo "   $nf case formulas identical from both encoders and equal to the recorded hashes"
cd ..

cd ramsey
echo "8. Ramsey colourings: three checkers, edge counts as recorded, one planted copy per colour refused"
grep -v '^#' witnesses.tsv | tail -n +2 > "$T/rw"
nr=0
while IFS="$TAB" read -r w N pats claim edges; do
  "$T/qvr" check "$w" "$pats" | grep -q "^PASS n=$N" || fail "qvr on $w"
  "$T/kabcount" "$w" "$pats" | grep -q "^PASS n=$N" || fail "kabcount on $w"
  "$PY" -I checks/check_char.py "$w" "$pats" | grep -q "^PASS n=$N" || fail "check_char on $w"
  e=$("$PY" -c 'import sys; L=open(sys.argv[1]).read().split(); n,k=int(L[0]),int(L[1]); R=L[2:2+n]; print(",".join(str(sum(R[i][j]==str(c) for i in range(n) for j in range(i+1,n))) for c in range(k)))' "$w")
  [ "$e" = "$edges" ] || fail "edge counts of $w: $e"
  "$PY" -I checks/plant.py "$w" "$pats" "$T/rc" 7 > /dev/null
  for c in "$T"/rc_c*.col; do
    "$T/qvr" check "$c" "$pats" | grep -q "^PASS" && fail "qvr accepted a planted copy ($w)"
    "$T/kabcount" "$c" "$pats" | grep -q "^PASS" && fail "kabcount accepted a planted copy ($w)"
    "$PY" -I checks/check_char.py "$c" "$pats" | grep -q "^PASS" && fail "check_char accepted a planted copy ($w)"
  done
  rm -f "$T"/rc_c*.col
  echo "   $claim: colouring of K_$N PASS (three checkers), edges $edges"
  nr=$((nr + 1))
done < "$T/rw"

echo "9. Ramsey upper-bound formulas: regenerated and compared with the recorded hashes"
grep -v '^#' records/proofs.tsv | tail -n +2 > "$T/rp"
PYSAT=0; "$PY" -c 'import pysat' 2>/dev/null && PYSAT=1
if [ $PYSAT = 1 ]; then mkdir -p "$T/enc"; cp encoders/*.py encoders/sgfind.c "$T/enc/"; cc -O3 -shared -fPIC -o "$T/enc/sgfind.so" "$T/enc/sgfind.c"; fi
while IFS="$TAB" read -r claim N pats h nv ncls secs lb lh gb gh arch; do
  "$T/kabcard" "$N" "$pats" "$T/k.cnf" > /dev/null
  [ "$(sha "$T/k.cnf")" = "$h" ] || fail "formula hash for $claim"
  if [ $PYSAT = 1 ]; then
    "$PY" -I "$T/enc/kab_card.py" "$N" "$pats" "$T/kp.cnf" > /dev/null
    cmp -s "$T/k.cnf" "$T/kp.cnf" || fail "the two Ramsey encoders differ for $claim"
  fi
  echo "   $claim: formula hash as recorded ($nv variables, $ncls clauses)"
done < "$T/rp"
[ $PYSAT = 1 ] && echo "   (both encoders: identical files)" || echo "   (C encoder only; install python-sat to compare the Python encoder too)"
rm -f "$T/k.cnf" "$T/kp.cnf"
cd ..

if command -v cadical > /dev/null && command -v cake_lpr > /dev/null; then
  echo "10. Re-solve two small cases with CaDiCaL and check the LRAT proofs with cake_lpr"
  "$T/ztype" 8 21 4 4 115 "$T/z.cnf" pts 0,11,10,0,0 > /dev/null
  set +e; cadical -q --lrat=true --binary=true "$T/z.cnf" "$T/z.lrat" > /dev/null; rc=$?; set -e
  [ $rc = 20 ] || fail "CaDiCaL on z(8,21;4,4) >= 115 (rc $rc)"
  cake_lpr "$T/z.cnf" "$T/z.lrat" | grep -q "s VERIFIED UNSAT" || fail "cake_lpr on z(8,21;4,4) >= 115"
  rm -f "$T/z.lrat"
  "$T/kabcard" 25 K2,13/K2,3 "$T/r.cnf" > /dev/null
  set +e; cadical -q --lrat=true --binary=true "$T/r.cnf" "$T/r.lrat" > /dev/null; rc=$?; set -e
  [ $rc = 20 ] || fail "CaDiCaL on R(K2,13,K2,3), K25 (rc $rc)"
  cake_lpr "$T/r.cnf" "$T/r.lrat" | grep -q "s VERIFIED UNSAT" || fail "cake_lpr on R(K2,13,K2,3), K25"
  rm -f "$T/r.lrat"
  echo "    z(8,21;4,4) <= 114 (the one case) and R(K2,13,K2,3) <= 25: UNSAT, s VERIFIED UNSAT"
else
  echo "10. (skipped: put cadical and cake_lpr on PATH to re-solve two small cases here)"
fi
echo "ALL CHECKS PASSED: $nw Zarankiewicz witnesses, the bounds and constructions, $ncl case lists, $nf case formulas, $nr Ramsey colourings and 5 Ramsey formulas as recorded."
