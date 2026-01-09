"""
T-12: Fire Clock
Blazing fire background with floating time display.
Translated from deybacsi/asciiclock backg_fire.cpp
- Double-buffer heat propagation
- 5-neighbor averaging (top, left, center, right, bottom)
- Random flame points throughout
- Character ramp: dark → red → yellow → white
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class FireState:
    def __init__(self):
        self.buffer0 = None  # Current frame
        self.buffer1 = None  # Next frame
        self.w = 0
        self.h = 0


_state = FireState()

# Character ramp from original (23 levels)
FIRE_CHARS = ' ' * 5 + '.+xXxXxXxXxXxX'
FIRE_LEVELS = len(FIRE_CHARS)


def render(buffer, width, height, t, theme_manager):
    global _state
    
    # Initialize buffers
    if _state.buffer0 is None or _state.w != width or _state.h != height:
        _state.w = width
        _state.h = height
        _state.buffer0 = [[0] * width for _ in range(height)]
        _state.buffer1 = [[0] * width for _ in range(height)]
    
    # 1. Copy buffer1 -> buffer0 (from original copy_back_buffer)
    for y in range(height):
        for x in range(width):
            _state.buffer0[y][x] = _state.buffer1[y][x]
    
    # 2. Draw random bottom (feeds the fire)
    for x in range(width):
        _state.buffer0[height - 1][x] = random.randint(0, FIRE_LEVELS - 1)
    
    # 3. Draw random flame points (from original draw_fire_random)
    max_random = (width * height) // 20
    for _ in range(max_random // 10):
        rx = random.randint(0, width - 1)
        ry = random.randint(height * 3 // 4, height - 1)
        _state.buffer0[ry][rx] = FIRE_LEVELS - 1
    
    # 4. Calculate next frame with 5-neighbor averaging
    for y in range(1, height):
        for x in range(1, width - 1):
            # Get 5 neighbors: top, left, center, right, bottom
            top = _state.buffer0[max(0, y - 1)][x]
            left = _state.buffer0[y][x - 1]
            center = _state.buffer0[y][x]
            right = _state.buffer0[y][x + 1]
            bottom = _state.buffer0[min(height - 1, y + 1)][x]
            
            # Average and propagate upward (to y-1)
            average = (top + left + center + right + bottom) // 5
            average = min(average, FIRE_LEVELS - 1)
            
            if y > 0:
                _state.buffer1[y - 1][x] = average
    
    # 5. Render fire to screen
    accent = theme_manager.get_accent()
    
    for y in range(height):
        for x in range(width):
            level = _state.buffer1[y][x]
            
            if level > 0:
                char_idx = min(level, len(FIRE_CHARS) - 1)
                char = FIRE_CHARS[char_idx]
                
                if char != ' ':
                    # Map level to z-depth (higher = brighter = closer)
                    z = 10 - int((level / FIRE_LEVELS) * 12)
                    color = theme_manager.get_color_for_depth(z, -5, 12)
                    buffer.set_pixel(x, y, char, z=z, color=color)
    
    # 6. Draw bottom row (from original)
    for x in range(width):
        level = _state.buffer1[height - 1][x]
        if level > 5:
            buffer.set_pixel(x, height - 1, 'X', z=-3, color=accent)
    
    # 7. Time display with glow
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2
    ty += int(math.sin(t * 1.5) * 2)
    
    # Glow layers
    for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        draw_text(buffer, tx + ox, ty + oy, time_str, font,
                  theme_manager.get_color_for_depth(-8, -12, 0), z=-12)
    
    draw_text(buffer, tx, ty, time_str, font, accent, z=-18)
    
    return (-18, 12)
