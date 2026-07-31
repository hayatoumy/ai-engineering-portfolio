"""
Day 1 — stop_reason probe.

    uv run python stop_reason_probe.py

Deliberately triggers the stop_reason values you can reach without tool use,
and dumps one full response object so you can see every field.
"""

import json

from ai_engineering_portfolio.cost import tracked_create
from ai_engineering_portfolio.models import HAIKU


def show(label: str, r) -> None:
    print(f"\n{'=' * 62}\n{label}\n{'=' * 62}")
    print(f"stop_reason   : {r.stop_reason!r}")
    print(f"stop_sequence : {r.stop_sequence!r}")
    print(f"content blocks: {[b.type for b in r.content]}")
    text = "".join(b.text for b in r.content if b.type == "text")
    print(f"text          : {text!r}")
    print(f"usage         : in={r.usage.input_tokens} out={r.usage.output_tokens}")


# 1. end_turn -- the model finished on its own.
show("1. end_turn", tracked_create(
    model=HAIKU,
    max_tokens=100,
    messages=[{"role": "user", "content": "Name three primary colors."}],
))

# 2. max_tokens -- YOUR ceiling cut it off. Note that `content` is present but
#    truncated mid-thought. This is the silent-corruption case: a naive
#    `r.content[0].text` returns a partial answer with no error raised.
show("2. max_tokens", tracked_create(
    model=HAIKU,
    max_tokens=5,
    messages=[{"role": "user", "content": "Explain how a refrigerator works."}],
))

# 3. stop_sequence -- YOUR sentinel string appeared. Note stop_sequence is now
#    populated with WHICH one matched, and the sentinel is NOT in the text.
show("3. stop_sequence", tracked_create(
    model=HAIKU,
    max_tokens=200,
    stop_sequences=["END"],
    messages=[{"role": "user", "content":
               "Count from 1 to 10, one number per line. "
               "Then write END on its own line, then write a poem."}],
))

# --- Full field dump -------------------------------------------------------
r = tracked_create(
    model=HAIKU,
    max_tokens=50,
    system="Be terse.",
    messages=[{"role": "user", "content": "What is the capital of Peru?"}],
)

print(f"\n{'=' * 62}\nFULL RESPONSE OBJECT\n{'=' * 62}")
print(json.dumps(r.model_dump(), indent=2, default=str))

print(f"\n{'=' * 62}\nUSAGE ONLY\n{'=' * 62}")
print(json.dumps(r.usage.model_dump(), indent=2, default=str))