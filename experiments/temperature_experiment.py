"""
Day 1 — Temperature experiment.

Runs a 2 (task) x 3 (temperature) x 20 (replicate) factorial design against
Haiku 4.5 and writes one row per call to temp_experiment.csv.

Usage:
    uv run python temperature_experiment.py --estimate   # cost estimate, no calls
    uv run python temperature_experiment.py              # run for real
"""

from __future__ import annotations

import argparse
import csv
import itertools
import random
import re
import sys
import time
from dataclasses import dataclass, asdict
import anthropic
from ai_engineering_portfolio.paths import TEMP_EXPERIMENT_CSV

# Match your Day 0 layout. If you get ImportError, you're running from the wrong
# directory -- cd into src/ai_engineering_portfolio/ or adjust these imports.
# NOTE: `import cost` -- NOT `from cost import last_call_cost`.
# `from X import name` copies the value at import time. When cost.py later
# rebinds its module-level `last_call_cost`, your copy does not update, and
# every cost you read is the initial 0.0. See Day_1.md, "The zero-cost bug".
import ai_engineering_portfolio.cost as cost
from ai_engineering_portfolio.cost import tracked_create
from ai_engineering_portfolio.models import HAIKU, PRICES

# --------------------------------------------------------------------------
# Experiment configuration
# --------------------------------------------------------------------------

MODEL = HAIKU
MAX_TOKENS = 100          # generous: must NOT truncate, or it confounds length
N_REPLICATES = 20
TEMPERATURES = [0.0, 0.5, 1.0]
SEED = 0                  # seeds run ORDER only. It does not seed the model.
BUDGET_USD = 0.25         # hard stop; this experiment should cost ~2 cents

OUTFILE = TEMP_EXPERIMENT_CSV


# --- Task A: closed. One correct answer. Scoreable with ==. -----------------

CLOSED_SYSTEM = (
    "You extract a single value from text. "
    "Respond with only the value. No units, no currency symbols, no explanation."
)

CLOSED_PROMPT = """Invoice #4471
Line 1: Consulting services .......  980.00
Line 2: Travel reimbursement .....  216.50
Line 3: Software license .........   88.00
Subtotal .........................  1284.50
Tax (0%) .........................      0.00
Total ............................  1284.50

What is the total?"""

CLOSED_GROUND_TRUTH = "1284.50"


# --- Task B: open. No correct answer. Generative. ---------------------------

OPEN_SYSTEM = "You write advertising copy. Respond with one sentence only."

OPEN_PROMPT = "Write a tagline for a reusable stainless steel water bottle."


TASKS = {
    "closed": (CLOSED_SYSTEM, CLOSED_PROMPT),
    "open": (OPEN_SYSTEM, OPEN_PROMPT),
}


