import argparse

from PIL import Image, ImageDraw, ImageFont

from colorize_icons import colorize_icon, export_colored_icons
from output_paths import SHEETS_DIR, ensure_sheets_dir
from suits_loader import load_suits

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
CARD_WIDTH, CARD_HEIGHT = 118, 162   # each card cell size
PADDING = 2                          # pixels around each cell
GAP     = 10                          # pixels between number and icon
ICON_SCALE = 0.12                    # max side of center pip (fraction of card width); aspect preserved
ICON_SCALE_OTHER = 0.15            # max side of corner icons (fraction of card width); aspect preserved (~same budget as center pips)
FONT_SCALE = 0.2                    # font size as fraction of card height
# ------------------------------------------------------------

# normalized pip positions (fractions of card width/height)
POS = {
    'tl': (0.35, 0.30), 'tc': (0.50, 0.30), 'tr': (0.65, 0.30),
    'ml': (0.35, 0.50), 'c' : (0.50, 0.50), 'mr': (0.65, 0.50),
    'bl': (0.35, 0.70), 'bc': (0.50, 0.70), 'br': (0.65, 0.70),
    'l2': (0.35, 0.40), 'l4': (0.35, 0.60),
    'r2': (0.65, 0.40), 'r4': (0.65, 0.60),
}
POS.update({
    'l1': POS['tl'], 'l3': POS['ml'], 'l5': POS['bl'],
    'r1': POS['tr'], 'r3': POS['mr'], 'r5': POS['br'],
})

# pip patterns for cards 1–10
PIP_MAP = {
     1: ['c'],
     2: ['tc','bc'],
     3: ['tc','c','bc'],
     4: ['tl','tr','bl','br'],
     5: ['tl','tr','c','bl','br'],
     6: ['tl','tr','ml','mr','bl','br'],
     7: ['tl','tr','ml','mr','bl','br','c'],
     8: ['tl','tr','ml','mr','bl','br','tc','bc'],
     9: ['tl','tr','ml','mr','bl','br','tc','bc','c'],
    10: ['l1','l2','l3','l4','l5','r1','r2','r3','r4','r5'],
}


def _resize_nearest_max_side(img: Image.Image, max_side: int) -> Image.Image:
    """Fit image inside max_side×max_side, preserving aspect ratio (NEAREST)."""
    w, h = img.size
    if w <= 0 or h <= 0 or max_side <= 0:
        return img
    scale = min(max_side / w, max_side / h)
    nw = max(1, int(round(w * scale)))
    nh = max(1, int(round(h * scale)))
    return img.resize((nw, nh), Image.NEAREST)


