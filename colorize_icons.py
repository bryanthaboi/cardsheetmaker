"""Shared suit tinting and standalone `{name}_colored.png` export."""

from PIL import Image

from output_paths import SUITS_DIR, ensure_suits_dir
from suits_loader import load_suits


def colorize_icon(img: Image.Image, color: tuple) -> Image.Image:
    """Tint an RGBA icon to `color`, preserving alpha."""
    img = img.convert("RGBA")
    alpha = img.split()[3]
    colored = Image.new("RGBA", img.size, color + (255,))
    colored.putalpha(alpha)
    return colored


def export_colored_icons(suits=None):
    """Write `output/suits/{name}_colored.png` per suit and optional face copies there."""
    ensure_suits_dir()
    suits = suits if suits is not None else load_suits()

    for name, path, color in suits:
        try:
            icon = Image.open(path).convert("RGBA")
            colored_icon = colorize_icon(icon, color)
            output_path = SUITS_DIR / f"{name}_colored.png"
            colored_icon.save(output_path)
            print(f"✔️  Saved: {output_path}")
        except FileNotFoundError:
            print(f"❌ Could not find: {path}")

    for face in ("jack", "queen", "king"):
        try:
            icon = Image.open(f"icons/{face}.png").convert("RGBA")
            output_path = SUITS_DIR / f"{face}_original.png"
            icon.save(output_path)
            print(f"✔️  Saved: {output_path}")
        except FileNotFoundError:
            print(f"ℹ️  No {face}.png found (optional)")


if __name__ == "__main__":
    export_colored_icons()
