"""Load suit name / icon path / RGB from JSON, with optional env override."""

from __future__ import annotations

import json
import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent / ".env"
_DEFAULT_JSON = Path(__file__).resolve().parent / "suits.json"
_ENV_SUITS = "CARDSHEET_SUITS"
_ENV_JSON_PATH = "CARDSHEET_SUITS_JSON"


def _load_dotenv_file(path: Path) -> None:
    """Set missing os.environ keys from a simple KEY=VALUE .env file (no deps)."""
    if not path.is_file():
        return
    with path.open(encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            if key and key not in os.environ:
                os.environ[key] = val


def _parse_suit_entry(obj: dict) -> tuple[str, str, tuple[int, int, int]]:
    name = obj.get("name")
    path = obj.get("path")
    color = obj.get("color")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Each suit needs a non-empty string 'name'")
    if not isinstance(path, str) or not path.strip():
        raise ValueError(f"Suit {name!r} needs a string 'path'")
    if not isinstance(color, list) or len(color) != 3:
        raise ValueError(f"Suit {name!r} needs 'color' as [r, g, b]")
    try:
        r, g, b = (int(color[0]), int(color[1]), int(color[2]))
    except (TypeError, ValueError, IndexError) as e:
        raise ValueError(f"Suit {name!r} color values must be integers") from e
    rgb = (r, g, b)
    for c in rgb:
        if not 0 <= c <= 255:
            raise ValueError(f"Suit {name!r} color components must be 0–255")
    return name.strip(), path.strip(), rgb


def _normalize_suits(data: list) -> list[tuple[str, str, tuple[int, int, int]]]:
    if not isinstance(data, list) or not data:
        raise ValueError("Suits data must be a non-empty JSON array")
    out = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each suit must be a JSON object with name, path, color")
        out.append(_parse_suit_entry(item))
    return out


def load_suits() -> list[tuple[str, str, tuple[int, int, int]]]:
    """
    Suit list source (first match wins):
    1. CARDSHEET_SUITS — JSON array string in the environment (after optional .env load).
    2. JSON file — path from CARDSHEET_SUITS_JSON, else suits.json next to this module.
    """
    _load_dotenv_file(_ENV_PATH)

    raw = os.environ.get(_ENV_SUITS)
    if raw is not None and raw.strip():
        data = json.loads(raw)
        return _normalize_suits(data)

    json_path = os.environ.get(_ENV_JSON_PATH, "").strip()
    path = Path(json_path) if json_path else _DEFAULT_JSON
    if not path.is_file():
        raise FileNotFoundError(
            f"Missing suits config: {path}. "
            f"Add suits.json, set {_ENV_JSON_PATH}, or set {_ENV_SUITS} to a JSON array."
        )
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return _normalize_suits(data)
