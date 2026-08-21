# llmkit

Small, well-tested Python utilities for building LLM applications.

## Metrics

- 16 tests, **100% coverage** across 4 text utilities.
    - Report generated with `uv run --package llmkit python -m pytest --cov=llmkit --cov-report=term-missing`
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

## Development

```bash
uv sync --all-packages --extra dev   # install everything
uv run ruff check .                  # lint
uv run ruff format .                 # format
uv run mypy                          # type check
uv run --package llmkit python -m pytest -v
uv run pre-commit run --all-files    # everything at once
```

## What I learned

- **src/ layout** prevents a class of test bugs: tests run against the *installed* package, not a folder that happens to be importable — so green tests actually mean the shipped thing works.
- **pyproject.toml declares ranges, uv.lock pins reality.** Commit both; `uv sync` reproduces the environment byte-for-byte.
- **Fail loudly, early.** `truncate` and `chunk_text` raise `ValueError` on bad input instead of silently coping — a silent bug surfaces three services away.
- **Off-by-one in chunking** is the whole game: the window advances by `size - overlap`, not `size`. This is the naive version of RAG chunking.
- Some of **`uv`** best practices while developing.
