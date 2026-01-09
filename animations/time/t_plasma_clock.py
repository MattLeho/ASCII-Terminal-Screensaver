"""
T-13: Plasma Clock
Psychedelic plasma waves background.
Translated from deybacsi/asciiclock backg_plasma.cpp
- Uses precalculated sin/cos for speed
- Complex multi-wave formula from original
- Character set: space . + x X
"""

import math
from datetime import datetime
from ..utils.fonts import FONT_BLOCK, draw_text, get_text_width, get_char_height


class PlasmaState:
    def __init__(self):
        # Precalculate sin/cos tables (0-360 degrees)
        self.sin_table = [math.sin(i * math.pi / 180) for i in range(361)]
        self.cos_table = [math.cos(i * math.pi / 180) for i in range(361)]
        self.time = 0


_state = PlasmaState()

# Character ramp from original: . + x X
MAX_PLASMA_CHARS = 10
PLASMA_CHARS = ' .+xXxX+. '


def render(buffer, width, height, t, theme_manager):
    global _state
    
    _state.time += 1
    plasma_time = _state.time
    
    accent = theme_manager.get_accent()
    
    # Plasma calculation (translated from original)
    for y in range(height):
        for x in range(width):
            # From original backg_plasma.cpp:
            # double t = plasma_time * 0.2;
            # double k = (t + y) * 0.02;
            # double v1 = 10 + 10 * sin(0.075 * (x * sin(k) + (y*2) * cos(k * 2)));
            # double v2 = 10 + 10 * sin(0.055 * (x * cos(k * 3) + (y*2) * sin(k * 4)));
            # double v3 = 10 + 10 * cos((t + (y*2)) * 0.04);
            # double v4 = 10 + 10 * sin((t + x) * 0.04);
            # double v5 = 10 + 10 * sin(k + sqrt(v3 + v4));
            # double v6 = (v1 + v2 + v5) / 3;
            
            pt = plasma_time * 0.2
            k = (pt + y) * 0.02
            
            v1 = 10 + 10 * math.sin(0.075 * (x * math.sin(k) + (y * 2) * math.cos(k * 2)))
            v2 = 10 + 10 * math.sin(0.055 * (x * math.cos(k * 3) + (y * 2) * math.sin(k * 4)))
            v3 = 10 + 10 * math.cos((pt + (y * 2)) * 0.04)
            v4 = 10 + 10 * math.sin((pt + x) * 0.04)
            v5 = 10 + 10 * math.sin(k + math.sqrt(abs(v3 + v4)))
            v6 = (v1 + v2 + v5) / 3
            
            c = int(v6) % MAX_PLASMA_CHARS
            
            char = PLASMA_CHARS[c]
            
            if char != ' ':
                # Color based on character index
                z = 12 - c
                color = theme_manager.get_color_for_depth(z, 0, 12)
                buffer.set_pixel(x, y, char, z=z, color=color)
    
    # Time display
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    font = FONT_BLOCK
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2
    
    # Gentle floating
    tx += int(math.cos(t * 1.3) * 1.5)
    ty += int(math.sin(t * 1.8) * 1)
    
    # Shadow
    draw_text(buffer, tx + 1, ty + 1, time_str, font,
              theme_manager.get_color_for_depth(5, 0, 10), z=-12)
    
    # Main text
    draw_text(buffer, tx, ty, time_str, font, accent, z=-18)
    
    return (-18, 12)
