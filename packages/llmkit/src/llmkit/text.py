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

    Examples:
        >>> truncate("hello world", 8)
        'hello...'

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


def normalize_whitespace(text: str) -> str:
    """Collapse all runs of whitespace to single whitespace and strip leading/trailing whitespace.

    Args:
        text: Input string. Newlines and tabs count as whitespace.

    Returns:
        The text with every whitespace run reduced to one space, no leading or trailing whitespace.

    Examples:
        >>> normalize_whitespace("a\\n\\n b\\t\\tc ")
        'a b c'
    """
    return " ".join(text.split())


def chunk_text(text: str, size: int, overlap: int = 0) -> list[str]:
    """Split ``text`` into character chunks of length ``size``.

    Each chunk overlaps the previous one by ``overlap`` characters.

    Args:
        text: Input string.
        size: Chunk length in characters. Must be positive.
        overlap: Number of characters each chunk shares with the previous chunk.
            Must be non-negative and strictly less than ``size``.

    Returns:
        A list of character chunks in order. Empty input returns an empty list.
        The last chunk may be shorter than ``size``.

    Raises:
        ValueError: If ``size <= 0``, ``overlap < 0``, or ``overlap >= size``.

    Examples:
        >>> chunk_text("abcdefghij", 4)
        ['abcd', 'efgh', 'ij']
        >>> chunk_text("abcdefghij", size=4, overlap=2)
        ['abcd', 'cdef', 'efgh', 'ghij', 'ij']

    Note:
        ``step = size - overlap`` controls how far the window advances. With
        size=4 and overlap=2, step=2, so windows start at 0, 2, 4, 6, 8.
    """
    if size <= 0:
        raise ValueError(f"size must be positive, got {size}")
    if overlap < 0:
        raise ValueError(f"overlap must be non-negative, got {overlap}")
    if overlap >= size:
        # Guarantees step > 0; range() also rejects a zero step outright.
        raise ValueError(f"overlap ({overlap}) must be less than the size ({size})")

    if not text:
        return []

    step = size - overlap
    return [text[i : i + size] for i in range(0, len(text), step)]
