"""llmkit - small utilities for building LLM applications."""
__version__ = "0.1.0"

from llmkit.text import truncate, word_count, normalize_whitespace, chunk_text

__all__ = ["__version__", "truncate", "word_count", "normalize_whitespace", "chunk_text"]