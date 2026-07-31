"""
Day 1 — Analysis of the temperature experiment.

    uv run python analyze.py

Reads temp_experiment.csv and answers the four pre-registered questions.
"""

from __future__ import annotations
import itertools
import pandas as pd
from ai_engineering_portfolio.paths import TEMP_EXPERIMENT_CSV


def jaccard(a: str, b: str) -> float:
    """Token-set overlap. Crude, but zero dependencies and good enough to rank
    dispersion across conditions. You are comparing conditions to each other,
    not reporting an absolute similarity, so a crude metric is fine here."""
    sa, sb = set(a.split()), set(b.split())
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def mean_pairwise_similarity(texts: list[str]) -> float:
    pairs = list(itertools.combinations(texts, 2))
    if not pairs:
        return float("nan")
    return sum(jaccard(a, b) for a, b in pairs) / len(pairs)


def main() -> None:
    df = pd.read_csv(TEMP_EXPERIMENT_CSV)

    # --- Q1 + Q3: dispersion -------------------------------------------------
    disp = (
        df.groupby(["task", "temperature"])
        .agg(
            n=("normalized", "size"),
            distinct=("normalized", "nunique"),
            modal_share=("normalized", lambda s: s.value_counts().iloc[0] / len(s)),
            mean_similarity=("normalized", lambda s: mean_pairwise_similarity(list(s))),
        )
        .reset_index()
    )
    disp["distinct_ratio"] = disp.distinct / disp.n

    print("=== DISPERSION ===")
    print(disp.to_string(index=False))

    # --- Q2: accuracy (closed task only) -------------------------------------
    acc = (
        df[df.task == "closed"]
        .groupby("temperature")
        .correct.agg(["mean", "sum", "size"])
        .rename(columns={"mean": "accuracy", "sum": "n_correct", "size": "n"})
    )
    print("\n=== ACCURACY (closed task) ===")
    print(acc.to_string())

    # --- Q4: does length move with temperature? ------------------------------
    length = (
        df.groupby(["task", "temperature"])
        .output_tokens.agg(["mean", "std", "min", "max"])
    )
    print("\n=== OUTPUT LENGTH ===")
    print(length.to_string())

    # --- Response object fields present in the corpus ------------------------
    print("\n=== STOP REASONS OBSERVED ===")
    print(df.stop_reason.value_counts().to_string())

    print("\n=== COST ===")
    print(f"total: ${df.cost_usd.sum():.5f} over {len(df)} calls")
    print(f"mean per call: ${df.cost_usd.mean():.7f}")
    print(f"\ninput tokens:  {df.input_tokens.sum():,}")
    print(f"output tokens: {df.output_tokens.sum():,}")

    # --- The thing you should actually stare at ------------------------------
    print("\n=== DISTINCT OUTPUTS AT TEMPERATURE 0.0 (closed task) ===")
    t0 = df[(df.temperature == 0.0) & (df.task == "closed")]
    for text, count in t0.normalized.value_counts().items():
        print(f"  {count:>3}x  {text!r}")


if __name__ == "__main__":
    main()