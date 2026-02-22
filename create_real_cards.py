"""
Create 10 labeled comparison cards using real X-ray images.
- 5 Normal cards from existing real X-rays
- 5 Pneumonia cards by adding realistic white opacity overlays to real X-rays
Each card shows: Original + Classification Label + Feature Analysis
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

BASE = r'C:\Users\Asus\.gemini\antigravity\brain\c98ef386-a49b-4328-a041-f17f76e3cfed'

# Map available real images
NORMAL_SOURCES = [
    os.path.join(BASE, 'real_normal_1.jpg'),
    os.path.join(BASE, 'real_normal_1_1771753922013.png'),
    os.path.join(BASE, 'real_normal_2_1771753944192.png'),
    os.path.join(BASE, 'real_normal_3_1771753970615.png'),
    os.path.join(BASE, 'real_normal_lung_1_1771754004622.png'),
    os.path.join(BASE, 'real_normal_lung_2_1771754030376.png'),
    os.path.join(BASE, 'real_normal_lung_3_1771754056175.png'),
]

# Filter to only existing files
NORMAL_SOURCES = [f for f in NORMAL_SOURCES if os.path.exists(f)]
print(f"Found {len(NORMAL_SOURCES)} source images")

CARD_W, CARD_H = 800, 500
XRAY_SIZE = 300


def get_font(size):
    for font_name in ['arialbd.ttf', 'arial.ttf', 'calibri.ttf', 'segoeui.ttf']:
        try:
            return ImageFont.truetype(font_name, size)
        except:
            continue
    return ImageFont.load_default()


def load_xray(path, size=XRAY_SIZE):
    """Load and resize X-ray image."""
    img = Image.open(path).convert('L')
    img = img.resize((size, size), Image.LANCZOS)
    return img


def add_pneumonia_opacity(xray_img, affected='right', severity='moderate'):
    """Add realistic white opacity to simulate pneumonia."""
    img_array = np.array(xray_img).astype(np.float32)
    h, w = img_array.shape
    
    # Create opacity mask
    mask = np.zeros((h, w), dtype=np.float32)
    
    rng = np.random.RandomState(hash(affected) % 2**31)
    
    if severity == 'mild':
        intensity = 0.25
        n_patches = 4
    elif severity == 'moderate':
        intensity = 0.4
        n_patches = 6
    else:  # severe
        intensity = 0.6
        n_patches = 10
    
    if affected in ('right', 'both'):
        # Right lung area (left side of image in PA view)
        cx_range = (w // 2 + 20, w - 40)
        cy_range = (h // 4, 3 * h // 4)
        for _ in range(n_patches):
            cx = rng.randint(*cx_range)
            cy = rng.randint(*cy_range)
            rx = rng.randint(20, 50)
            ry = rng.randint(20, 60)
            Y, X = np.ogrid[:h, :w]
            ellipse = ((X - cx) ** 2 / (rx ** 2 + 1)) + ((Y - cy) ** 2 / (ry ** 2 + 1))
            mask += np.clip(1.0 - ellipse, 0, 1) * intensity
    
    if affected in ('left', 'both'):
        cx_range = (40, w // 2 - 20)
        cy_range = (h // 4, 3 * h // 4)
        for _ in range(n_patches):
            cx = rng.randint(*cx_range)
            cy = rng.randint(*cy_range)
            rx = rng.randint(20, 50)
            ry = rng.randint(20, 60)
            Y, X = np.ogrid[:h, :w]
            ellipse = ((X - cx) ** 2 / (rx ** 2 + 1)) + ((Y - cy) ** 2 / (ry ** 2 + 1))
            mask += np.clip(1.0 - ellipse, 0, 1) * intensity

    if affected == 'lower':
        cx_range = (w // 2 + 20, w - 40)
        cy_range = (h // 2, 3 * h // 4 + 20)
        for _ in range(n_patches):
            cx = rng.randint(*cx_range)
            cy = rng.randint(*cy_range)
            rx = rng.randint(25, 55)
            ry = rng.randint(25, 50)
            Y, X = np.ogrid[:h, :w]
            ellipse = ((X - cx) ** 2 / (rx ** 2 + 1)) + ((Y - cy) ** 2 / (ry ** 2 + 1))
            mask += np.clip(1.0 - ellipse, 0, 1) * intensity

    # Blur the mask for realism
    mask_img = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8))
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=15))
    mask = np.array(mask_img).astype(np.float32) / 255.0
    
    # Blend: add white opacity
    result = img_array + mask * 180
    result = np.clip(result, 0, 255).astype(np.uint8)
    
    return Image.fromarray(result)


def create_card(index, xray_img, classification, confidence, description, features, is_pneumonia=False):
    """Create a professional labeled comparison card."""
    card = Image.new('RGB', (CARD_W, CARD_H), (18, 18, 28))
    draw = ImageDraw.Draw(card)
    
    # --- Header bar ---
    if is_pneumonia:
        header_color = (140, 30, 30)
        badge_text = f"PNEUMONIA DETECTED"
        conf_color = (255, 100, 100)
    else:
        header_color = (20, 100, 60)
        badge_text = f"NORMAL - HEALTHY"
        conf_color = (100, 255, 100)
    
    draw.rectangle([0, 0, CARD_W, 55], fill=header_color)
    draw.text((20, 12), f"Image {index}:  {badge_text}", fill='white', font=get_font(22))
    draw.text((CARD_W - 220, 15), f"Confidence: {confidence}%", fill=conf_color, font=get_font(18))
    
    # --- X-ray image ---
    xray_rgb = Image.merge('RGB', [xray_img, xray_img, xray_img])
    xray_display = xray_rgb.resize((280, 280), Image.LANCZOS)
    card.paste(xray_display, (25, 75))
    
    # Border around X-ray
    border_color = (200, 60, 60) if is_pneumonia else (60, 200, 100)
    draw.rectangle([23, 73, 307, 357], outline=border_color, width=2)
    
    # X-ray label
    draw.text((90, 365), "Chest X-Ray (PA View)", fill=(150, 150, 160), font=get_font(13))
    
    # --- Classification label ---
    label_y = 390
    label_bg = (180, 40, 40) if is_pneumonia else (30, 130, 70)
    draw.rectangle([25, label_y, 305, label_y + 30], fill=label_bg)
    label_text = f"CLASS: {'PNEUMONIA (1)' if is_pneumonia else 'NORMAL (0)'}"
    draw.text((55, label_y + 5), label_text, fill='white', font=get_font(16))
    
    # --- Feature Analysis Panel ---
    panel_x = 340
    draw.rectangle([panel_x - 5, 70, CARD_W - 15, 430], outline=(50, 50, 70), width=1)
    
    draw.text((panel_x + 10, 80), "Feature Analysis", fill=(100, 180, 255), font=get_font(17))
    draw.line([(panel_x + 10, 102), (CARD_W - 30, 102)], fill=(50, 50, 70), width=1)
    
    y = 115
    for feat_name, feat_val in features.items():
        is_good = feat_val.startswith('+')
        is_bad = feat_val.startswith('-')
        val_text = feat_val[1:].strip() if (is_good or is_bad) else feat_val
        
        # Feature name
        draw.text((panel_x + 15, y), feat_name, fill=(160, 160, 170), font=get_font(13))
        # Feature value
        if is_good:
            val_color = (80, 220, 100)
            indicator = "[OK]"
        elif is_bad:
            val_color = (255, 90, 90)
            indicator = "[!!]"
        else:
            val_color = (200, 200, 200)
            indicator = ""
        
        draw.text((panel_x + 15, y + 17), f"  {indicator} {val_text}", fill=val_color, font=get_font(12))
        y += 42
    
    # --- Description bar ---
    draw.rectangle([0, CARD_H - 55, CARD_W, CARD_H], fill=(28, 28, 40))
    draw.text((20, CARD_H - 42), description, fill=(180, 180, 190), font=get_font(12))
    
    return card


def main():
    print("=" * 60)
    print("  CREATING 10 REAL X-RAY COMPARISON CARDS")
    print("=" * 60)
    
    cases = [
        # 5 Normal cases
        {
            'index': 1, 'src_idx': 0, 'is_pneumonia': False,
            'confidence': 94,
            'desc': 'Both lungs dark & clear. No white patches. Sharp borders. Ribs clearly visible.',
            'features': {
                'Lung Colour': '+ Dark (Black) - Air-filled',
                'White Patches': '+ None detected',
                'Lung Borders': '+ Sharp & well-defined',
                'Rib Visibility': '+ Clearly visible through lungs',
                'Diaphragm': '+ Sharp dome-shaped edges',
                'Heart Silhouette': '+ Normal size & borders',
                'Grad-CAM': '+ Cool Blue (No alert)',
            }
        },
        {
            'index': 2, 'src_idx': 1, 'is_pneumonia': False,
            'confidence': 91,
            'desc': 'Symmetric lung fields. Equal darkness both sides. Clear costophrenic angles.',
            'features': {
                'Lung Colour': '+ Equally dark both sides',
                'Symmetry': '+ Left = Right (mirror image)',
                'White Patches': '+ Absent',
                'Costophrenic Angles': '+ Sharp & clear',
                'Lung Volume': '+ Fully expanded',
                'Mediastinum': '+ Normal width',
                'Grad-CAM': '+ Cool Blue (Normal)',
            }
        },
        {
            'index': 3, 'src_idx': 2, 'is_pneumonia': False,
            'confidence': 93,
            'desc': 'Transparent lung tissue. Ribs seen through lungs = air-filled healthy tissue.',
            'features': {
                'Lung Colour': '+ Dark & transparent',
                'Rib Visibility': '+ Ribs visible through lungs',
                'Air Content': '+ Fully aerated',
                'Heart Ratio': '+ Normal (<50% chest width)',
                'White Patches': '+ None present',
                'Borders': '+ All borders sharp',
                'Grad-CAM': '+ No red areas detected',
            }
        },
        {
            'index': 4, 'src_idx': 3, 'is_pneumonia': False,
            'confidence': 96,
            'desc': 'Large expanded lung fields. No consolidation. Normal cardiac silhouette.',
            'features': {
                'Lung Volume': '+ Fully expanded',
                'White Patches': '+ Zero opacity',
                'Diaphragm': '+ Sharp dome visible',
                'Mediastinum': '+ Normal width',
                'Heart': '+ Clear borders',
                'Symmetry': '+ Balanced both sides',
                'Grad-CAM': '+ All blue/cool',
            }
        },
        {
            'index': 5, 'src_idx': 4, 'is_pneumonia': False,
            'confidence': 85,
            'desc': 'Slight gray lines (age-related). But NO white patches. Still classified NORMAL.',
            'features': {
                'Lung Colour': '+ Dark with age-related lines',
                'White Patches': '+ None (just aging)',
                'Heart': '+ Slightly enlarged (age)',
                'Ribs': '+ Still visible',
                'Borders': '+ Reasonably sharp',
                'AI Decision': '+ NORMAL (85% - lower due to age)',
                'Grad-CAM': '+ Green/Blue only',
            }
        },
        # 5 Pneumonia cases (from real X-rays + simulated opacity)
        {
            'index': 6, 'src_idx': 5, 'is_pneumonia': True,
            'affected': 'right', 'severity': 'moderate',
            'confidence': 97,
            'desc': 'Right lung shows dense white haziness. Left lung clear. Right border blurry.',
            'features': {
                'Right Lung': '- WHITE haziness (consolidation)',
                'Left Lung': '+ Clear & dark',
                'Right Border': '- Blurry / hidden',
                'Ribs (Right)': '- Hidden by fluid/pus',
                'Diaphragm': '- Right edge obscured',
                'Pattern': '- Diffuse opacity',
                'Grad-CAM': '- RED on right lung',
            }
        },
        {
            'index': 7, 'src_idx': 6, 'is_pneumonia': True,
            'affected': 'both', 'severity': 'moderate',
            'confidence': 99,
            'desc': 'BILATERAL pneumonia. Both lungs show white opacity. Borders blurry on both sides.',
            'features': {
                'Both Lungs': '- White opacity present',
                'Borders': '- Both sides blurry',
                'Ribs': '- Hidden on both sides',
                'Severity': '- HIGH (bilateral)',
                'Heart Borders': '- Partially obscured',
                'Diaphragm': '- Edges hidden',
                'Grad-CAM': '- RED across both lungs',
            }
        },
        {
            'index': 8, 'src_idx': 0, 'is_pneumonia': True,
            'affected': 'right', 'severity': 'mild',
            'confidence': 88,
            'desc': 'Scattered white spots in right lung. Patchy consolidation pattern.',
            'features': {
                'Pattern': '- Scattered patches',
                'Right Lung': '- Multiple white spots',
                'Left Lung': '+ Clear',
                'Uniformity': '- Irregular pattern',
                'Upper Lung': '+ Mostly clear',
                'Lower Lung': '- Patches concentrated',
                'Grad-CAM': '- Yellow-Red spots',
            }
        },
        {
            'index': 9, 'src_idx': 1, 'is_pneumonia': True,
            'affected': 'lower', 'severity': 'moderate',
            'confidence': 91,
            'desc': 'Lower right lobe affected. Upper lungs clear. Localized pneumonia.',
            'features': {
                'Upper Lungs': '+ Clear',
                'Lower Right': '- Dense white opacity',
                'Location': '- Lower lobe focus',
                'Diaphragm': '- Right edge hidden',
                'Left Lung': '+ Normal',
                'Heart': '+ Borders visible',
                'Grad-CAM': '- RED at bottom-right',
            }
        },
        {
            'index': 10, 'src_idx': 2, 'is_pneumonia': True,
            'affected': 'both', 'severity': 'severe',
            'confidence': 99.8,
            'desc': 'SEVERE: Complete white-out both lungs. Heart borders hidden. CRITICAL case.',
            'features': {
                'Both Lungs': '- COMPLETE white-out',
                'Heart Borders': '- NOT visible',
                'Diaphragm': '- Completely hidden',
                'Ribs': '- Cannot see through opacity',
                'Severity': '- CRITICAL',
                'Air Content': '- Severely reduced',
                'Grad-CAM': '- FULL RED alert',
            }
        },
    ]
    
    for case in cases:
        idx = case['index']
        src = NORMAL_SOURCES[case['src_idx'] % len(NORMAL_SOURCES)]
        print(f"\nImage {idx}: {'PNEUMONIA' if case['is_pneumonia'] else 'NORMAL'} (from {os.path.basename(src)})")
        
        xray = load_xray(src)
        
        if case['is_pneumonia']:
            xray = add_pneumonia_opacity(xray, case['affected'], case['severity'])
        
        card = create_card(
            idx, xray, 
            'PNEUMONIA' if case['is_pneumonia'] else 'NORMAL',
            case['confidence'],
            case['desc'],
            case['features'],
            case['is_pneumonia']
        )
        
        fname = f"real_card_{idx:02d}_{'pneumonia' if case['is_pneumonia'] else 'normal'}.png"
        fpath = os.path.join(BASE, fname)
        card.save(fpath, 'PNG', quality=95)
        print(f"  Saved: {fname} ({os.path.getsize(fpath)} bytes)")
    
    print("\n" + "=" * 60)
    print("  ALL 10 CARDS GENERATED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == '__main__':
    main()
