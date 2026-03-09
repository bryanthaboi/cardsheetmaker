from PIL import Image

def colorize_icon(img: Image.Image, color: tuple) -> Image.Image:
    """Tint an RGBA icon to `color`, preserving alpha."""
    img = img.convert("RGBA")
    alpha = img.split()[3]
    colored = Image.new("RGBA", img.size, color + (255,))
    colored.putalpha(alpha)
    return colored

if __name__ == "__main__":
    # Define the suits with their colors
    suits = [
        ("skulls", "icons/skull.png", (255, 255, 255)),     # White
        ("bananas", "icons/banana.png", (255, 255, 0)),     # Yellow
        ("money", "icons/money.png", (0, 179, 0)),          # Green
        ("crowns", "icons/crown.png", (255, 180, 0)),       # Gold
        ("hearts", "icons/heart.png", (255, 128, 128)),     # Light red
        ("diamonds", "icons/diamond.png", (100, 149, 237)), # Light blue
        ("clubs", "icons/club.png", (180, 120, 230)),       # Light purple
        ("spades", "icons/spade.png", (192, 192, 192)),     # Light grey
    ]
    
    # Process each suit icon
    for name, path, color in suits:
        try:
            # Load the original icon
            icon = Image.open(path).convert("RGBA")
            
            # Colorize it
            colored_icon = colorize_icon(icon, color)
            
            # Save with the suit name
            output_path = f"{name}_colored.png"
            colored_icon.save(output_path)
            print(f"✔️  Saved: {output_path}")
            
        except FileNotFoundError:
            print(f"❌ Could not find: {path}")
    
    # Also colorize face cards if they exist
    face_cards = ["jack", "queen", "king"]
    for face in face_cards:
        try:
            icon = Image.open(f"icons/{face}.png").convert("RGBA")
            # Face cards stay in their original colors (no colorization)
            # Just copy them to output
            output_path = f"{face}_original.png"
            icon.save(output_path)
            print(f"✔️  Saved: {output_path}")
        except FileNotFoundError:
            print(f"ℹ️  No {face}.png found (optional)")