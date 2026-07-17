from pathlib import Path

from pypdf import PdfReader

from rag.vectorstore import client, model, COLLECTION_NAME


BASE_DIR = Path(__file__).resolve().parent.parent

PDF_PATH = BASE_DIR / "resources" / "resume.pdf"
SUMMARY_PATH = BASE_DIR / "resources" / "summary.txt"


# ---------------------------------------------------
# Load documents
# ---------------------------------------------------

documents = []

if SUMMARY_PATH.exists():

    summary = SUMMARY_PATH.read_text(encoding="utf-8")

    documents.append(
        {
            "source": "summary",
            "text": summary
        }
    )


if PDF_PATH.exists():

    reader = PdfReader(PDF_PATH)

    resume = ""

    for page in reader.pages:

        text = page.extract_text()

        if text:
            resume += text + "\n"

    documents.append(
        {
            "source": "resume",
            "text": resume
        }
    )


# ---------------------------------------------------
# Chunk documents
# ---------------------------------------------------

CHUNK_SIZE = 500
OVERLAP = 100

chunks = []

for document in documents:

    text = document["text"]

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunks.append(
            {
                "text": text[start:end],
                "source": document["source"]
            }
        )

        start += CHUNK_SIZE - OVERLAP


print(f"Created {len(chunks)} chunks")


# ---------------------------------------------------
# Create embeddings
# ---------------------------------------------------

texts = [chunk["text"] for chunk in chunks]

embeddings = model.encode(texts).tolist()


# ---------------------------------------------------
# Recreate collection
# ---------------------------------------------------

try:
    client.delete_collection(COLLECTION_NAME)
except Exception:
    pass

collection = client.create_collection(COLLECTION_NAME)


# ---------------------------------------------------
# Store chunks
# ---------------------------------------------------

collection.add(
    ids=[str(i) for i in range(len(chunks))],
    documents=texts,
    embeddings=embeddings,
    metadatas=[
        {
            "source": chunk["source"]
        }
        for chunk in chunks
    ]
)

print(f"Stored {collection.count()} chunks.")