
from typing import List, Dict, Optional
import logging
from .base_embedder import BaseEmbedder


class TextEmbedder(BaseEmbedder):
	"""Create embeddings for text content."""

	def embed_texts(self, texts: List[str]) -> List[List[float]]:
		"""Return embeddings for a list of strings."""
		if not texts:
			return []

		try:
			response = self.client.embeddings.create(input=texts, model=self.model)
			# Correctly access the embedding from the response object
			embeddings = [d.embedding for d in response.data]
			return embeddings
		except Exception as e:
			logging.error(f"Error in TextEmbedder: {e}", exc_info=True)
			return [[] for _ in texts]


__all__ = ["TextEmbedder"]
