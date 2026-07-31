"""
Tests for BudgetGuard.

    uv add --dev pytest
    uv run pytest budget_guard_test.py -v

Why this file exists: a safety mechanism you have never seen fire is not a
safety mechanism. Every one of these tests asserts that the guard STOPS you.
No API calls, no cost, runs in milliseconds.
"""

import threading

import pytest

from ai_engineering_portfolio.cost import BudgetGuard, BudgetOverrun   # -> `from ai_engineering_portfolio.cost ...`


# --- the tests that matter: does it actually stop? -------------------------

def test_fires_on_spend_limit():
    guard = BudgetGuard(max_steps=100, max_spend=0.10)
    with pytest.raises(BudgetOverrun, match="budget exceeded"):
        for _ in range(100):
            guard.record(0.02)          # breaches on the 6th call
    assert guard.steps == 6
    assert guard.spent == pytest.approx(0.12)


def test_fires_on_step_limit():
    guard = BudgetGuard(max_steps=3, max_spend=100.0)
    with pytest.raises(BudgetOverrun, match="step limit"):
        for _ in range(100):
            guard.record(0.0)
    assert guard.steps == 4


def test_precheck_fires_before_spending():
    guard = BudgetGuard(max_steps=100, max_spend=0.10)
    guard.record(0.09)
    with pytest.raises(BudgetOverrun, match="would exceed budget"):
        guard.precheck(estimated=0.05)
    assert guard.spent == pytest.approx(0.09)   # nothing extra was spent


# --- the regression test for the bug that started all this -----------------

def test_zero_cost_is_detectable():
    """If cost tracking is broken and every call reports 0.0, the guard can
    never fire on spend. The step limit is the backstop -- which is exactly why
    max_steps exists alongside max_spend. Belt and braces."""
    guard = BudgetGuard(max_steps=5, max_spend=0.50)
    with pytest.raises(BudgetOverrun, match="step limit"):
        for _ in range(100):
            guard.record(0.0)           # simulates the broken-import bug


# --- the boring but necessary ones -----------------------------------------

def test_does_not_fire_under_limits():
    guard = BudgetGuard(max_steps=10, max_spend=1.00)
    for _ in range(9):
        guard.record(0.05)
    assert guard.steps == 9
    assert guard.remaining == pytest.approx(0.55)


def test_rejects_negative_cost():
    guard = BudgetGuard()
    with pytest.raises(ValueError):
        guard.record(-1.0)


def test_rejects_nonsense_config():
    with pytest.raises(ValueError):
        BudgetGuard(max_spend=0)


def test_thread_safe_accounting():
    """20 threads x 50 calls. Without the lock, `self.spent += x` is a
    read-modify-write race and the total comes out short."""
    guard = BudgetGuard(max_steps=10_000, max_spend=10_000.0)

    def worker():
        for _ in range(50):
            guard.record(0.001)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert guard.steps == 1000
    assert guard.spent == pytest.approx(1.0)