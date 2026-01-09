"""
T-09: Life Timer
Game of Life forming time digits with age coloring.
Enhanced: Better mask attraction, ghost trails, clear overlay.
"""

import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class LifeState:
    def __init__(self):
        self.cells = {}  # (x,y) -> age
        self.trails = {}  # (x,y) -> fade
        self.w = 0
        self.h = 0
        self.last_time = ""
        self.mask = set()


_state = LifeState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    # Initialize
    if _state.w != width or _state.h != height:
        _state.w = width
        _state.h = height
        _state.cells = {(x, y): 0 for x in range(width) for y in range(height) if random.random() < 0.08}
    
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    # Update mask
    if time_str != _state.last_time:
        _state.last_time = time_str
        _state.mask = set()
        
        font = FONT_DIGITAL
        text_w = get_text_width(time_str, font)
        text_h = get_char_height(font)
        tx = (width - text_w) // 2
        ty = (height - text_h) // 2
        
        cursor_x = tx
        for char in time_str:
            if char in font:
                bitmap = font[char]
                for row_idx, row_str in enumerate(bitmap):
                    for col_idx, pixel in enumerate(row_str):
                        if pixel != ' ':
                            _state.mask.add((cursor_x + col_idx, ty + row_idx))
                cursor_x += len(bitmap[0]) + 1
            else:
                cursor_x += 3
    
    # Game of Life step
    new_cells = {}
    
    # Get candidates
    candidates = set(_state.cells.keys())
    for (x, y) in list(_state.cells.keys()):
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                candidates.add((x + dx, y + dy))
    
    for (x, y) in candidates:
        # Count neighbors
        count = sum(1 for dy in [-1,0,1] for dx in [-1,0,1] 
                   if (dx != 0 or dy != 0) and (x+dx, y+dy) in _state.cells)
        
        alive = (x, y) in _state.cells
        in_mask = (x, y) in _state.mask
        
        survives = False
        born = False
        
        if in_mask:
            # Sticky mask - easier to survive and be born
            if alive:
                survives = 1 <= count <= 6
            else:
                born = 2 <= count <= 5 or random.random() < 0.12
        else:
            # Standard rules
            if alive:
                survives = count in [2, 3]
            else:
                born = count == 3
        
        if survives:
            age = _state.cells.get((x, y), 0)
            new_cells[(x, y)] = min(age + 0.1, 1.0)
        elif born:
            new_cells[(x, y)] = 0.0
        elif alive:
            # Died - add trail
            _state.trails[(x, y)] = 1.0
    
    _state.cells = new_cells
    
    # Update trails
    new_trails = {}
    for pos, fade in _state.trails.items():
        if fade > 0.1:
            new_trails[pos] = fade - 0.05
    _state.trails = new_trails
    
    # Render
    accent = theme_manager.get_accent()
    
    # Trails (ghosts)
    for (x, y), fade in _state.trails.items():
        if (x, y) not in _state.cells and 0 <= x < width and 0 <= y < height:
            char = '·' if fade < 0.5 else '+'
            z = int(10 + (1 - fade) * 5)
            color = theme_manager.get_color_for_depth(z, 5, 20)
            buffer.set_pixel(x, y, char, z=z, color=color)
    
    # Living cells
    for (x, y), age in _state.cells.items():
        if 0 <= x < width and 0 <= y < height:
            in_mask = (x, y) in _state.mask
            
            if in_mask:
                # Part of time display
                char = '█'
                z = -8
                color = accent
            else:
                # Background life
                char = '▓' if age > 0.5 else '▒'
                z = 5
                color = theme_manager.get_color_for_depth(int(age * 10), 0, 12)
            
            buffer.set_pixel(x, y, char, z=z, color=color)
    
    # GUARANTEED time overlay (always visible)
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2
    
    draw_text(buffer, tx, ty, time_str, font, accent, z=-15)
    
    return (-15, 20)
