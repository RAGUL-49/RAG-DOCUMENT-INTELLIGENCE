from PIL import Image
from typing import List, Dict, Optional
import io
import pytesseract
import logging
from .base_embedder import BaseEmbedder


class ImageEmbedder(BaseEmbedder):
	"""Embed images by extracting text (OCR) and creating text embeddings."""

	def _ocr_image(self, image: Image.Image) -> str:
		try:
			text = pytesseract.image_to_string(image)
			return text.strip()
		except Exception:
			return ""

	def embed_images(self, images: List[Image.Image], sources: Optional[List[Dict]] = None) -> List[Dict]:
		"""Return embeddings for a list of PIL images.

		Args:
			images: list of PIL `Image` objects.
			sources: optional list of metadata dicts (one per image) that will
					 be attached to the returned items.

		Returns:
			A list of dicts: each contains `embedding` (list[float]), `text`
			(the OCR'd text or placeholder) and `metadata`.
		"""
		texts = []
		metadatas = []

		for idx, img in enumerate(images):
			text = self._ocr_image(img)
			metadata = (sources[idx] if sources and idx < len(sources) else {})

			if not text:
				# Minimal descriptive placeholder to still get an embedding
				source_desc = metadata.get("source") or metadata.get("page") or f"image_{idx}"
				text = f"Image content (no extracted text) from {source_desc}"

			texts.append(text)
			metadatas.append(metadata)

		# Use the configured client to get embeddings for the extracted texts
		try:
			response = self.client.embeddings.create(input=texts, model=self.model)
			embeddings = [d.embedding for d in response.data]
		except Exception as e:
			logging.error(f"Error in ImageEmbedder: {e}", exc_info=True)
			# In case embedding call fails, return empty embeddings list of same length
			embeddings = [[] for _ in texts]

		results = []
		for text, emb, meta in zip(texts, embeddings, metadatas):
			results.append({"text": text, "embedding": emb, "metadata": meta})

		return results

	def embed_image_bytes(self, image_bytes: bytes, metadata: Optional[Dict] = None) -> Dict:
		"""Convenience helper to embed a single image provided as raw bytes."""
		try:
			image = Image.open(io.BytesIO(image_bytes))
		except Exception:
			raise ValueError("Invalid image bytes provided")

		return self.embed_images([image], sources=[metadata or {}])[0]


__all__ = ["ImageEmbedder"]
