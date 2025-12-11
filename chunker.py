from typing import List, Dict
import logging
from ..utils.config import config

class Chunker:
    """Split documents into manageable chunks"""
    
    def __init__(self, chunk_size: int = None, overlap: int = None):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.overlap = overlap or config.CHUNK_OVERLAP

    def process_chunk(self, chunk: Dict) -> List[Dict]:
        """
        Decides whether to chunk a given piece of content.
        Only 'text' type chunks that exceed the chunk size are split.
        """
        if chunk.get("type") == "text" and len(chunk.get("content", "").split()) > self.chunk_size:
            metadata = {k: v for k, v in chunk.items() if k != "content"}
            return self.chunk_by_sentence(chunk["content"], metadata)
        else:
            # Return non-text chunks or small text chunks as-is
            return [chunk]
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunks.append({
                **metadata,
                "content": chunk_text,
                "chunk_index": len(chunks)
            })
        
        return chunks
    
    def chunk_by_sentence(self, text: str, metadata: Dict) -> List[Dict]:
        """Split by sentences for better semantic coherence"""
        import nltk
        try:
            sentences = nltk.sent_tokenize(text)
        except Exception as e:
            sentences = text.split('. ')
            logging.warning(f"NLTK sentence tokenizer failed: {e}. Falling back to splitting by '. '.")
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunks.append({
                    **metadata,
                    "content": ' '.join(current_chunk),
                    "chunk_index": len(chunks)
                })
                current_chunk = current_chunk[-self.overlap:] if self.overlap > 0 else []
                current_length = sum(len(s.split()) for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        if current_chunk:
            chunks.append({
                **metadata,
                "content": ' '.join(current_chunk),
                "chunk_index": len(chunks)
            })
        
        return chunks