# --------------------------------------------------------------------------
# Normalization -- DECIDED BEFORE LOOKING AT RESULTS. Do not tune this after.
# --------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Canonical form used for BOTH the distinct-count and the accuracy score.

    Rules, fixed in advance:
      1. strip leading/trailing whitespace
      2. lowercase
      3. collapse runs of internal whitespace to a single space
      4. strip trailing sentence punctuation  . ! ,
      5. strip surrounding quotes

    Deliberately NOT normalized: internal punctuation, thousands separators,
    currency symbols. If the model emits "$1,284.50" that is a DIFFERENT string
    from "1284.50" and it should score as wrong -- the system prompt told it not
    to add symbols, and instruction-following is part of what we are measuring.
    """
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = t.strip('"\u201c\u201d\'')
    t = t.rstrip(".!,")
    return t


def score_closed(text: str) -> bool:
    """Exact match against ground truth, after normalization."""
    return normalize(text) == normalize(CLOSED_GROUND_TRUTH)


# --------------------------------------------------------------------------
# Cost estimation -- run this BEFORE you spend anything
# --------------------------------------------------------------------------

def estimate_cost() -> None:
    """Pre-flight estimate using the real tokenizer via the count_tokens endpoint."""
    client = anthropic.Anthropic()
    p_in, p_out = PRICES[MODEL]

    total_in = 0
    assumed_out = {"closed": 8, "open": 22}   # your guess; the run will correct you

    print(f"{'task':<8} {'input_tok':>10} {'calls':>7} {'in_total':>10}")
    for task, (sys_p, user_p) in TASKS.items():
        n_calls = len(TEMPERATURES) * N_REPLICATES
        counted = client.messages.count_tokens(
            model=MODEL,
            system=sys_p,
            messages=[{"role": "user", "content": user_p}],
        )
        total_in += counted.input_tokens * n_calls
        print(f"{task:<8} {counted.input_tokens:>10} {n_calls:>7} "
              f"{counted.input_tokens * n_calls:>10}")

    total_out = sum(
        assumed_out[t] * len(TEMPERATURES) * N_REPLICATES for t in TASKS
    )

    cost_in = total_in / 1e6 * p_in
    cost_out = total_out / 1e6 * p_out

    print(f"\ninput  {total_in:>7,} tok  x ${p_in}/MTok  = ${cost_in:.5f}")
    print(f"output {total_out:>7,} tok  x ${p_out}/MTok  = ${cost_out:.5f}")
    print(f"TOTAL                              = ${cost_in + cost_out:.5f}")
    print(f"\noutput is {total_out/(total_in+total_out):.1%} of tokens "
          f"but {cost_out/(cost_in+cost_out):.1%} of cost")


# --------------------------------------------------------------------------
# Runner
# --------------------------------------------------------------------------

@dataclass
class Row:
    task: str
    temperature: float
    replicate: int
    text: str
    normalized: str
    correct: bool | None
    input_tokens: int
    output_tokens: int
    stop_reason: str
    stop_sequence: str | None
    msg_id: str
    model: str
    cost_usd: float


def call_with_retry(**kwargs):
    """Bounded exponential backoff on 429. Never retry a 400 -- that's your bug."""
    for attempt in range(5):
        try:
            return tracked_create(**kwargs)
        except anthropic.RateLimitError:
            wait = 2 ** attempt
            print(f"  rate limited, sleeping {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("rate limited 5 times in a row; check your tier")


def run() -> None:
    # Build the full run list, then SHUFFLE it. Running all temp=0.0 calls first
    # would confound temperature with anything that drifts over time (server-side
    # load, model routing, your own network). Randomized order kills that.
    plan = list(itertools.product(TASKS.keys(), TEMPERATURES, range(N_REPLICATES)))
    random.Random(SEED).shuffle(plan)

    rows: list[Row] = []
    spent = 0.0

    for i, (task, temp, rep) in enumerate(plan, 1):
        sys_p, user_p = TASKS[task]

        r = call_with_retry(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            temperature=temp,
            system=sys_p,
            messages=[{"role": "user", "content": user_p}],
        )

        call_cost = cost.last_call_cost          # read through the module
        if i == 1 and call_cost == 0.0:
            # Fail fast. A budget guard that reads zero is not a guard at all.
            raise RuntimeError(
                "last_call_cost is 0.0 on the first call. Your cost tracking is "
                "broken and BUDGET_USD will never fire. Check cost.py."
            )
        spent += call_cost
        if spent > BUDGET_USD:
            raise RuntimeError(f"budget exceeded at call {i}: ${spent:.4f}")

        text = r.content[0].text
        rows.append(Row(
            task=task,
            temperature=temp,
            replicate=rep,
            text=text,
            normalized=normalize(text),
            correct=score_closed(text) if task == "closed" else None,
            input_tokens=r.usage.input_tokens,
            output_tokens=r.usage.output_tokens,
            stop_reason=r.stop_reason,
            stop_sequence=r.stop_sequence,
            msg_id=r.id,
            model=r.model,
            cost_usd=call_cost,
        ))

        if i % 20 == 0:
            print(f"  {i}/{len(plan)} calls, ${spent:.5f}")

    with open(OUTFILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        w.writeheader()
        for row in rows:
            w.writerow(asdict(row))

    print(f"\nwrote {len(rows)} rows to {OUTFILE}")
    print(f"actual spend: ${spent:.5f}")

    # The check that matters: did anything truncate? If so your length numbers
    # are garbage and you need to raise MAX_TOKENS and rerun.
    truncated = sum(1 for r in rows if r.stop_reason == "max_tokens")
    if truncated:
        print(f"WARNING: {truncated} responses hit max_tokens. Raise it and rerun.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true",
                    help="print a cost estimate and exit without calling")
    args = ap.parse_args()

    if args.estimate:
        estimate_cost()
    else:
        run()