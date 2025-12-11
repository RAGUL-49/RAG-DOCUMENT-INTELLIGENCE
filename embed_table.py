
from typing import List, Dict, Optional
import json
import logging
from .base_embedder import BaseEmbedder


class TableEmbedder(BaseEmbedder):
	"""Convert structured table content to textual form and embed it."""

	def _table_to_text(self, table_content) -> str:
		"""Convert a table (JSON string or list of dicts) to a readable text block."""
		if isinstance(table_content, str):
			try:
				rows = json.loads(table_content)
			except Exception:
				return table_content
		else:
			rows = table_content

		lines = []
		if isinstance(rows, list):
			for r in rows:
				if isinstance(r, dict):
					parts = [f"{k}: {v}" for k, v in r.items()]
					lines.append("; ".join(parts))
				else:
					lines.append(str(r))
		else:
			lines.append(str(rows))

		return "\n".join(lines)

	def embed_tables(self, tables: List[Dict]) -> List[Dict]:
		"""Embed a list of table dicts where each dict contains a `content` field.

		Returns list of dicts with `text`, `embedding`, and original `metadata`.
		"""
		texts = []
		metadatas = []

		for t in tables:
			content = t.get("content")
			text = self._table_to_text(content)
			texts.append(text)
			metadata = {k: v for k, v in t.items() if k != "content"}
			metadatas.append(metadata)

		try:
			response = self.client.embeddings.create(input=texts, model=self.model)
			embeddings = [d.embedding for d in response.data]
		except Exception as e:
			logging.error(f"Error in TableEmbedder: {e}", exc_info=True)
			embeddings = [[] for _ in texts]

		results = []
		for text, emb, meta in zip(texts, embeddings, metadatas):
			results.append({"text": text, "embedding": emb, "metadata": meta})

		return results


__all__ = ["TableEmbedder"]
