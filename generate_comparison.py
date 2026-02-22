"""
Generate 10 Normal vs Pneumonia X-Ray Comparison Images
Creates annotated side-by-side comparison images for the presentation guide.
Uses synthetic grayscale images with realistic patterns.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "comparison_images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMG_SIZE = 300


def draw_text(draw, text, position, font_size=16, fill="white"):
    """Draw text at position."""
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    draw.text(position, text, fill=fill, font=font)


def create_lung_shape(draw, cx, cy, w, h, fill_color, outline_color="gray"):
    """Draw a lung-like ellipse."""
    draw.ellipse([cx - w, cy - h, cx + w, cy + h], fill=fill_color, outline=outline_color)


def generate_normal_xray(index, description):
    """Generate a synthetic normal chest X-ray."""
    img = Image.new("L", (IMG_SIZE, IMG_SIZE), 0)  # Black background
    draw = ImageDraw.Draw(img)

    # Rib cage lines (subtle white lines)
    for y_offset in range(60, 240, 25):
        draw.line([(50, y_offset), (250, y_offset)], fill=40, width=1)

    # Left lung (dark - healthy)
    create_lung_shape(draw, 105, 150, 55, 80, fill_color=15)
    # Right lung (dark - healthy)
    create_lung_shape(draw, 195, 150, 55, 80, fill_color=15)

    # Heart silhouette (center-left, medium gray)
    create_lung_shape(draw, 140, 155, 30, 35, fill_color=80)

    # Spine (bright center line)
    draw.line([(150, 50), (150, 260)], fill=100, width=4)

    # Diaphragm (sharp curved line at bottom)
    for x in range(50, 250):
        y = 230 + int(10 * np.sin((x - 50) * np.pi / 200))
        draw.point((x, y), fill=90)

    # Apply slight blur for realism
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    return img, description


def generate_pneumonia_xray(index, description, affected="right", severity="moderate"):
    """Generate a synthetic pneumonia chest X-ray."""
    img = Image.new("L", (IMG_SIZE, IMG_SIZE), 0)  # Black background
    draw = ImageDraw.Draw(img)

    # Rib cage lines
    for y_offset in range(60, 240, 25):
        draw.line([(50, y_offset), (250, y_offset)], fill=40, width=1)

    # Spine
    draw.line([(150, 50), (150, 260)], fill=100, width=4)

    if severity == "mild":
        left_fill, right_fill = 15, 60
        patch_intensity = 80
    elif severity == "moderate":
        left_fill = 15 if affected != "both" else 70
        right_fill = 90 if affected != "left" else 15
        patch_intensity = 120
    elif severity == "severe":
        left_fill, right_fill = 130, 140
        patch_intensity = 180
    else:
        left_fill, right_fill = 15, 70
        patch_intensity = 100

    # Left lung
    create_lung_shape(draw, 105, 150, 55, 80, fill_color=left_fill)
    # Right lung
    create_lung_shape(draw, 195, 150, 55, 80, fill_color=right_fill)

    # Add white patches (consolidation) for pneumonia
    rng = np.random.RandomState(index + 42)
    if affected in ("right", "both"):
        for _ in range(rng.randint(3, 7)):
            px = rng.randint(165, 225)
            py = rng.randint(110, 210)
            pr = rng.randint(8, 20)
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=patch_intensity)

    if affected in ("left", "both"):
        for _ in range(rng.randint(3, 7)):
            px = rng.randint(75, 135)
            py = rng.randint(110, 210)
            pr = rng.randint(8, 20)
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=patch_intensity)

    # Heart silhouette
    create_lung_shape(draw, 140, 155, 30, 35, fill_color=80)

    # Blurred diaphragm (less sharp than normal)
    for x in range(50, 250):
        y = 230 + int(10 * np.sin((x - 50) * np.pi / 200))
        draw.point((x, y), fill=60)

    # Apply blur
    img = img.filter(ImageFilter.GaussianBlur(radius=2.0))

    return img, description


def create_gradcam_overlay(base_img, affected="right"):
    """Create a Grad-CAM style heatmap overlay."""
    base_array = np.array(base_img).astype(np.float32)
    # Create RGB version
    rgb = np.stack([base_array, base_array, base_array], axis=-1)

    # Create heatmap
    heatmap = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.float32)

    if affected == "right":
        # Red on right lung area
        for y in range(70, 230):
            for x in range(155, 245):
                dist = np.sqrt((x - 195) ** 2 / 2500 + (y - 150) ** 2 / 6400)
                if dist < 1.0:
                    heatmap[y, x] = max(0, 1.0 - dist)
    elif affected == "left":
        for y in range(70, 230):
            for x in range(55, 145):
                dist = np.sqrt((x - 105) ** 2 / 2500 + (y - 150) ** 2 / 6400)
                if dist < 1.0:
                    heatmap[y, x] = max(0, 1.0 - dist)
    elif affected == "both":
        for y in range(70, 230):
            for x in range(55, 245):
                dist_r = np.sqrt((x - 195) ** 2 / 2500 + (y - 150) ** 2 / 6400)
                dist_l = np.sqrt((x - 105) ** 2 / 2500 + (y - 150) ** 2 / 6400)
                dist = min(dist_r, dist_l)
                if dist < 1.0:
                    heatmap[y, x] = max(0, 1.0 - dist)
    else:
        # Normal - very low blue tint
        pass

    # Apply jet-like colormap manually
    # Red channel increases with heatmap intensity
    rgb[:, :, 0] = np.clip(rgb[:, :, 0] + heatmap * 200, 0, 255)
    # Green channel for medium values
    rgb[:, :, 1] = np.clip(rgb[:, :, 1] * (1 - heatmap * 0.3), 0, 255)
    # Blue channel decreases
    rgb[:, :, 2] = np.clip(rgb[:, :, 2] * (1 - heatmap * 0.5), 0, 255)

    return Image.fromarray(rgb.astype(np.uint8))


def create_comparison_card(index, xray_img, gradcam_img, label, description, confidence, features):
    """Create a single comparison card with X-ray, heatmap, and annotations."""
    card_w, card_h = 750, 420
    card = Image.new("RGB", (card_w, card_h), (20, 20, 30))
    draw = ImageDraw.Draw(card)

    # Title bar color
    if "NORMAL" in label:
        title_color = (40, 120, 80)  # Green
        badge = "✅ NORMAL"
    else:
        title_color = (160, 50, 50)  # Red
        badge = "❌ PNEUMONIA"

    # Title bar
    draw.rectangle([0, 0, card_w, 45], fill=title_color)
    draw_text(draw, f"Image {index}: {label}", (15, 10), font_size=20, fill="white")
    draw_text(draw, f"Confidence: {confidence}%", (card_w - 200, 12), font_size=16, fill="yellow")

    # Paste X-ray
    xray_resized = xray_img.resize((180, 180))
    card.paste(xray_resized.convert("RGB") if xray_resized.mode != "RGB" else xray_resized, (20, 60))
    draw_text(draw, "Original X-Ray", (55, 245), font_size=12, fill=(180, 180, 180))

    # Paste Grad-CAM
    gradcam_resized = gradcam_img.resize((180, 180))
    card.paste(gradcam_resized, (220, 60))
    draw_text(draw, "Grad-CAM Heatmap", (245, 245), font_size=12, fill=(180, 180, 180))

    # Feature annotations (right side)
    x_text = 430
    y_text = 60
    draw_text(draw, "Analysis:", (x_text, y_text), font_size=14, fill=(100, 200, 255))
    y_text += 25

    for feat_name, feat_val in features.items():
        color = (100, 255, 100) if "✅" in feat_val else (255, 100, 100) if "❌" in feat_val else (200, 200, 200)
        draw_text(draw, f"• {feat_name}:", (x_text, y_text), font_size=11, fill=(180, 180, 180))
        draw_text(draw, f"  {feat_val}", (x_text + 10, y_text + 16), font_size=11, fill=color)
        y_text += 35

    # Description at bottom
    draw.rectangle([0, card_h - 50, card_w, card_h], fill=(30, 30, 45))
    draw_text(draw, description, (15, card_h - 38), font_size=11, fill=(200, 200, 200))

    return card


def main():
    print("=" * 60)
    print("  GENERATING 10 X-RAY COMPARISON IMAGES")
    print("=" * 60)

    # Define 10 image cases
    cases = [
        # Normal cases (5)
        {
            "index": 1, "type": "normal",
            "label": "NORMAL LUNG - Clear & Healthy",
            "desc": "Both lungs dark & clear. Ribs visible. Sharp borders. No white patches.",
            "confidence": 94, "affected": "none",
            "features": {
                "Lung Colour": "✅ Uniformly Dark (Black)",
                "White Patches": "✅ None Present",
                "Borders": "✅ Sharp & Clear",
                "Ribs Visibility": "✅ Clearly Visible",
                "Heatmap": "✅ Cool Blue (No Alert)",
            }
        },
        {
            "index": 2, "type": "normal",
            "label": "NORMAL LUNG - Symmetric",
            "desc": "Both lungs symmetric. Equal darkness on both sides. Clear diaphragm.",
            "confidence": 91, "affected": "none",
            "features": {
                "Lung Colour": "✅ Both Equally Dark",
                "Symmetry": "✅ Left = Right",
                "Borders": "✅ Sharp & Clear",
                "Costophrenic": "✅ Angles Sharp",
                "Heatmap": "✅ Cool Blue (Normal)",
            }
        },
        {
            "index": 3, "type": "normal",
            "label": "NORMAL LUNG - Transparent",
            "desc": "Lung tissue transparent. Ribs seen through lungs. Air-filled healthy tissue.",
            "confidence": 93, "affected": "none",
            "features": {
                "Lung Colour": "✅ Dark & Transparent",
                "Rib Visibility": "✅ Ribs Through Lungs",
                "Air Content": "✅ Fully Aerated",
                "Heart Size": "✅ Normal Ratio",
                "Heatmap": "✅ No Red Areas",
            }
        },
        {
            "index": 4, "type": "normal",
            "label": "NORMAL LUNG - Wide Fields",
            "desc": "Large lung fields. Fully expanded. No consolidation anywhere.",
            "confidence": 96, "affected": "none",
            "features": {
                "Lung Volume": "✅ Fully Expanded",
                "White Patches": "✅ Zero Opacity",
                "Diaphragm": "✅ Sharp Dome Shape",
                "Mediastinum": "✅ Normal Width",
                "Heatmap": "✅ All Blue/Cool",
            }
        },
        {
            "index": 5, "type": "normal",
            "label": "NORMAL LUNG - Elderly (Age Lines)",
            "desc": "Slight gray lines (age-related). But NO white patches. Still NORMAL.",
            "confidence": 85, "affected": "none",
            "features": {
                "Lung Colour": "✅ Dark with Age Lines",
                "White Patches": "✅ None (Just Aging)",
                "Heart": "✅ Slightly Enlarged (Age)",
                "AI Decision": "✅ NORMAL (85%)",
                "Heatmap": "✅ Green/Blue Only",
            }
        },
        # Pneumonia cases (5)
        {
            "index": 6, "type": "pneumonia",
            "label": "PNEUMONIA - Right Side Affected",
            "desc": "Right lung shows white haziness. Left lung clear. Right border blurry.",
            "confidence": 97, "affected": "right", "severity": "moderate",
            "features": {
                "Right Lung": "❌ WHITE Haziness",
                "Left Lung": "✅ Clear & Dark",
                "Right Border": "❌ Blurry/Hidden",
                "Ribs (Right)": "❌ Hidden by Fluid",
                "Heatmap": "❌ RED on Right Side",
            }
        },
        {
            "index": 7, "type": "pneumonia",
            "label": "PNEUMONIA - Bilateral (Both Sides)",
            "desc": "BOTH lungs show white opacity. Bilateral pneumonia. High severity.",
            "confidence": 99, "affected": "both", "severity": "moderate",
            "features": {
                "Both Lungs": "❌ White Opacity",
                "Borders": "❌ Both Blurry",
                "Ribs": "❌ Hidden on Both Sides",
                "Severity": "❌ HIGH (Bilateral)",
                "Heatmap": "❌ RED Across Both Lungs",
            }
        },
        {
            "index": 8, "type": "pneumonia",
            "label": "PNEUMONIA - Patchy Pattern",
            "desc": "Scattered white spots in right lung. Patchy consolidation pattern.",
            "confidence": 88, "affected": "right", "severity": "mild",
            "features": {
                "Pattern": "❌ Scattered Patches",
                "Right Lung": "❌ Multiple White Spots",
                "Left Lung": "✅ Clear",
                "Uniformity": "❌ Irregular Pattern",
                "Heatmap": "❌ Yellow-Red Spots",
            }
        },
        {
            "index": 9, "type": "pneumonia",
            "label": "PNEUMONIA - Lower Lobe Only",
            "desc": "Only lower right lobe affected. Upper lungs clear. Localized pneumonia.",
            "confidence": 91, "affected": "right", "severity": "mild",
            "features": {
                "Upper Lungs": "✅ Clear",
                "Lower Right": "❌ Dense White Opacity",
                "Location": "❌ Lower Lobe Focus",
                "Diaphragm": "❌ Right Edge Hidden",
                "Heatmap": "❌ RED at Bottom-Right",
            }
        },
        {
            "index": 10, "type": "pneumonia",
            "label": "PNEUMONIA - Severe Whiteout",
            "desc": "COMPLETE white-out. Both lungs almost fully white. Heart borders hidden. CRITICAL.",
            "confidence": 99.8, "affected": "both", "severity": "severe",
            "features": {
                "BOTH Lungs": "❌ COMPLETE Whiteout",
                "Heart Borders": "❌ NOT Visible",
                "Diaphragm": "❌ Completely Hidden",
                "Severity": "❌ CRITICAL",
                "Heatmap": "❌ FULL RED Alert",
            }
        },
    ]

    all_cards = []

    for case in cases:
        idx = case["index"]
        print(f"\n📸 Generating Image {idx}: {case['label']}...")

        # Generate base X-ray
        if case["type"] == "normal":
            xray, _ = generate_normal_xray(idx, case["desc"])
            gradcam = create_gradcam_overlay(xray, affected="none")
        else:
            xray, _ = generate_pneumonia_xray(idx, case["desc"],
                                              affected=case["affected"],
                                              severity=case.get("severity", "moderate"))
            gradcam = create_gradcam_overlay(xray, affected=case["affected"])

        # Create comparison card
        card = create_comparison_card(
            idx, xray, gradcam,
            case["label"], case["desc"],
            case["confidence"], case["features"]
        )
        
        # Save individual card
        card_path = os.path.join(OUTPUT_DIR, f"image_{idx:02d}_{case['type']}.png")
        card.save(card_path, "PNG")
        print(f"   ✅ Saved: {card_path}")
        all_cards.append(card)

    # Create a combined 5x2 grid image
    print("\n🖼️ Creating combined comparison grid...")
    grid_w = 750
    grid_h = 420 * 10 + 80  # 10 cards stacked + title
    grid = Image.new("RGB", (grid_w, grid_h), (15, 15, 25))
    grid_draw = ImageDraw.Draw(grid)

    # Title
    grid_draw.rectangle([0, 0, grid_w, 70], fill=(30, 60, 100))
    draw_text(grid_draw, "Anti-Gravity System: Normal vs Pneumonia", (20, 10), font_size=22, fill="white")
    draw_text(grid_draw, "10 Image Visual Comparison — Color Features & Grad-CAM Analysis", (20, 40), font_size=14, fill=(180, 200, 255))

    for i, card in enumerate(all_cards):
        grid.paste(card, (0, 75 + i * 420))

    grid_path = os.path.join(OUTPUT_DIR, "all_10_comparison.png")
    grid.save(grid_path, "PNG")
    print(f"\n✅ Combined grid saved: {grid_path}")

    # Create a side-by-side summary card (Normal vs Pneumonia)
    print("\n📊 Creating summary comparison card...")
    summary_w, summary_h = 750, 350
    summary = Image.new("RGB", (summary_w, summary_h), (20, 20, 30))
    s_draw = ImageDraw.Draw(summary)

    # Title
    s_draw.rectangle([0, 0, summary_w, 40], fill=(40, 80, 120))
    draw_text(s_draw, "Quick Summary: Normal vs Pneumonia — Key Visual Differences", (15, 8), font_size=16, fill="white")

    # Normal column
    s_draw.rectangle([15, 55, 360, 330], outline=(40, 160, 80), width=2)
    draw_text(s_draw, "NORMAL LUNGS", (120, 60), font_size=16, fill=(40, 200, 80))
    normal_points = [
        "Lung Colour: DARK (Black)",
        "White Patches: NONE",
        "Borders: Sharp & Clear",
        "Ribs: Visible Through Lungs",
        "Diaphragm: Sharp Edges",
        "Heart: Clearly Visible",
        "Symmetry: Left = Right",
        "Grad-CAM: BLUE (Cool)",
        "Pixel Intensity: Low (0.1-0.3)",
        "AI Class: 0 (Normal)",
    ]
    for j, pt in enumerate(normal_points):
        draw_text(s_draw, f"✅ {pt}", (25, 85 + j * 24), font_size=11, fill=(120, 220, 120))

    # Pneumonia column
    s_draw.rectangle([385, 55, 735, 330], outline=(200, 60, 60), width=2)
    draw_text(s_draw, "PNEUMONIA LUNGS", (490, 60), font_size=16, fill=(255, 80, 80))
    pneumonia_points = [
        "Lung Colour: WHITE (Bright/Hazy)",
        "White Patches: PRESENT",
        "Borders: Blurry & Hidden",
        "Ribs: Hidden by Fluid",
        "Diaphragm: Edges Hidden",
        "Heart: May Be Obscured",
        "Symmetry: Often Asymmetric",
        "Grad-CAM: RED (Hot)",
        "Pixel Intensity: High (0.6-0.9)",
        "AI Class: 1 (Pneumonia)",
    ]
    for j, pt in enumerate(pneumonia_points):
        draw_text(s_draw, f"❌ {pt}", (395, 85 + j * 24), font_size=11, fill=(255, 120, 120))

    summary_path = os.path.join(OUTPUT_DIR, "summary_comparison.png")
    summary.save(summary_path, "PNG")
    print(f"✅ Summary card saved: {summary_path}")

    print("\n" + "=" * 60)
    print(f"  ALL IMAGES SAVED IN: {OUTPUT_DIR}")
    print("=" * 60)
    print(f"\n  📁 {len(all_cards)} individual cards")
    print(f"  📊 1 combined grid image")
    print(f"  📋 1 summary comparison card")
    print(f"  📂 Total: {len(all_cards) + 2} files")


if __name__ == "__main__":
    main()
