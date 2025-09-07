import json, re, textwrap, pathlib

MODEL_OK = re.compile(r"(?=.*[A-Z])(?=.*\d)[A-Z0-9\-]{5,}$")

def clean_rec(rec):
    rec["models"] = sorted({m for m in rec["models"] if MODEL_OK.match(m)})
    rec["text"]   = textwrap.shorten(rec["text"], 300, placeholder=" …")
    return rec

path_in  = pathlib.Path("data/compatibility_cleaned.json")
path_out = pathlib.Path("data/compatibility_final.json")

docs = [clean_rec(d) for d in json.loads(path_in.read_text())]
path_out.write_text(json.dumps(docs, indent=2))
print(f"Wrote {len(docs)} cleaned docs → {path_out}")