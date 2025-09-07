# backend/scripts/ingest_chroma.py
import os, json, argparse
from pathlib import Path
from typing import Dict, Any, List

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ---- Config: where your JSONs live
DATA_DIR = Path("data")
FILES = {
    "installation": DATA_DIR / "installation.json",
    "compatibility": DATA_DIR / "compatibility.json",
    "troubleshooting": DATA_DIR / "troubleshooting.json",
}

def load_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        print(f"[warn] missing file: {path}")
        return []
    return json.loads(path.read_text())

def to_doc(source: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a record into {id, document, metadata} for Chroma.
    We keep source-specific fields in metadata for filtering later.
    """
    # Common
    rid = raw.get("id") or f"{source}-{raw.get('part_number') or raw.get('title')}"
    doc_text = (raw.get("text") or "").strip()
    url = (raw.get("url") or "").split("?", 1)[0]  # normalize URLs (drop tracking)

    meta: Dict[str, Any] = {
        "source": source,
        "title": raw.get("title", ""),
        "url": url,
        "part_number": raw.get("part_number", ""),
        "appliance": raw.get("appliance", ""),
    }

    # Source-specific enrichments
    if source == "installation":
        tools = raw.get("tools", [])
        meta.update({
            "difficulty": raw.get("difficulty", ""),
            "time_required": raw.get("time_required", ""),
            "tools": ", ".join(tools) if isinstance(tools, list) else str(tools),
        })
    elif source == "compatibility":
        # models/brands often large; keep but cap for metadata weight
        models = raw.get("models") or []
        brands = raw.get("brands", [])
        meta.update({
            "models": ", ".join(models[:100]) if isinstance(models, list) else str(models),
            "brands": ", ".join(brands) if isinstance(brands, list) else str(brands),
            "notes": raw.get("notes", ""),
        })
    elif source == "troubleshooting":
        common_parts = raw.get("common_parts", [])
        # Convert common_parts list to a string summary for metadata
        part_names = []
        if isinstance(common_parts, list):
            for part in common_parts:
                if isinstance(part, dict) and "part_name" in part:
                    part_names.append(part["part_name"])
        
        meta.update({
            "symptom": raw.get("symptom", ""),
            "common_parts": ", ".join(part_names),  # Convert to comma-separated string
        })

    return {"id": rid, "document": doc_text, "metadata": meta}

def batch(iterable, size=100):
    buf = []
    for x in iterable:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf

def main(collection_name: str, persist_dir: str, dry_run: bool):
    # ---- Embeddings
    openai_key = os.getenv("OPENAI_API_KEY")
    print(f"[debug] OPENAI_API_KEY found: {'YES' if openai_key else 'NO'}")
    if openai_key:
        print(f"[debug] Key length: {len(openai_key)}")
    
    if not openai_key and not dry_run:
        raise SystemExit("OPENAI_API_KEY not set")

    # ---- Skip Chroma setup during dry run
    if not dry_run:
        # ---- Chroma client (persist to disk so your app can reuse it)
        client = chromadb.Client(
            Settings(
                is_persistent=bool(persist_dir),
                persist_directory=persist_dir or None,
            )
        )
        embed_fn = OpenAIEmbeddingFunction(api_key=openai_key, model_name="text-embedding-3-small")

        collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=embed_fn
        )

    # ---- Load + normalize
    raw_count = 0
    docs: List[Dict[str, Any]] = []
    for source, path in FILES.items():
        rows = load_json(path)
        raw_count += len(rows)
        for r in rows:
            d = to_doc(source, r)
            # skip empty documents
            if not d["document"]:
                continue
            docs.append(d)

    if dry_run:
        print(f"[dry-run] loaded {raw_count} records; {len(docs)} non-empty docs to ingest.")
        # show a tiny sample
        for s in docs[:2]:
            print(f"— {s['id']}  ({s['metadata']['source']})  url={s['metadata'].get('url')}")
        return

    # ---- Optional: clear collection (comment out if you want to append)
    # collection.delete(where={})  # careful: wipes the collection

    # ---- Dedup by id (in case you re-run)
    seen = set()
    unique_docs = []
    for d in docs:
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        unique_docs.append(d)

    if not dry_run:
        # ---- Ingest in batches
        inserted = 0
        for chunk in batch(unique_docs, size=128):
            collection.add(
                ids=[c["id"] for c in chunk],
                documents=[c["document"] for c in chunk],
                metadatas=[c["metadata"] for c in chunk],
            )
            inserted += len(chunk)
            print(f"[ingest] total inserted: {inserted}")

        # ChromaDB with persistent storage automatically saves to disk
        print(f"✅ done. inserted {inserted} docs into '{collection_name}' (persist_dir={persist_dir})")
    else:
        print(f"[dry-run] would have inserted {len(unique_docs)} unique docs into '{collection_name}'")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--collection", default="partselect-docs", help="Chroma collection name")
    parser.add_argument("--persist_dir", default="chroma_store", help="Directory to persist Chroma ('' for in-memory)")
    parser.add_argument("--dry_run", action="store_true", help="Load/normalize only; do not write to Chroma")
    args = parser.parse_args()

    main(collection_name=args.collection, persist_dir=args.persist_dir, dry_run=args.dry_run)