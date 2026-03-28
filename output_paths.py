"""Output directories for generated assets (relative to cwd when you run the scripts)."""

from pathlib import Path

OUTPUT_ROOT = Path("output")
SHEETS_DIR = OUTPUT_ROOT / "sheets"
SUITS_DIR = OUTPUT_ROOT / "suits"


def ensure_sheets_dir() -> None:
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_suits_dir() -> None:
    SUITS_DIR.mkdir(parents=True, exist_ok=True)
