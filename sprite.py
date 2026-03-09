from PIL import Image, ImageDraw, ImageFont

# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------
CARD_WIDTH, CARD_HEIGHT = 118, 162   # each card cell size
PADDING = 2                          # pixels around each cell
GAP     = 6                          # pixels between number and icon
ICON_SCALE = 0.15                    # icon size as fraction of card width
ICON_SCALE_OTHER = 0.10              # icon size as fraction of card width for other icons
FONT_SCALE = 0.15                    # font size as fraction of card height
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

def colorize_icon(img: Image.Image, color: tuple) -> Image.Image:
    """Tint an RGBA icon to `color`, preserving alpha."""
    img = img.convert("RGBA")
    alpha = img.split()[3]
    colored = Image.new("RGBA", img.size, color + (255,))
    colored.putalpha(alpha)
    return colored

def generate_sprite_sheet(icon_path: str, color: tuple, output_path: str, font_path: str = None):
    cols = 13
    sheet_w = cols * CARD_WIDTH + (cols + 1) * PADDING
    sheet_h = CARD_HEIGHT + 2 * PADDING

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0,0,0,0))
    draw  = ImageDraw.Draw(sheet)

    # load, resize, tint icons
    base_icon = Image.open(icon_path).convert("RGBA")
    iw = int(CARD_WIDTH * ICON_SCALE)
    iw2 = int(CARD_WIDTH * ICON_SCALE_OTHER)
    ih = iw
    icon = base_icon.resize((iw, ih), Image.NEAREST)
    icon2 = base_icon.resize((iw2, ih), Image.NEAREST)
    icon = colorize_icon(icon, color)
    icon2 = colorize_icon(icon2, color)
    icon_rot = icon.rotate(180, Image.NEAREST)
    icon_rot2 = icon2.rotate(180, Image.NEAREST)
    
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
        # Create a new image with padding to account for rotation
        # Add padding around the text to prevent clipping
        padding = max(text_w, text_h) // 4  # Add some padding to prevent clipping
        lbl_img = Image.new("RGBA", (text_w + padding*2, text_h + padding*2), (0,0,0,0))
        ld = ImageDraw.Draw(lbl_img)
        # Draw text centered in the padded image
        ld.text((padding, padding), label, font=font, fill=color)
        
        # Rotate the image
        rot_lbl = lbl_img.rotate(180, expand=False)
        
        # Calculate position for bottom right corner
        bx = x0 + CARD_WIDTH - PADDING - text_w - padding
        by = y0 + CARD_HEIGHT - PADDING - text_h - padding
        
        # Paste the rotated text
        sheet.paste(rot_lbl, (bx, by), rot_lbl)
        
        # Rotated icon above label
        icon_y_offset = GAP + ih
        sheet.paste(icon_rot2, (bx + padding, by - icon_y_offset), icon_rot2)

        # --- CENTER PIPS for 1–10 or FACE CARDS for J/Q/K ---
        if 1 <= val <= 10:
            spots = PIP_MAP[val]
            # determine bottom half to flip
            sorted_spots = sorted(spots, key=lambda s: POS[s][1])
            flip_count = len(sorted_spots) // 2
            bottom_set = set(sorted_spots[-flip_count:])
            for spot in spots:
                fx, fy = POS[spot]
                px = int(x0 + fx * CARD_WIDTH  - iw/2)
                py = int(y0 + fy * CARD_HEIGHT - ih/2)
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
    suits = [
    ("skulls", "icons/skull.png", (255, 255, 255)),     # White
    ("bananas", "icons/banana.png", (255, 255, 0)),     # Yellow (1.0, 1.0, 0.0)
    ("money", "icons/money.png", (0, 179, 0)),          # Green (0.0, 0.7, 0.0)
    ("crowns", "icons/crown.png", (255, 180, 0)),       # Gold (orange-gold to distinguish from yellow)
    ("hearts", "icons/heart.png", (255, 128, 128)),     # Light red
    ("diamonds", "icons/diamond.png", (100, 149, 237)), # Light blue
    ("clubs", "icons/club.png", (180, 120, 230)),       # Light purple
    ("spades", "icons/spade.png", (192, 192, 192)),     # Light grey
    ]

    for name, path, col in suits:
        generate_sprite_sheet(
            icon_path=path,
            color=col,
            output_path=f"{name}_sheet.png",
            font_path="m6x11plus.ttf"
        )