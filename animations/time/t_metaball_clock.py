"""
T-02: Metaball Clock
Organic blob digits with plasma interior and specular highlights.
Enhanced: Clearer digit shapes, pulsing glow, smoother animation.
"""

import math
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


def render(buffer, width, height, t, theme_manager):
    """Render metaball-style clock with clear digits."""
    
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    cx = width // 2
    cy = height // 2
    tx = cx - text_w // 2
    ty = cy - text_h // 2
    
    accent = theme_manager.get_accent()
    
    # 1. PULSING PLASMA BACKGROUND
    pulse = math.sin(t * 2) * 0.3 + 0.7
    
    for y in range(height):
        for x in range(width):
            # Distance from center
            dx = (x - cx) / width
            dy = (y - cy) / height
            dist = math.sqrt(dx*dx + dy*dy)
            
            # Plasma waves
            v = math.sin(x * 0.1 + t) + math.sin(y * 0.1 - t * 0.5)
            v += math.sin(dist * 10 - t * 2) * 0.5
            v = (v + 3) / 6  # Normalize
            
            # Only draw if strong enough
            if v > 0.4:
                char = '·' if v < 0.6 else ('░' if v < 0.8 else '▒')
                z = int((1 - v) * 15)
                color = theme_manager.get_color_for_depth(z, 0, 15)
                buffer.set_pixel(x, y, char, z=z, color=color)
    
    # 2. BLOB FIELD AROUND TEXT
    # Create blob centers from font pixels
    blob_centers = []
    cursor_x = tx
    for char in time_str:
        if char in font:
            bitmap = font[char]
            for row_idx, row_str in enumerate(bitmap):
                for col_idx, pixel in enumerate(row_str):
                    if pixel != ' ':
                        blob_centers.append((cursor_x + col_idx, ty + row_idx))
            cursor_x += len(bitmap[0]) + 1
        else:
            cursor_x += 3
    
    # Draw blob field
    for y in range(max(0, ty - 3), min(height, ty + text_h + 3)):
        for x in range(max(0, tx - 3), min(width, tx + text_w + 3)):
            # Calculate field strength
            field = 0
            for bx, by in blob_centers:
                dx = x - bx
                dy = y - by
                dist_sq = dx*dx + dy*dy + 0.1
                field += 1.0 / dist_sq
            
            # Threshold
            if field > 0.8:
                # Inside blob
                intensity = min(field / 2, 1)
                char = '█' if intensity > 0.8 else '▓'
                
                # Specular highlight (top-left bias)
                is_highlight = False
                for bx, by in blob_centers:
                    if abs(x - bx) <= 1 and abs(y - by) <= 1:
                        if x <= bx and y <= by:
                            is_highlight = True
                            break
                
                if is_highlight and field > 1.5:
                    char = '█'
                    z = -12
                else:
                    z = -8
                
                buffer.set_pixel(x, y, char, z=z, color=accent)
            elif field > 0.4:
                # Edge glow
                buffer.set_pixel(x, y, '░', z=-5, color=theme_manager.get_color_for_depth(-3, -10, 0))
    
    # 3. CRISP TEXT OVERLAY (Guarantee readability)
    draw_text(buffer, tx, ty, time_str, font, accent, z=-15)
    
    return (-15, 15)
