
import chromadb

_client = None


def get_client():
    """Return the shared Chroma HTTP client."""
    global _client

    if _client is None:
       _client = chromadb.HttpClient(host="localhost", port=8001)

    return _client


def get_collection():
    """Return the jobs collection, creating it if necessary."""
    return get_client().get_or_create_collection(
        "jobs",
        metadata={"hnsw:space": "cosine"},
    )
