from typing import List, Dict, Optional
import numpy as np
from src.vector_db import VectorDatabase
from src.embeddings import generate_query_embedding
from src.config import get_config


class Retriever:
    def __init__(
        self,
        vector_db: VectorDatabase,
        top_k: int = 4,
    ):
        self.vector_db = vector_db
        self.top_k = top_k
    
    def retrieve(self, query: str) -> List[Dict]:
        query_embedding = generate_query_embedding(query)
        results = self.vector_db.search(query_embedding, top_k=self.top_k)
        return results
    
    def retrieve_with_metadata(
        self,
        query: str,
        filter_dict: Optional[Dict] = None,
    ) -> List[Dict]:
        query_embedding = generate_query_embedding(query)
        results = self.vector_db.search(query_embedding, top_k=self.top_k, filter_dict=filter_dict)
        return results
    
    def format_sources(self, results: List[Dict]) -> List[Dict]:
        sources = []
        seen_urls = set()
        
        for result in results:
            metadata = result.get("metadata", {})
            url = metadata.get("source_url", "")
            title = metadata.get("source_title", "Unknown Source")
            
            if url and url not in seen_urls:
                seen_urls.add(url)
                sources.append({
                    "title": title,
                    "url": url,
                    "score": result.get("score", 0),
                })
        
        return sources


def create_retriever(
    vector_db: VectorDatabase,
    top_k: int = 4,
) -> Retriever:
    return Retriever(vector_db, top_k)