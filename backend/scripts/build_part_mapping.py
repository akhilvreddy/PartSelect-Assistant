import json, pathlib, re, argparse
from collections import defaultdict

IN_PATH  = pathlib.Path("data/compatibility.json")
OUT_DIR  = pathlib.Path("data/maps")
P2M_PATH = OUT_DIR / "parts_to_models.json"
M2P_PATH = OUT_DIR / "model_to_parts.json"

# basic sanity: model tokens must have letters+digits and be >=5 chars
MODEL_OK = re.compile(r"(?=.*[A-Za-z])(?=.*\d).{5,}")

def norm_model(s: str) -> str:
    return s.strip().upper().replace("–","-").replace("—","-")

def main(in_path=IN_PATH, out_dir=OUT_DIR, dry_run=False):
    data = json.loads(in_path.read_text())
    parts_to_models = defaultdict(set)
    model_to_parts = defaultdict(set)

    for row in data:
        part = (row.get("part_number") or "").strip().upper()
        if not part:
            continue
        models = row.get("models") or []
        cleaned = []
        for m in models:
            if not isinstance(m, str): 
                continue
            mm = norm_model(m)
            if MODEL_OK.fullmatch(mm):
                cleaned.append(mm)

        for m in set(cleaned):
            parts_to_models[part].add(m)
            model_to_parts[m].add(part)

    # convert sets to sorted lists
    p2m = {p: sorted(ms) for p, ms in parts_to_models.items()}
    m2p = {m: sorted(ps) for m, ps in model_to_parts.items()}

    if dry_run:
        print(f"[dry-run] parts: {len(p2m)} unique part_numbers")
        print(f"[dry-run] models: {len(m2p)} unique models")
        # peek a few
        for k in list(p2m)[:3]:
            print("  ", k, "→", p2m[k][:8], "…")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    P2M_PATH.write_text(json.dumps(p2m, indent=2))
    M2P_PATH.write_text(json.dumps(m2p, indent=2))
    print(f"✔ wrote {P2M_PATH} ({len(p2m)} parts)")
    print(f"✔ wrote {M2P_PATH} ({len(m2p)} models)")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="in_path", default=str(IN_PATH))
    ap.add_argument("--outdir", dest="out_dir", default=str(OUT_DIR))
    ap.add_argument("--dry_run", action="store_true")
    args = ap.parse_args()
    main(in_path=pathlib.Path(args.in_path), out_dir=pathlib.Path(args.out_dir), dry_run=args.dry_run)