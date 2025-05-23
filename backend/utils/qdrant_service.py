# Qdrant service
from typing import Callable
from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, models

from utils.configs import EMBEDDING_DIM, QDRANT_HOST


class QdrantService:
    def __init__(
        self,
        host=QDRANT_HOST,
        create_default_collection: bool = True,
        embedding_dim: int = EMBEDDING_DIM,
    ) -> None:
        self.client = QdrantClient(url=host)
        if create_default_collection and not self.client.collection_exists("test"):
            print("Creating default collection")
            self.create_collection("test", embedding_dim, recreate=False)

    def create_collection(
        self,
        collection_name: str,
        vector_dim: int = EMBEDDING_DIM,
        recreate: bool = True,
    ):
        # @TODO parametrize other configs
        if self.client.collection_exists("test"):
            if recreate:
                print("Collection already exists..Deleting existing collection")
                self.delete_collection(collection_name=collection_name)
            else:
                print("Collection already exists, not creating again")
                return
        print(f"Creating new collection - {collection_name}")
        return self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.DOT),
        )

    def insert_docs(
        self,
        collection_name: str,
        docs: list,
        embedding_func: Callable[[list[str]], list],
        include_doc_in_payload: bool = True,
        metadatas: list[dict] = None,
    ):
        if not self.client.collection_exists(collection_name):
            print("Collection does not exist.. creating one")
            self.create_collection(
                collection_name,
            )

        if include_doc_in_payload:
            if metadatas:
                for metadata, doc in zip(metadatas, docs):
                    metadata.update({"text": doc})
            else:
                metadatas = [{"text": doc} for doc in docs]
        embeddings = embedding_func(docs)
        ids = [uuid4().hex for _ in range(len(embeddings))]
        return self.client.upsert(
            collection_name=collection_name,
            points=models.Batch(
                ids=ids, vectors=embeddings, payloads=metadatas if metadatas else None
            ),
        )

    def delete_collection(self, collection_name: str):
        return self.client.delete_collection(collection_name=collection_name)

    def get_similar_docs(
        self,
        query: str,
        embedding_func: Callable[[list[str]], list],
        collection_name: str,
        top_k: int = 3,
    ):
        embedding = embedding_func([query])[0]
        return self.client.query_points(
            collection_name=collection_name,
            query=embedding,
            with_payload=True,
            limit=top_k,
        ).points
