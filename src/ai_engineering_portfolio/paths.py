# paths.py — single source of truth for on-disk data file locations.
# Every path is anchored to this file's location, so it is identical no
# matter what directory you run from. Never hardcode a bare filename again.
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SPEND_CSV           = REPO_ROOT / "spend.csv"
TEMP_EXPERIMENT_CSV = REPO_ROOT / "experiments" / "temp_experiment.csv"
