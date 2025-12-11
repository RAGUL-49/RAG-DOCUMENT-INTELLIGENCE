import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    """Central configuration for MultiDoc-IntelliAgent"""
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    PERPLEXITY_API_KEY: str = os.getenv("PERPLEXITY_API_KEY", "")
    
    # Paths
    RAW_DOCUMENTS_PATH: str = "data/raw_documents"
    PROCESSED_CHUNKS_PATH: str = "data/processed_chunks"
    VECTOR_DB_PATH: str = "data/vector_db"
    
    # Model Settings
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "llama-3.1-sonar-large-128k-online"
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    
    # Retrieval Settings
    TOP_K: int = 5
    RERANK_TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.7
    
    # OCR Settings
    TESSERACT_CMD: Optional[str] = None  # Set path if needed
    
    def __post_init__(self):
        # Create directories if they don't exist
        os.makedirs(self.RAW_DOCUMENTS_PATH, exist_ok=True)
        os.makedirs(self.PROCESSED_CHUNKS_PATH, exist_ok=True)
        os.makedirs(self.VECTOR_DB_PATH, exist_ok=True)

config = Config()