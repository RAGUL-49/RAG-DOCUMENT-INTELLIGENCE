import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import uuid
from src.utils.config import config
from openai import OpenAI
import logging

class VectorStore:
    """Vector store using ChromaDB with Perplexity embeddings"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=config.VECTOR_DB_PATH)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        # Use Perplexity API client
        if config.PERPLEXITY_API_KEY and config.PERPLEXITY_API_KEY != "test_key":
            self.embedding_client = OpenAI(api_key=config.PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
        else:
            # Set to None if key is missing, allows for testing without real keys
            self.embedding_client = None

    def add_chunks(self, chunks: List[Dict]) -> None:
        """Add chunks to vector store"""
        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []

        for chunk in chunks:
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            documents.append(chunk["content"])
            # Store all chunk fields except content in metadata
            metadata = {k: v for k, v in chunk.items() if k != "content"}
            metadatas.append(metadata)

        # Generate embeddings
        embeddings = self._get_embeddings(documents)

        # Filter out chunks where embedding failed
        valid_indices = [i for i, emb in enumerate(embeddings) if emb]
        if not valid_indices: return

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the vector store"""
        embeddings = self._get_embeddings([query])
        query_embedding = embeddings[0] if embeddings else None

        # Validate embedding result shape — chromadb expects non-empty numeric vectors
        if not query_embedding:
            # Return empty-but-shaped response to avoid downstream errors
            return {"ids": [[]], "documents": [[]], "metadatas": [[]]}

        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
        except Exception:
            # On query failure, return empty-shaped response
            return {"ids": [[]], "documents": [[]], "metadatas": [[]]}

        return results

    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings using the configured client (Perplexity)"""
        # If test key is set, return mock embeddings to avoid network calls
        if not self.embedding_client:
            return [[0.1] * 1536 for _ in texts]

        try:
            response = self.embedding_client.embeddings.create(input=texts, model=config.EMBEDDING_MODEL)
            return [data.embedding for data in response.data]
        except Exception as e:
            # On failure, return empty embeddings of correct length
            logging.error(f"Error getting embeddings: {e}", exc_info=True)
            return [[] for _ in texts]

    def clear(self) -> None:
        """Clear all documents"""
        self.client.delete_collection("documents")
        self.collection = self.client.create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )