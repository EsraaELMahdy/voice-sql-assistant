import chromadb
from fastembed import TextEmbedding

from src import config
from src.examples import EXAMPLES

_model = None
_collection = None


def get_model():
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=config.EMBEDDING_MODEL)
    return _model


def embed(texts):
    return [vector.tolist() for vector in get_model().embed(texts)]


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.EphemeralClient()
        collection = client.get_or_create_collection(
            name="sql_examples",
            metadata={"hnsw:space": "cosine"},
        )
        questions = [item["question"] for item in EXAMPLES]
        collection.add(
            ids=[str(index) for index in range(len(EXAMPLES))],
            embeddings=embed(questions),
            documents=questions,
            metadatas=[{"sql": item["sql"]} for item in EXAMPLES],
        )
        _collection = collection
    return _collection


def find_examples(question, limit=None):
    limit = limit or config.TOP_K_EXAMPLES
    result = get_collection().query(query_embeddings=embed([question]), n_results=limit)
    return [
        {"question": document, "sql": metadata["sql"], "score": 1 - distance}
        for document, metadata, distance in zip(
            result["documents"][0], result["metadatas"][0], result["distances"][0]
        )
    ]