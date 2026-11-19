"""Check a SHA256SUMS file (lines: '<hex>  <path>'), paths relative to the current directory (the repository root).
Standard library only."""
import hashlib, os, sys

def main(listing):
    base = os.getcwd()
    bad = 0
    n = 0
    for line in open(listing):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        digest, path = line.split(None, 1)
        path = path.lstrip("*").strip()
        h = hashlib.sha256()
        with open(os.path.join(base, path), "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        n += 1
        if h.hexdigest() != digest:
            print("MISMATCH", path)
            bad += 1
    print(f"sha256: {n - bad}/{n} files match")
    return 1 if bad or n == 0 else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
