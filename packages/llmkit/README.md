# llmkit

Small, well-tested Python utilities for building LLM applications.

## Metrics

<<<<<<< HEAD
- 17 tests, **100% coverage** across 4 text utilities. 
    - Report generated with `uv run --package llmkit python -m pytest --cov=llmkit --cov-report=term-missing` 
=======
- 16 tests, **100% coverage** across 4 text utilities.
    - Report generated with `uv run --package llmkit python -m pytest --cov=llmkit --cov-report=term-missing`
>>>>>>> 01edc5a (chore: run rff and mypy till clean and add pre-commit git hook)
- Zero runtime dependencies

## Install

From the workspace root:

```bash
uv sync --all-packages
```

## Usage

```python
from llmkit import word_count, truncate, normalize_whitespace, chunk_text

word_count("hello world")  # 2
truncate("hello world", 8)  # "hello..."
normalize_whitespace("a\n\n b\t\tc ")  # "a b c"
chunk_text("abcdefghij", 4, overlap=2)  # ["abcd", "cdef", "efgh", "ghij", "ij"]
```

## What I learned

- **src/ layout** prevents a class of test bugs: tests run against the *installed* package, not a folder that happens to be importable — so green tests actually mean the shipped thing works.
- **pyproject.toml declares ranges, uv.lock pins reality.** Commit both; `uv sync` reproduces the environment byte-for-byte.
- **Fail loudly, early.** `truncate` and `chunk_text` raise `ValueError` on bad input instead of silently coping — a silent bug surfaces three services away.
- **Off-by-one in chunking** is the whole game: the window advances by `size - overlap`, not `size`. This is the naive version of RAG chunking.
<<<<<<< HEAD
- Some of **`uv`** best practices while developing. 
=======
- Some of **`uv`** best practices while developing.
>>>>>>> 01edc5a (chore: run rff and mypy till clean and add pre-commit git hook)
