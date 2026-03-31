from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client()

def get_or_create_collection(session_id: str):
    return client.get_or_create_collection(name = session_id)

def add_chunks(session_id: str, chunks: list[str]):
    collection = get_or_create_collection(session_id)
    embeddings = model.encode(chunks).tolist()
    collection.add(
        documents = chunks,
        embeddings = embeddings,
        ids = [f"chunk_{i}" for i in range(len(chunks))]
    )

def retrieve(session_id: str, query: str, top_k: int = 4) -> list[str]:
    collection = get_or_create_collection(session_id)
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings = query_embedding, n_results = top_k)
    return results["documents"][0]