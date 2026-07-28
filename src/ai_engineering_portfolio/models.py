# models.py
HAIKU  = "claude-haiku-4-5-20251001"   # pin dated IDs; bare aliases can move under you
SONNET = "claude-sonnet-5"
OPUS   = "claude-opus-5"

PRICES = {                  # (input, output) $ per million tokens
    HAIKU:  (1.00,  5.00),
    SONNET: (2.00, 10.00),  # intro rate — rises to (3.00, 15.00) on Sep 1, 2026
    OPUS:   (5.00, 25.00),
}

DEFAULT_MODEL = HAIKU       # everything starts on Haiku; promote deliberately
