from typing import List, Dict
from sentence_transformers import CrossEncoder
from ..utils.config import config

class Reranker:
    """Rerank retrieved chunks for better relevance"""
    
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.model = CrossEncoder(model_name)
    
    def rerank(self, query: str, chunks: List[Dict], top_k: int = None) -> List[Dict]:
        """Rerank chunks based on query relevance"""
        top_k = top_k or config.RERANK_TOP_K
        
        if not chunks:
            return []
        
        # Prepare pairs for cross-encoder
        pairs = [[query, chunk['content']] for chunk in chunks]
        
        # Get relevance scores
        scores = self.model.predict(pairs)
        
        # Add scores to chunks
        for chunk, score in zip(chunks, scores):
            chunk['rerank_score'] = float(score)
        
        # Sort by score and return top-k
        chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return chunks[:top_k]