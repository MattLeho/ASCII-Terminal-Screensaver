"""
T-03: Matrix Clock
Matrix rain that freezes to form time.
Translated from deybacsi/asciiclock backg_matrix.cpp
- One falling line per column
- Each line has: y position, speed, length, bright head char
- Lines reset when fully off screen
"""

import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class MatrixLine:
    """One falling line per column (from original s_matrixchrs)"""
    def __init__(self, max_height):
        self.y = -random.randint(0, max_height // 2)  # Start above screen
        self.spd = random.randint(0, 4)  # Speed (0 = fastest)
        self.counter = 0
        self.length = random.randint(max_height // 5, max_height // 2)
        self.char = chr(random.randint(33, 126))  # Random printable ASCII


class MatrixState:
    def __init__(self):
        self.lines = []
        self.w = 0
        self.h = 0
        self.text_mask = set()
        self.last_sec = -1


_state = MatrixState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    # Initialize lines (one per column)
    if _state.w != width or _state.h != height:
        _state.w = width
        _state.h = height
        _state.lines = [MatrixLine(height) for _ in range(width)]
    
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    # Update text mask on second change
    if now.second != _state.last_sec:
        _state.last_sec = now.second
        _build_mask(time_str, width, height)
    
    accent = theme_manager.get_accent()
    
    # Update and render lines (from original calc_bg_matrix)
    for x, line in enumerate(_state.lines):
        line.counter += 1
        
        if line.counter > line.spd:
            line.counter = 0
            line.y += 1
            
            # New random char for head
            line.char = chr(random.randint(33, 126))
            
            # Reset if tail is off screen
            if line.y - line.length > height:
                line.y = -random.randint(0, height // 2)
                line.spd = random.randint(0, 4)
                line.length = random.randint(height // 5, height // 2)
        
        # Draw line from head to tail
        for offset in range(line.length):
            draw_y = line.y - offset
            
            if not (0 <= draw_y < height):
                continue
            
            # Check if this pixel is part of the time display
            if (x, draw_y) in _state.text_mask:
                # Draw frozen time character
                buffer.set_pixel(x, draw_y, '█', z=-10, color=accent)
            else:
                if offset == 0:
                    # Head character (bright)
                    buffer.set_pixel(x, draw_y, line.char, z=2, color=accent)
                else:
                    # Tail characters (dimmer with distance)
                    fade = offset / line.length
                    if fade < 0.4:
                        char = chr(random.randint(33, 126))
                        z = 5
                    elif fade < 0.7:
                        char = chr(random.randint(33, 126)).lower()
                        z = 8
                    else:
                        char = '.'
                        z = 11
                    
                    color = theme_manager.get_color_for_depth(z, 0, 12)
                    buffer.set_pixel(x, draw_y, char, z=z, color=color)
    
    # Guaranteed time overlay
    draw_text(buffer, 
              (width - get_text_width(time_str, FONT_DIGITAL)) // 2,
              (height - 7) // 2, 
              time_str, FONT_DIGITAL, accent, z=-15)
    
    return (-15, 12)


def _build_mask(time_str, width, height):
    _state.text_mask = set()
    
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = 7  # FONT_DIGITAL height
    
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2
    
    cursor_x = tx
    for char in time_str:
        if char in font:
            bitmap = font[char]
            for row_idx, row_str in enumerate(bitmap):
                for col_idx, pixel in enumerate(row_str):
                    if pixel != ' ':
                        _state.text_mask.add((cursor_x + col_idx, ty + row_idx))
            cursor_x += len(bitmap[0]) + 1
        else:
            cursor_x += 3
