import os
import pandas as pd
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
chroma = chromadb.PersistentClient(path="backend/chroma_db")

def dedupe_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate part_ids so Chroma IDs are unique."""
    before = len(df)
    df = df.drop_duplicates(subset=["part_id"]).reset_index(drop=True)
    after = len(df)
    if before != after:
        print(f"⚠️ Dropped {before - after} duplicate rows (based on part_id)")
    return df

def ingest_csv(csv_path, collection_name):
    df = pd.read_csv(csv_path).fillna("")
    df = dedupe_dataframe(df)  # 🧹 remove dupes before ingest

    col = chroma.get_or_create_collection(
        collection_name, metadata={"hnsw:space":"cosine"}
    )

    docs = (
        df["title"] + " — " + df["description"] +
        " | brand: " + df["brand"] + " | part_id: " + df["part_id"]
    ).tolist()
    ids = df["part_id"].tolist()
    metas = df.to_dict(orient="records")

    for i in range(0, len(docs), 128):
        batch = docs[i:i+128]
        emb = client.embeddings.create(model="text-embedding-3-small", input=batch).data
        vectors = [e.embedding for e in emb]
        col.add(
            ids=ids[i:i+128],
            documents=batch,
            metadatas=metas[i:i+128],
            embeddings=vectors,
        )

    print(f"✅ Ingested {len(docs)} records into `{collection_name}`")

if __name__ == "__main__":
    ingest_csv("data/appliance_parts_dishwasher.csv", "dishwasher_parts")
    ingest_csv("data/appliance_parts_refrigerator.csv", "refrigerator_parts")