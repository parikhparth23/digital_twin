from rag.vectorstore import client, model, COLLECTION_NAME


collection = client.get_collection(COLLECTION_NAME)


def retrieve_resume(query: str):

    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=5,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results["documents"][0]

    return "\n\n".join(documents)