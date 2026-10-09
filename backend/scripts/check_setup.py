from pymongo import MongoClient
import ollama
import chromadb

client = MongoClient(
    "mongodb://localhost:27017",
    serverSelectionTimeoutMS=3000
)

print("MongoDB OK, version:", client.server_info()["version"])

print("Ollama models:", [m.model for m in ollama.list().models])

chromadb.PersistentClient(path="data/chroma")
print("Chroma OK")