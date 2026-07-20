"""Generates high-quality QR codes and lockups for the Aleto Pintores business card.

Outputs:
1. Transparent PNG of the QR code (white modules)
2. Green background PNG of the QR code
3. Business card lockup with QR code + Instagram badge

Run: .venv/bin/python scripts/generate_qr.py
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

# Configuration
URL = "https://wa.me/34624046210?text=Hola%2C%20me%20gustar%C3%ADa%20pedir%20un%20presupuesto%20de%20pintura.&utm_source=business-card&utm_medium=qr&utm_campaign=offline"
FOREST_GREEN = (22, 56, 42, 255)       # #16382a
CHARTREUSE = (213, 215, 67, 255)       # #d5d743
PAPER_WHITE = (250, 249, 244, 255)     # #faf9f4
TRANSPARENT = (0, 0, 0, 0)

ARTIFACTS_DIR = "/Users/felipegregorio/.gemini/antigravity-cli/brain/1d1a475e-cd28-42f0-ad5a-92016d211ca6"

def generate_base_qr():
    """Generates the high-res QR code with rounded modules and eyes."""
    qr = qrcode.QRCode(
        version=None,  # Auto-fit
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,    # High resolution
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)

    # We use RoundedModuleDrawer for modules AND eyes to replicate the user's style
    img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        eye_drawer=RoundedModuleDrawer(),
    )
    return img

def create_transparent_qr(base_img):
    """Saves a version with a transparent background and white modules."""
    # Convert base image (L/RGB) to RGBA
    base_rgba = base_img.convert("RGBA")
    datas = base_rgba.getdata()

    new_data = []
    for item in datas:
        # qrcode lib StyledPilImage outputs dark pixels as black/dark-color, and light as white
        # We map dark pixels to white, and light pixels to transparent
        # Average brightness
        brightness = (item[0] + item[1] + item[2]) / 3
        if brightness < 128:
            new_data.append(PAPER_WHITE)
        else:
            new_data.append(TRANSPARENT)

    transparent_img = Image.new("RGBA", base_rgba.size)
    transparent_img.putdata(new_data)
    return transparent_img

def create_green_bg_qr(base_img):
    """Saves a version with forest green background and white modules."""
    base_rgba = base_img.convert("RGBA")
    datas = base_rgba.getdata()

    new_data = []
    for item in datas:
        brightness = (item[0] + item[1] + item[2]) / 3
        if brightness < 128:
            new_data.append(PAPER_WHITE)
        else:
            new_data.append(FOREST_GREEN)

    green_img = Image.new("RGBA", base_rgba.size)
    green_img.putdata(new_data)
    return green_img

def draw_instagram_icon(draw, x, y, size, color):
    """Draws a clean vector-like Instagram icon using PIL Draw."""
    thickness = max(2, int(size * 0.08))
    # 1. Main rounded square
    draw.rounded_rectangle(
        [x, y, x + size, y + size],
        radius=int(size * 0.28),
        outline=color,
        width=thickness
    )
    # 2. Inner circle
    center_x = x + size / 2
    center_y = y + size / 2
    r = size * 0.24
    draw.ellipse(
        [center_x - r, center_y - r, center_x + r, center_y + r],
        outline=color,
        width=thickness
    )
    # 3. Small lens dot
    dot_r = size * 0.06
    dot_x = x + size * 0.72
    dot_y = y + size * 0.28
    draw.ellipse(
        [dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r],
        fill=color
    )

def create_card_lockup(qr_white_transparent):
    """Creates the final 1000x1200 PNG lockup matching the user's mockup."""
    # 1. Base canvas
    canvas = Image.new("RGBA", (1000, 1200), FOREST_GREEN)
    
    # 2. Resize QR code to fit 700x700
    qr_resized = qr_white_transparent.resize((700, 700), Image.Resampling.LANCZOS)
    
    # Paste QR code centered horizontally
    qr_x = (1000 - 700) // 2
    qr_y = 100
    canvas.paste(qr_resized, (qr_x, qr_y), qr_resized)

    # 3. Draw Instagram badge box
    draw = ImageDraw.Draw(canvas)
    
    # Badge Box dimensions
    box_w = 420
    box_h = 90
    box_x = (1000 - box_w) // 2
    box_y = 900
    box_radius = 24
    
    # Draw gold border
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=box_radius,
        outline=CHARTREUSE,
        width=3
    )
    
    # Draw Instagram Icon inside the box
    icon_size = 46
    icon_x = box_x + 30
    icon_y = box_y + (box_h - icon_size) // 2
    draw_instagram_icon(draw, icon_x, icon_y, icon_size, CHARTREUSE)
    
    # Draw text "@aleto.pintores"
    text = "@aleto.pintores"
    # Find a system font
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "arial.ttf"
    ]
    font = None
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 36)
            break
        except IOError:
            continue
    if not font:
        font = ImageFont.load_default()
        print("Warning: Arial font not found, using default low-res font.")

    # Get text size
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    
    text_x = icon_x + icon_size + 20
    # Align text vertically in the box
    text_y = box_y + (box_h - text_h) // 2 - 4
    
    draw.text((text_x, text_y), text, fill=PAPER_WHITE, font=font)
    
    return canvas

def main():
    print("Generating base QR code...")
    base_img = generate_base_qr()
    
    print("Creating transparent version...")
    transparent_qr = create_transparent_qr(base_img)
    transparent_path = os.path.join(ARTIFACTS_DIR, "aleto_qr_transparent.png")
    transparent_qr.save(transparent_path, "PNG")
    print(f"✓ Saved transparent QR to: {transparent_path}")
    
    print("Creating green background version...")
    green_qr = create_green_bg_qr(base_img)
    green_path = os.path.join(ARTIFACTS_DIR, "aleto_qr_green_bg.png")
    green_qr.save(green_path, "PNG")
    print(f"✓ Saved green QR to: {green_path}")
    
    print("Creating final business card lockup...")
    lockup = create_card_lockup(transparent_qr)
    lockup_path = os.path.join(ARTIFACTS_DIR, "aleto_business_card_lockup.png")
    lockup.save(lockup_path, "PNG")
    print(f"✓ Saved business card lockup to: {lockup_path}")
    
    print("\nGeneration complete!")

if __name__ == "__main__":
    main()
