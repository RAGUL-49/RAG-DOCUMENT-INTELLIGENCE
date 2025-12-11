from typing import List, Dict
from ..embedding.vector_store import VectorStore
from ..utils.config import config

class Retriever:
    """Retrieve relevant chunks from vector store"""
    
    def __init__(self):
        self.vector_store = VectorStore()
    
    def retrieve(self, query: str, top_k: int = None) -> List[Dict]:
        """Retrieve top-k relevant chunks"""
        top_k = top_k or config.TOP_K
        
        results = self.vector_store.query(query, top_k)
        
        # Format results
        chunks = []
        for i in range(len(results['ids'][0])):
            chunk = {
                'id': results['ids'][0][i],
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            chunks.append(chunk)
        
        return chunks
