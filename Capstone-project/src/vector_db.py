import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
import numpy as np
from pathlib import Path
import json


class VectorDatabase:
    def __init__(
        self,
        persist_directory: str = "./vectorstore",
        collection_name: str = "college_knowledge",
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    
    def add_chunks(
        self,
        chunks: List[Dict],
        embeddings: np.ndarray,
    ) -> List[str]:
        if not chunks:
            raise ValueError(
                "No text chunks are available to add. The configured pages "
                "may be blocked, empty, or inaccessible."
            )

        embeddings_array = np.asarray(embeddings)
        if embeddings_array.size == 0:
            raise ValueError("No embeddings were generated for the text chunks.")
        if len(chunks) != len(embeddings_array):
            raise ValueError(
                f"Chunk/embedding count mismatch: {len(chunks)} chunks and "
                f"{len(embeddings_array)} embeddings."
            )

        ids = [str(chunk["metadata"].get("global_index", f"chunk_{i}")) for i, chunk in enumerate(chunks)]
        
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings_array.tolist(),
            metadatas=metadatas,
        )
        
        return ids
    
    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 4,
        filter_dict: Optional[Dict] = None,
    ) -> List[Dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filter_dict,
            include=["documents", "metadatas", "distances"],
        )
        
        if not results["documents"] or not results["documents"][0]:
            return []
        
        docs = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "score": 1 - dist,
            }
            for doc, meta, dist in zip(docs, metadatas, distances)
        ]
    
    def get_collection_info(self) -> Dict:
        count = self.collection.count()
        return {
            "count": count,
            "name": self.collection_name,
            "persist_directory": self.persist_directory,
        }
    
    def delete_collection(self):
        self.client.delete_collection(name=self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    
    def get_all_documents(self) -> List[Dict]:
        results = self.collection.get(include=["documents", "metadatas"])
        return [
            {"content": doc, "metadata": meta}
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]


def create_vector_db(
    persist_directory: str = "./vectorstore",
    collection_name: str = "college_knowledge",
) -> VectorDatabase:
    return VectorDatabase(persist_directory, collection_name)
