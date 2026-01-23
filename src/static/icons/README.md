# App Icons

## How to Generate Icons

You need to create app icons in the following sizes:
- 72x72px (icon-72x72.png)
- 96x96px (icon-96x96.png)
- 128x128px (icon-128x128.png)
- 144x144px (icon-144x144.png)
- 152x152px (icon-152x152.png)
- 192x192px (icon-192x192.png)
- 384x384px (icon-384x384.png)
- 512x512px (icon-512x512.png)

## Quick Generation Methods:

### Option 1: Use an Online Tool
1. Go to https://www.pwabuilder.com/imageGenerator
2. Upload your logo/icon (at least 512x512px)
3. Download the generated icons
4. Place them in this directory

### Option 2: Use ImageMagick (Command Line)
```bash
# Install ImageMagick first:
# macOS: brew install imagemagick
# Ubuntu: sudo apt-get install imagemagick

# Generate from a source image (replace source.png with your image)
convert source.png -resize 72x72 icon-72x72.png
convert source.png -resize 96x96 icon-96x96.png
convert source.png -resize 128x128 icon-128x128.png
convert source.png -resize 144x144 icon-144x144.png
convert source.png -resize 152x152 icon-152x152.png
convert source.png -resize 192x192 icon-192x192.png
convert source.png -resize 384x384 icon-384x384.png
convert source.png -resize 512x512 icon-512x512.png
```

### Option 3: Use Pillow (Python)
Run the `generate_icons.py` script in the parent directory:
```bash
python generate_placeholder_icons.py
```

## Design Recommendations:
- Use indigo/blue color scheme to match the app
- Include a double reed or music note symbol
- Keep it simple and recognizable at small sizes
- Use a square canvas (1:1 aspect ratio)
- Avoid text at small sizes

## Favicon
Also create a favicon.ico (16x16, 32x32) from your icon and place it in the static root.
