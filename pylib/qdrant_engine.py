import uuid
from typing import List
from fastembed import TextEmbedding
from qdrant_client import QdrantClient, models
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)

class QdrantEngine:
    def __init__(self, db_path: str="qdrant",
                 collection_name: str="chunks", embedding_model: str="BAAI/bge-small-en-v1.5"):
        self.client = QdrantClient(path=db_path)
        self.collection_name = collection_name
        
        self.fastembed_model = TextEmbedding(model_name=embedding_model)
        self.vector_size = len(list(self.fastembed_model.embed(["dummy"]))[0])

        self._initialize()

    def _document_embedding(self, text: str) -> List[float]:
        return list(self.fastembed_model.embed([text]))[0].tolist()

    def _initialize(self):
        collections = [
            c.name for c in self.client.get_collections().collections]

        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE))

    def reset(self):
        self.client.delete_collection(self.collection_name)
        self._initialize()

    def upload(self, text: str):
        vector = self._document_embedding(text)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": text})])

    def search(self, text: str, limit: int=5) -> List:
        vector = self._document_embedding(text)
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=vector,
            limit=limit)
        
        return [result.payload["text"] for result in results.points]
