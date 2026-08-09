"""Text utilities used across llmkit."""

def word_count(text: str) -> int:
    """Count whitespace-separated words in ``text``.

    Args:
        text: Input string. May be empty.

    Returns:
        Number of whitespace-separated tokens in ``text``. If ``text`` is empty, returns 0.

    Examples:
        >>> word_count("hello world")
        2
    """
    return len(text.split())


def truncate(text: str, max_chars: int, suffix: str = "...") -> str:
    """Truncate ``text`` to at most ``max_chars`` characters.
    If truncation happens, ``suffix`` is included within the limit.
    The result is never longer than ``max_chars`` characters.

    Args:
        text: Input string. 
        max_chars: Maximum number of the result. must be positive.
        suffix: Marker appended when text is shortened. Default is '...'.

    Returns:
        The original string, or a shortened version ending in ``suffix``. 

    Raises: 
        ValueError: If ``max_chars`` is not positive.
    """

    if max_chars <= 0:
        raise ValueError(f"max_chars must be positive, got {max_chars}")
    if len(text) <= max_chars:
        return text
    if max_chars <= len(suffix):
        return suffix[:max_chars]
    return text[: max_chars - len(suffix)] + suffix

