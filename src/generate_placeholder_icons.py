#!/usr/bin/env python
"""
Generate placeholder app icons for ReedManage PWA
This creates simple colored icons with the app initial "R"
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
except ImportError:
    print("PIL/Pillow is required. Install it with: pip install Pillow")
    exit(1)

# Icon sizes needed for PWA
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Colors (indigo theme)
BG_COLOR = (79, 70, 229)  # Indigo-600
TEXT_COLOR = (255, 255, 255)  # White

def create_icon(size):
    """Create a simple icon with the letter R"""
    # Create image with background color
    img = Image.new('RGB', (size, size), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fallback to default
    try:
        # Try to find a system font
        font_size = int(size * 0.6)
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(size * 0.6))
        except:
            font = ImageFont.load_default()

    # Draw the letter "R" centered
    text = "R"

    # Get text bounding box for centering
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position to center text
    x = (size - text_width) / 2 - bbox[0]
    y = (size - text_height) / 2 - bbox[1]

    # Draw text
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

    return img

def main():
    """Generate all icon sizes"""
    # Create icons directory if it doesn't exist
    icons_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    print("Generating placeholder icons for ReedManage PWA...")

    for size in SIZES:
        filename = f"icon-{size}x{size}.png"
        filepath = os.path.join(icons_dir, filename)

        # Create and save icon
        icon = create_icon(size)
        icon.save(filepath, 'PNG')

        print(f"✓ Created {filename}")

    # Also create favicon
    favicon_path = os.path.join(os.path.dirname(__file__), 'static', 'favicon.ico')
    favicon = create_icon(32)
    favicon.save(favicon_path, 'ICO')
    print(f"✓ Created favicon.ico")

    print("\n✅ All icons generated successfully!")
    print("\n📝 Next steps:")
    print("1. Replace these placeholder icons with your actual app logo")
    print("2. Use https://www.pwabuilder.com/imageGenerator for professional icons")
    print("3. Or use Photoshop/Figma to design custom icons")

if __name__ == '__main__':
    main()
