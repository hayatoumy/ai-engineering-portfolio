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

# Loop kill-switch -- call this into every agent loop you ever write
class BudgetGuard:
    """Kill-switch for agent loops — caps steps and spend.

    To use in every loop: 
    guard = BudgetGuard()
    while not done:
        resp = tracked_create(...)
        guard.check()
    """
    def __init__(self, max_steps=15, max_spend=0.50):
        self.max_steps, self.max_spend = max_steps, max_spend
        self.steps, self.spent = 0, 0.0

    def check(self):
        self.steps += 1
        self.spent += last_call_cost
        if self.steps > self.max_steps:
            raise RuntimeError(f"step limit hit: {self.steps}")
        if self.spent > self.max_spend:
            raise RuntimeError(f"budget exceeded: ${self.spent:.3f}")
