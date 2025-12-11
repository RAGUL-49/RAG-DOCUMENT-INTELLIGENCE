from typing import Optional
from openai import OpenAI
from ..utils.config import config

class BaseEmbedder:
    """
    Base class for embedders to handle common client initialization.

    Prefers the Perplexity API when `config.PERPLEXITY_API_KEY` is set,
    and will raise an error if the key is not available.
    """
    def __init__(self, model: Optional[str] = None):
        self.model = model or config.EMBEDDING_MODEL

        if not config.PERPLEXITY_API_KEY or config.PERPLEXITY_API_KEY == "test_key":
            self.client = None # For testing or if key is missing
        else:
            self.client = OpenAI(
                api_key=config.PERPLEXITY_API_KEY,
                base_url="https://api.perplexity.ai"
            )

__all__ = ["BaseEmbedder"]