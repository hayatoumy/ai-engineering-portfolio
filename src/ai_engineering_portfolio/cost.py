# cost.py
import os 
import csv, datetime, threading
import anthropic
from ai_engineering_portfolio.models import PRICES

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from env
_lock = threading.Lock()
last_call_cost = 0.0

new_file = not os.path.exists("spend.csv")
with _lock, open("spend.csv", "a", newline="") as f:
    w = csv.writer(f)
    if new_file:
        w.writerow(["ts","model","in_tok","cache_read","out_tok","cost"])
    w.writerow([...])

def tracked_create(**kwargs):
    """Drop-in replacement for client.messages.create that logs spend."""
    global last_call_cost
    model = kwargs["model"]
    resp = client.messages.create(**kwargs)
    u = resp.usage
    p_in, p_out = PRICES[model]
    cost = (
        u.input_tokens / 1e6 * p_in
        + getattr(u, "cache_creation_input_tokens", 0) / 1e6 * p_in * 1.25
        + getattr(u, "cache_read_input_tokens", 0)     / 1e6 * p_in * 0.10
        + u.output_tokens / 1e6 * p_out
    )
    last_call_cost = cost
    with _lock, open("spend.csv", "a", newline="") as f:
        csv.writer(f).writerow([
            datetime.datetime.now().isoformat(), model,
            u.input_tokens,
            getattr(u, "cache_read_input_tokens", 0),
            u.output_tokens, round(cost, 6),
        ])
    return resp


"""
Key change in BudgetGuard: the cost is PASSED IN, not read from a module global. The old
version worked only because BudgetGuard happened to live in the same file as
`last_call_cost`. That is an invisible dependency: move the class to another
module and it silently reads a stale 0.0 forever, with no error.
"""

class BudgetOverrun(RuntimeError):
    """Raised when a loop exceeds its step or spend cap.

    A dedicated exception type so callers can catch THIS without also
    swallowing unrelated RuntimeErrors from the API client.
    """


class BudgetGuard:
    """Kill-switch for agent loops — caps steps and spend.

    Usage (explicit, preferred):

        from cost import tracked_create, BudgetGuard
        import cost

        guard = BudgetGuard(max_steps=15, max_spend=0.50)
        while not done:
            guard.precheck(estimated=0.05)     # optional: stop BEFORE spending
            resp = tracked_create(...)
            guard.record(cost.last_call_cost)  # explicit. no hidden globals.

    Raises BudgetOverrun on breach. Let it propagate — the whole point is to
    halt the loop, so do not wrap `record()` in a bare `except`.
    """

    def __init__(self, max_steps: int = 15, max_spend: float = 0.50):
        if max_steps < 1 or max_spend <= 0:
            raise ValueError("max_steps must be >= 1 and max_spend > 0")
        self.max_steps = max_steps
        self.max_spend = max_spend
        self.steps = 0
        self.spent = 0.0
        self._lock = threading.Lock()

    def record(self, cost_usd: float) -> None:
        """Register one completed call. Raises BudgetOverrun if a cap is breached.

        Pass the cost explicitly. `cost.last_call_cost` is fine as the source in
        a sequential loop, but under concurrency it is a shared global that
        another thread may have already overwritten — so read it once, right
        after your call, and hand the value to this method.
        """
        if cost_usd < 0:
            raise ValueError(f"negative cost: {cost_usd}")

        with self._lock:
            self.steps += 1
            self.spent += cost_usd
            steps, spent = self.steps, self.spent

        # Raise outside the lock. NOT because the exception would leak the lock
        # -- `with` calls __exit__ on exception propagation, so it releases
        # either way. Two lesser reasons: (1) f-string formatting is real work
        # and shouldn't happen while holding a lock, (2) `steps`/`spent` are a
        # consistent snapshot, so the number in the message is the one that
        # actually breached the cap rather than whatever another thread drifted
        # it to. Hygiene, not correctness.
        if steps > self.max_steps:
            raise BudgetOverrun(
                f"step limit hit: {steps} > {self.max_steps} "
                f"(spent ${spent:.4f})"
            )
        if spent > self.max_spend:
            raise BudgetOverrun(
                f"budget exceeded: ${spent:.4f} > ${self.max_spend:.2f} "
                f"at step {steps}"
            )

    def precheck(self, estimated: float = 0.0) -> None:
        """Raise BEFORE making a call that would breach the cap.

        `record()` is reactive: you have already spent the money by the time it
        fires, so you always overshoot by one call. At Haiku prices that is
        noise. With a large Opus context it is not. Estimate the next call with
        client.messages.count_tokens (free) and gate on it.
        """
        with self._lock:
            steps, spent = self.steps, self.spent

        if steps + 1 > self.max_steps:
            raise BudgetOverrun(f"next call would exceed step limit {self.max_steps}")
        if spent + estimated > self.max_spend:
            raise BudgetOverrun(
                f"next call (~${estimated:.4f}) would exceed budget: "
                f"${spent:.4f} + ${estimated:.4f} > ${self.max_spend:.2f}"
            )

    @property
    def remaining(self) -> float:
        """Dollars left before the cap. Useful for logging and for deciding
        whether to escalate a call to a more expensive model."""
        with self._lock:
            return max(0.0, self.max_spend - self.spent)

    def __repr__(self) -> str:
        return (f"BudgetGuard(steps={self.steps}/{self.max_steps}, "
                f"spent=${self.spent:.4f}/${self.max_spend:.2f})")
