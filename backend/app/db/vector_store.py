import chromadb

_client = chromadb.PersistentClient(path="data/chroma")


def get_collection():
    return _client.get_or_create_collection("jobs", metadata={"hnsw:space": "cosine"})