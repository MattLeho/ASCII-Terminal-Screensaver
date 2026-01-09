"""
T-10: Hourglass Timer
Detailed hourglass with sand physics and decorative frame.
Enhanced: Better sand piling, glass effects, stream wobble, clear time.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class SandGrain:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = random.uniform(0.3, 0.8)


class HourglassState:
    def __init__(self):
        self.grains = []
        self.last_sec = -1


_state = HourglassState()


def _draw_line(buffer, x0, y0, x1, y1, char, z, color):
    """Bresenham line drawing."""
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        buffer.set_pixel(x0, y0, char, z=z, color=color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    elapsed = now.second + now.microsecond / 1e6
    progress = elapsed / 60.0  # 0 to 1 over minute
    
    # Reset every minute
    if now.second == 0 and _state.last_sec != 0:
        _state.grains = []
    _state.last_sec = now.second
    
    cx = width // 2
    cy = height // 2
    
    # Glass dimensions
    glass_w = min(width // 3, 32)
    glass_h = min(height - 10, 30)
    half_w = glass_w // 2
    
    top_y = cy - glass_h // 2
    bot_y = cy + glass_h // 2
    neck_y = cy
    
    accent = theme_manager.get_accent()
    frame_color = theme_manager.get_color_for_depth(-5, -10, 0)
    
    # 1. DECORATIVE FRAME
    # Top cap with ornaments
    for dx in range(-half_w - 3, half_w + 4):
        buffer.set_pixel(cx + dx, top_y - 2, '═', z=-8, color=frame_color)
        buffer.set_pixel(cx + dx, bot_y + 2, '═', z=-8, color=frame_color)
    
    # Corners
    buffer.set_pixel(cx - half_w - 3, top_y - 2, '╔', z=-8, color=frame_color)
    buffer.set_pixel(cx + half_w + 3, top_y - 2, '╗', z=-8, color=frame_color)
    buffer.set_pixel(cx - half_w - 3, bot_y + 2, '╚', z=-8, color=frame_color)
    buffer.set_pixel(cx + half_w + 3, bot_y + 2, '╝', z=-8, color=frame_color)
    
    # Vertical supports
    for dy in range(top_y - 1, bot_y + 2):
        buffer.set_pixel(cx - half_w - 3, dy, '║', z=-8, color=frame_color)
        buffer.set_pixel(cx + half_w + 3, dy, '║', z=-8, color=frame_color)
    
    # Glass outline
    _draw_line(buffer, cx - half_w, top_y, cx, neck_y, '\\', -5, frame_color)
    _draw_line(buffer, cx + half_w, top_y, cx, neck_y, '/', -5, frame_color)
    _draw_line(buffer, cx - half_w, bot_y, cx, neck_y, '/', -5, frame_color)
    _draw_line(buffer, cx + half_w, bot_y, cx, neck_y, '\\', -5, frame_color)
    _draw_line(buffer, cx - half_w, top_y, cx + half_w, top_y, '─', -5, frame_color)
    _draw_line(buffer, cx - half_w, bot_y, cx + half_w, bot_y, '─', -5, frame_color)
    
    # Glass reflections
    for i in range(3):
        ry = top_y + 2 + i + int(math.sin(t + i) * 0.5)
        rx = cx - half_w + 3 + i
        if ry < neck_y:
            buffer.set_pixel(rx, ry, '░', z=-10, color=theme_manager.get_color_for_depth(-12, -15, 0))
    
    # 2. SAND CALCULATION
    max_sand_h = glass_h // 2 - 2
    top_sand_h = int(max_sand_h * (1.0 - progress))
    bot_sand_h = int(max_sand_h * progress)
    
    # 3. TOP SAND (Draining cone)
    for y_off in range(top_sand_h):
        y = neck_y - 1 - y_off
        span = int(y_off * (half_w / max_sand_h))
        span = min(span, half_w - 1)
        
        for dx in range(-span, span + 1):
            x = cx + dx
            # Vary sand texture
            char = '░' if (x + y) % 3 == 0 else ('▒' if (x + y) % 2 == 0 else '▓')
            buffer.set_pixel(x, y, char, z=0, color=accent)
    
    # 4. BOTTOM SAND (Growing pile - pyramid shape, wide at base)
    for y_off in range(bot_sand_h):
        y = bot_y - 1 - y_off  # y_off=0 is bottom, y_off increases going up
        
        # Invert: at bottom (y_off=0), span should be LARGE (base of pyramid)
        # At top (y_off=bot_sand_h-1), span should be SMALL (peak)
        dist_from_peak = bot_sand_h - 1 - y_off  # 0 at peak, large at base
        pile_span = int((dist_from_peak + 1) * 2.5)
        
        # Also limit by glass walls (Triangular bottom: Wide at bottom, Narrow at neck)
        # Width is proportional to distance from neck (y - neck_y)
        glass_h_bottom = bot_y - neck_y
        max_span = int((y - neck_y) * (half_w / glass_h_bottom)) - 1
        
        # Clip
        span = min(pile_span, max_span, half_w - 1)
        
        for dx in range(-span, span + 1):
            x = cx + dx
            char = '▓' if (x + y) % 2 == 0 else '▒'
            buffer.set_pixel(x, y, char, z=0, color=accent)
    
    # 5. FALLING STREAM
    if top_sand_h > 0:
        pile_top = bot_y - bot_sand_h
        wobble = math.sin(t * 10) * 0.8
        
        for y in range(neck_y, pile_top):
            wx = int(cx + wobble)
            char = ':' if (y + int(t * 15)) % 2 == 0 else '·'
            buffer.set_pixel(wx, y, char, z=-3, color=accent)
        
        # Impact splash
        if int(t * 20) % 4 == 0:
            for offset in [-1, 1]:
                if 0 <= cx + offset < width and pile_top < height:
                    buffer.set_pixel(cx + offset, pile_top, '·', z=-3, color=accent)
    
    # 6. TIME DISPLAY
    remaining = 60 - int(elapsed)
    time_str = f"{remaining:02d}"
    
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    tx = cx - text_w // 2
    ty = bot_y + 4
    
    if ty + text_h < height:
        draw_text(buffer, tx, ty, time_str, font, accent, z=-10)
    
    # Full time at top
    full_time = now.strftime("%H:%M:%S")
    full_w = get_text_width(full_time, font)
    full_x = cx - full_w // 2
    full_y = top_y - 5
    
    if full_y >= 0:
        draw_text(buffer, full_x, full_y, full_time, font, accent, z=-15)
    
    return (-15, 10)