def generate_sprite_sheet(icon_path: str, color: tuple, output_path: str, font_path: str = None):
    cols = 13
    sheet_w = cols * CARD_WIDTH + (cols + 1) * PADDING
    sheet_h = CARD_HEIGHT + 2 * PADDING

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0,0,0,0))
    draw  = ImageDraw.Draw(sheet)

    # load, resize (aspect-preserving), tint icons
    base_icon = Image.open(icon_path).convert("RGBA")
    pip_max = int(CARD_WIDTH * ICON_SCALE)
    corner_max = int(CARD_WIDTH * ICON_SCALE_OTHER)
    icon = _resize_nearest_max_side(base_icon, pip_max)
    icon2 = _resize_nearest_max_side(base_icon, corner_max)
    icon = colorize_icon(icon, color)
    icon2 = colorize_icon(icon2, color)
    icon_rot = icon.rotate(180, Image.NEAREST)
    icon_rot2 = icon2.rotate(180, Image.NEAREST)
    iw, ih = icon.size
    
    # Load face card icons
    face_card_icons = {}
    face_card_size = 0.5  # 50% of card width
    for face in ['jack', 'queen', 'king']:
        try:
            face_img = Image.open(f"icons/{face}.png").convert("RGBA")
            face_size = int(CARD_WIDTH * face_card_size)
            face_img = face_img.resize((face_size, int(face_size * face_img.height / face_img.width)), Image.NEAREST)
            face_card_icons[face] = colorize_icon(face_img, color)
        except FileNotFoundError:
            print(f"Warning: Could not find {face}.png in icons folder")

    # load font
    if font_path:
        fs = int(CARD_HEIGHT * FONT_SCALE)
        font = ImageFont.truetype(font_path, fs)
    else:
        font = ImageFont.load_default()

    for i in range(cols):
        x0 = PADDING + i * (CARD_WIDTH + PADDING)
        y0 = PADDING
        val = i + 1

        # corner label
        if val <= 10:
            label = str(val)
        elif val == 11:
            label = 'J'
        elif val == 12:
            label = 'Q'
        else:
            label = 'K'

        # measure label
        bbox = draw.textbbox((0,0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # --- TOP-LEFT corner ---
        tx = x0 + PADDING
        ty = y0 + PADDING
        draw.text((tx, ty), label, font=font, fill=color)
        sheet.paste(icon2, (tx, ty + text_h + GAP), icon2)

        # --- BOTTOM-RIGHT corner (rotated) ---
        # textbbox is wider than visible pixels for some fonts; use getbbox() tight crop so the
        # glyph's right edge matches the bitmap edge (same idea as top-left flush to inner_r).
        padding = max(text_w, text_h) // 4
        tw = text_w + padding + 8
        th = text_h + padding + 8
        _tmp = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        _td = ImageDraw.Draw(_tmp)
        _td.text((tw, th), label, font=font, fill=color, anchor="rb")
        _gb = _tmp.getbbox()
        if not _gb:
            _gb = (0, 0, tw, th)
        _tight = _tmp.crop(_gb)
        lbl_w = padding + _tight.width
        lbl_h = padding + _tight.height
        lbl_img = Image.new("RGBA", (lbl_w, lbl_h), (0, 0, 0, 0))
        lbl_img.paste(_tight, (padding, padding))

        rot_lbl = lbl_img.rotate(180, expand=False)
        # rotate(180) leaves transparent slack on the sheet-ward sides of the fixed canvas;
        # crop so paste uses tight ink and the rank actually reaches inner_r / inner_b.
        _rb = rot_lbl.getbbox()
        if _rb:
            rot_lbl = rot_lbl.crop(_rb)

        inner_r = x0 + CARD_WIDTH - PADDING
        inner_b = y0 + CARD_HEIGHT - PADDING
        bx = inner_r - rot_lbl.width
        by = inner_b - rot_lbl.height

        sheet.paste(rot_lbl, (bx, by), rot_lbl)

        # Icon above rank, both flush to inner right (stays inside card cell)
        icon_y_offset = GAP + icon_rot2.height
        icon_x = inner_r - icon_rot2.width
        sheet.paste(icon_rot2, (icon_x, by - icon_y_offset), icon_rot2)

        # --- CENTER PIPS for 1–10 or FACE CARDS for J/Q/K ---
        if 1 <= val <= 10:
            spots = PIP_MAP[val]
            # determine bottom half to flip
            sorted_spots = sorted(spots, key=lambda s: POS[s][1])
            flip_count = len(sorted_spots) // 2
            bottom_set = set(sorted_spots[-flip_count:])
            for spot in spots:
                fx, fy = POS[spot]
                px = int(x0 + fx * CARD_WIDTH - iw / 2)
                py = int(y0 + fy * CARD_HEIGHT - ih / 2)
                use_icon = icon_rot if spot in bottom_set else icon
                sheet.paste(use_icon, (px, py), use_icon)
        # For face cards (J/Q/K), place the corresponding image in the center
        elif val == 11 and 'jack' in face_card_icons:
            face_img = face_card_icons['jack']
            # Center the face card image
            fx = x0 + (CARD_WIDTH - face_img.width) // 2
            fy = y0 + (CARD_HEIGHT - face_img.height) // 2
            sheet.paste(face_img, (fx, fy), face_img)
        elif val == 12 and 'queen' in face_card_icons:
            face_img = face_card_icons['queen']
            # Center the face card image
            fx = x0 + (CARD_WIDTH - face_img.width) // 2
            fy = y0 + (CARD_HEIGHT - face_img.height) // 2
            sheet.paste(face_img, (fx, fy), face_img)
        elif val == 13 and 'king' in face_card_icons:
            face_img = face_card_icons['king']
            # Center the face card image
            fx = x0 + (CARD_WIDTH - face_img.width) // 2
            fy = y0 + (CARD_HEIGHT - face_img.height) // 2
            sheet.paste(face_img, (fx, fy), face_img)

    sheet.save(output_path)
    print(f"✔️  Saved: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build card sheets under output/sheets and colored icons under output/suits (default: both).",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--icons-only",
        action="store_true",
        help="Only write output/suits/* (same idea as python colorize_icons.py).",
    )
    mode.add_argument(
        "--sheets-only",
        action="store_true",
        help="Only write output/sheets/*_sheet.png.",
    )
    args = parser.parse_args()

    if args.icons_only:
        export_colored_icons()
    elif args.sheets_only:
        ensure_sheets_dir()
        for name, path, col in load_suits():
            generate_sprite_sheet(
                icon_path=path,
                color=col,
                output_path=str(SHEETS_DIR / f"{name}_sheet.png"),
                font_path="m6x11plus.ttf",
            )
    else:
        export_colored_icons()
        ensure_sheets_dir()
        for name, path, col in load_suits():
            generate_sprite_sheet(
                icon_path=path,
                color=col,
                output_path=str(SHEETS_DIR / f"{name}_sheet.png"),
                font_path="m6x11plus.ttf",
            )