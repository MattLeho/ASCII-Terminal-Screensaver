"""
T-07: Water Timer
Draining water with reveal mechanic and fluid physics.
Enhanced: Better waves, bubbles, splash particles, clear time.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class Bubble:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = random.uniform(0.2, 0.5)
        self.wobble = random.uniform(0, 6.28)


class Splash:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-1, -0.3)
        self.life = 1.0


class WaterState:
    def __init__(self):
        self.bubbles = []
        self.splashes = []


_state = WaterState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    
    # 60-second timer
    total = 60.0
    elapsed = now.second + now.microsecond / 1e6
    remaining = total - elapsed
    progress = elapsed / total
    
    # Water level
    water_height = height * (1.0 - progress)
    base_surface = height - water_height
    
    accent = theme_manager.get_accent()
    
    # Build time mask
    time_str = f"{int(remaining):02d}"
    if remaining < 1:
        time_str = "00"
    
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2
    
    text_pixels = set()
    cursor_x = tx
    for char in time_str:
        if char in font:
            bitmap = font[char]
            for row_idx, row_str in enumerate(bitmap):
                for col_idx, pixel in enumerate(row_str):
                    if pixel != ' ':
                        text_pixels.add((cursor_x + col_idx, ty + row_idx))
            cursor_x += len(bitmap[0]) + 1
        else:
            cursor_x += 3
    
    # Spawn bubbles
    if random.random() < 0.1 and water_height > 5:
        _state.bubbles.append(Bubble(random.uniform(0, width), height - 1))
    
    # Update bubbles
    active_bubbles = []
    for b in _state.bubbles:
        b.y -= b.speed
        b.x += math.sin(t * 3 + b.wobble) * 0.2
        
        surface_at_x = base_surface + math.sin(b.x * 0.3 + t * 3) * 1.5
        
        if b.y > surface_at_x:
            active_bubbles.append(b)
            bx, by = int(b.x), int(b.y)
            if 0 <= bx < width and 0 <= by < height:
                buffer.set_pixel(bx, by, 'o', z=3, color=accent)
        else:
            # Pop - spawn splash
            _state.splashes.append(Splash(b.x, b.y))
    
    _state.bubbles = active_bubbles
    
    # Update splashes
    active_splashes = []
    for s in _state.splashes:
        s.x += s.vx
        s.y += s.vy
        s.vy += 0.1
        s.life -= 0.1
        
        if s.life > 0 and 0 <= s.x < width and 0 <= s.y < height:
            active_splashes.append(s)
            buffer.set_pixel(int(s.x), int(s.y), '·', z=-2, color=accent)
    
    _state.splashes = active_splashes
    
    # Render scene
    for y in range(height):
        for x in range(width):
            # Wave calculation
            wave = math.sin(x * 0.3 + t * 4) * 1.5 + math.sin(x * 0.1 - t * 2) * 0.5
            surface_y = base_surface + wave
            
            is_underwater = y > surface_y
            is_text = (x, y) in text_pixels
            
            if is_underwater:
                depth = y - surface_y
                
                if is_text:
                    # Text behind water - faintly visible
                    if (x + y + int(t * 5)) % 3 == 0:
                        buffer.set_pixel(x, y, '▒', z=6, color=theme_manager.get_color_for_depth(8, 0, 10))
                else:
                    # Water body
                    if depth < 3:
                        char = '░'
                    elif depth < 8:
                        char = '▒'
                    else:
                        char = '▓'
                    
                    color = theme_manager.get_color_for_depth(int(depth), 0, 15)
                    buffer.set_pixel(x, y, char, z=5, color=color)
            else:
                # Above water
                if is_text:
                    buffer.set_pixel(x, y, '█', z=-10, color=accent)
            
            # Surface foam
            if abs(y - surface_y) < 0.8:
                buffer.set_pixel(x, y, '~', z=-5, color=accent)
    
    # Fixed time overlay at top
    full_time = now.strftime("%H:%M:%S")
    overlay_w = get_text_width(full_time, font)
    overlay_x = (width - overlay_w) // 2
    overlay_y = 2
    
    draw_text(buffer, overlay_x, overlay_y, full_time, font, accent, z=-15)
    
    return (-15, 15)
