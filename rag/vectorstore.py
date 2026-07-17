import chromadb
from sentence_transformers import SentenceTransformer


DB_PATH = "chroma_db"
COLLECTION_NAME = "resume"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


model = SentenceTransformer(EMBEDDING_MODEL)

client = chromadb.PersistentClient(path=DB_PATH)