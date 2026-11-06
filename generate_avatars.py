# generate_avatars.py - Generate high-resolution sleek, futuristic AI avatars for ARIS
import os
import math
from PIL import Image, ImageDraw

def create_avatars():
    os.makedirs("avatars", exist_ok=True)
    size = (256, 256)

    # 1. ARIS NEXUS (Default - Regal Champagne Gold & Burgundy Iris)
    img1 = Image.new("RGBA", size, (32, 8, 16, 255)) # #200810
    draw1 = ImageDraw.Draw(img1)
    cx, cy = 128, 128

    # Outer border circle
    draw1.ellipse((10, 10, 246, 246), outline=(87, 37, 54, 255), width=2)
    # Concentric rings
    draw1.ellipse((35, 35, 221, 221), outline=(214, 184, 117, 100), width=2)
    draw1.ellipse((60, 60, 196, 196), outline=(214, 184, 117, 180), width=3)
    draw1.ellipse((85, 85, 171, 171), outline=(214, 184, 117, 240), width=2)
    # Crosshair tick marks
    draw1.line((128, 20, 128, 48), fill=(214, 184, 117, 220), width=2)
    draw1.line((128, 208, 128, 236), fill=(214, 184, 117, 220), width=2)
    draw1.line((20, 128, 48, 128), fill=(214, 184, 117, 220), width=2)
    draw1.line((208, 128, 236, 128), fill=(214, 184, 117, 220), width=2)
    # Central glowing iris
    draw1.ellipse((108, 108, 148, 148), fill=(214, 184, 117, 255))
    draw1.ellipse((118, 118, 138, 138), fill=(245, 239, 230, 255))
    img1.save("avatars/aris_nexus.png")

    # 2. QUANTUM ARC (Cyan & Electric Ice Blue Futuristic Cybernetic Core)
    img2 = Image.new("RGBA", size, (16, 24, 32, 255))
    draw2 = ImageDraw.Draw(img2)
    draw2.ellipse((10, 10, 246, 246), outline=(0, 229, 255, 60), width=2)
    # Arc segments
    draw2.arc((40, 40, 216, 216), start=30, end=150, fill=(0, 229, 255, 230), width=4)
    draw2.arc((40, 40, 216, 216), start=210, end=330, fill=(0, 229, 255, 230), width=4)
    draw2.arc((70, 70, 186, 186), start=120, end=240, fill=(128, 240, 255, 200), width=3)
    draw2.arc((70, 70, 186, 186), start=300, end=60, fill=(128, 240, 255, 200), width=3)
    # Core
    draw2.ellipse((106, 106, 150, 150), outline=(0, 229, 255, 255), width=2)
    draw2.ellipse((116, 116, 140, 140), fill=(0, 229, 255, 255))
    draw2.ellipse((123, 123, 133, 133), fill=(255, 255, 255, 255))
    img2.save("avatars/quantum_arc.png")

    # 3. NEURAL PULSE (Dusty Rose & Gold Constellation)
    img3 = Image.new("RGBA", size, (43, 11, 22, 255)) # #2B0B16
    draw3 = ImageDraw.Draw(img3)
    draw3.ellipse((12, 12, 244, 244), outline=(87, 37, 54, 255), width=2)
    # Star polygon / neural nodes
    nodes = []
    for i in range(8):
        angle = i * (math.pi / 4)
        r = 75
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        nodes.append((x, y))
    for i in range(len(nodes)):
        x1, y1 = nodes[i]
        x2, y2 = nodes[(i + 3) % len(nodes)]
        draw3.line((x1, y1, x2, y2), fill=(201, 143, 158, 120), width=2)
        draw3.line((cx, cy, x1, y1), fill=(214, 184, 117, 140), width=2)
    for x, y in nodes:
        draw3.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(201, 143, 158, 240), outline=(214, 184, 117, 255), width=1)
    draw3.ellipse((112, 112, 144, 144), fill=(214, 184, 117, 255))
    draw3.ellipse((120, 120, 136, 136), fill=(245, 239, 230, 255))
    img3.save("avatars/neural_pulse.png")

    # 4. TITAN MONOLITH (Dark Titanium & Gold Hexagon Core)
    img4 = Image.new("RGBA", size, (30, 26, 34, 255))
    draw4 = ImageDraw.Draw(img4)
    draw4.ellipse((12, 12, 244, 244), outline=(70, 60, 75, 255), width=2)
    # Hexagon
    hex_points = []
    for i in range(6):
        angle = i * (math.pi / 3) - (math.pi / 6)
        r = 70
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        hex_points.append((x, y))
    draw4.polygon(hex_points, outline=(214, 184, 117, 230), width=3)
    # Inner diamond
    diamond = [(128, 85), (163, 128), (128, 171), (93, 128)]
    draw4.polygon(diamond, outline=(214, 184, 117, 255), fill=(43, 11, 22, 200), width=2)
    draw4.ellipse((118, 118, 138, 138), fill=(214, 184, 117, 255))
    img4.save("avatars/titan_monolith.png")

    print("[PASS] Generated 4 futuristic avatars in avatars/ directory")

if __name__ == "__main__":
    create_avatars()

