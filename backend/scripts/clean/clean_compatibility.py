# backend/scripts/clean_compatibility_json.py
import json, pathlib, re
from bs4 import BeautifulSoup   # pip install beautifulsoup4

# -------- paths --------
RAW_PATH   = pathlib.Path("data/compatibility.json")        # your existing file
CLEAN_PATH = RAW_PATH.with_name("compatibility_clean.json")

# -------- helpers --------
MODEL_RE = re.compile(r"\b[A-Z0-9-]{5,}\b")
BAD_PREFIXES = ("GTM", "HTTP", "HTTPS", "WWW", "MODEL", "QUESTION", "1-866")
def looks_like_model(tok: str) -> bool:
    return (len(tok) >= 6 and tok.isupper()
            and any(c.isdigit() for c in tok)
            and any(c.isalpha() for c in tok)
            and not tok.startswith(BAD_PREFIXES))

BRAND_HINTS = [
    "Whirlpool","KitchenAid","Maytag","GE","Frigidaire",
    "Samsung","LG","Bosch","Amana","Kenmore"
]

def strip_html(html: str) -> str:
    return " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())

# -------- main clean pass --------
raw_docs = json.loads(RAW_PATH.read_text())
clean_docs = []

for doc in raw_docs:
    models = [m for m in doc.get("models", []) if looks_like_model(m)]
    models = list(dict.fromkeys(models))[:40]   # dedupe + cap

    if not models:
        continue  # skip if no usable models

    raw_text = doc.get("text", "")
    text_clean = strip_html(raw_text)
    summary = f"Compatible models: {', '.join(models)}."

    # rebuild record
    new_doc = {
        "id":           doc["id"],
        "part_number":  doc.get("part_number",""),
        "title":        doc.get("title",""),
        "url":          doc.get("url",""),
        "models":       models,
        "text":         summary + " " + text_clean[:300],
    }

    # detect brands dynamically
    brands = [b for b in BRAND_HINTS if b.lower() in text_clean.lower()]
    if brands:
        new_doc["brands"] = brands

    clean_docs.append(new_doc)

print(f"Kept {len(clean_docs)} docs (filtered from {len(raw_docs)})")
CLEAN_PATH.write_text(json.dumps(clean_docs, indent=2))
print(f"Wrote cleaned file → {CLEAN_PATH.resolve()}")