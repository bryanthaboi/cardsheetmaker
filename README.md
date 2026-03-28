# Card Sheet Maker

Python scripts that use [Pillow](https://python-pillow.org/) to build **playing-card-style sprite sheets** (one PNG per suit) and **tinted suit PNGs**. Suit names, paths, and RGB values come from **`suits.json`** (or environment — see below). By default **`python sprite.py`** writes **both** `output/sheets/` and `output/suits/`. **`colorize_icons.py`** exposes `colorize_icon` and `export_colored_icons`; **`suits_loader.load_suits()`** resolves the suit list.

Made by **bryanthaboi** for [**Boya Coya**](https://store.steampowered.com/app/4509030/Boya_Coya/) on Steam.

## Quick start

### Windows

```bash
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
python sprite.py
deactivate
```

Sheets only (skip `output/suits/`):

```bash
python sprite.py --sheets-only
```

Colored icons only (same output folder as below; equivalent to `python colorize_icons.py`):

```bash
python sprite.py --icons-only
```

Or run the suits export module directly:

```bash
python colorize_icons.py
```

### Mac

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install Pillow
python3 sprite.py
deactivate
```

```bash
python3 sprite.py --sheets-only
python3 sprite.py --icons-only
# or: python3 colorize_icons.py
```

If you use `requirements.txt` on Mac, you can run `pip install -r requirements.txt` instead of installing Pillow alone.

---

## Requirements

- Python 3 with Pillow installed (`pip install Pillow` or `pip install -r requirements.txt` if you maintain one).
- **`m6x11plus.ttf`** in the project root — used by `sprite.py` for corner ranks (1–10, J, Q, K).
- An **`icons/`** folder with suit glyphs and optional face art (see [Asset checklist](#asset-checklist)).
- **`suits.json`** in the project root (next to `suits_loader.py`) — default suit table unless overridden by env.

### Suit config: JSON, `.env`, and environment

**`suits_loader.load_suits()`** (used by `sprite.py` and `export_colored_icons()`):

1. Loads a project **`.env`** file if present (same folder as `suits_loader.py`). Only sets variables that are **not** already defined in the real process environment.
2. If **`CARDSHEET_SUITS`** is set and non-empty, it is parsed as a **JSON array** of objects `{ "name", "path", "color": [r,g,b] }` and used **instead of** a file.
3. Otherwise it reads **`CARDSHEET_SUITS_JSON`** if set (path to a JSON file), or defaults to **`suits.json`**.

Copy **`.env.example`** to **`.env`** to document or set overrides locally (`.env` is gitignored).

## Outputs

| Command | Typical outputs |
|--------|-----------------|
| `python3 sprite.py` (default) | **`output/sheets/{suit}_sheet.png`** — 13-card strip per suit, **and** **`output/suits/{suit}_colored.png`** (plus optional **`output/suits/{jack,queen,king}_original.png`**). |
| `python3 sprite.py --sheets-only` | **`output/sheets/{suit}_sheet.png`** only. |
| `python3 sprite.py --icons-only` or `python3 colorize_icons.py` | **`output/suits/*`** only (colored suit icons and optional face copies). |

Paths are relative to the **current working directory** when you run the script. `output/sheets` and `output/suits` are created if missing (`output_paths.py`).

---

## How it works

### `sprite.py` — card sheets

#### Configuration (top of file)

Constants control layout and scale:

- **`CARD_WIDTH` / `CARD_HEIGHT`** — pixel size of each card cell (default 118×162).
- **`PADDING`** — space around the sheet and between cells.
- **`GAP`** — space between corner rank text and the small corner icon.
- **`ICON_SCALE`** — max side of center pips (fraction of card width; aspect preserved; default ~15%).
- **`ICON_SCALE_OTHER`** — max side of **corner** suit icons (same idea; default matches center so corners stay readable after aspect-preserving resize).
- **`FONT_SCALE`** — TrueType font size relative to card height.

#### Pip layout (ranks 1–10)

- **`POS`** — normalized `(x, y)` positions on the card (0–1), named spots like `tl`, `c`, `l1`…`r5`.
- **`PIP_MAP`** — for each rank 1–10, which spots get an icon (standard playing-card pip patterns).

For each pip, the script pastes the suit icon at the mapped position. **Bottom-half pips** (by vertical sort) use a **180°-rotated** icon so orientation matches a real deck.

#### Corner decorations

For every column (rank):

1. **Top-left**: rank label (`1`–`10`, `J`, `Q`, `K`) in the suit color, then the small tinted icon below the text.
2. **Bottom-right**: label drawn on a small RGBA layer, rotated 180°, pasted so it reads correctly upside-down; the small icon sits above that label (also rotated).

#### Face cards (J, Q, K)

If `icons/jack.png`, `icons/queen.png`, and/or `icons/king.png` exist, they are loaded, resized to about **half the card width** (height scaled to preserve aspect ratio), tinted with the suit color, and **centered** on columns 11–13. Missing files print a warning and that rank shows only corners / no center art.

#### Icon tinting

Implemented in **`colorize_icons.py`**: `colorize_icon()` converts the icon to RGBA, keeps the **alpha channel**, and fills RGB with the suit color so transparent areas stay transparent. `sprite.py` imports it.

#### Main entrypoint

`python sprite.py` (default) runs **`export_colored_icons()`** then builds each sheet into **`output/sheets/{name}_sheet.png`**. **`--icons-only`** writes only **`output/suits/`**; **`--sheets-only`** writes only **`output/sheets/`**.

---

### `suits_loader.py` — suit list

- **`load_suits()`** — returns `list[tuple[name, path, (r, g, b)]]` from **`CARDSHEET_SUITS`** (JSON string) or a JSON file (**`suits.json`** by default).

---

### `colorize_icons.py` — module and standalone icons

This file is the **shared module** and can still be run as a script.

- **`colorize_icon()`** — tint helper used by `sprite.py` and `export_colored_icons()`.
- **`export_colored_icons()`** — uses **`load_suits()`** when `suits` is omitted; writes **`output/suits/{name}_colored.png`** and optional **`output/suits/{face}_original.png`** (no tint on face copies).

If an icon path is missing, it prints an error for that suit and continues.

---

### How the pieces fit

- **`sprite.py`** — full deck generator: default runs suits export + sheets; **`--icons-only`** / **`--sheets-only`** limit which outputs run. Uses **`load_suits()`**, `colorize_icon` from `colorize_icons`, and **`output_paths`** for folders.
- **`colorize_icons.py`** — tinting and colored-icon export; `python colorize_icons.py` calls `export_colored_icons()` directly.

### Asset checklist

| Path | Used by |
|------|---------|
| `suits.json` (or path in **`CARDSHEET_SUITS_JSON`**) | Default suit table: `name`, `path`, `color`. |
| `icons/<suit>.png` | Paths listed in that JSON (or in **`CARDSHEET_SUITS`**). |
| `icons/jack.png`, `queen.png`, `king.png` | `sprite.py` center art; `export_colored_icons()` optional copy-out. |
| `m6x11plus.ttf` | `sprite.py` only (`font_path` in `generate_sprite_sheet`). |

To add or change suits, edit **`suits.json`** or set **`CARDSHEET_SUITS`** / **`CARDSHEET_SUITS_JSON`**.
