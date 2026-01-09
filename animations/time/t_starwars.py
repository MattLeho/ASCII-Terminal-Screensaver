"""
T-05: Star Wars Scroll
Perspective scrolling with hyperspace background.
Enhanced: Fixed time display, better perspective, more effects.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class Star:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = random.uniform(-100, 100)
        self.y = random.uniform(-100, 100)
        self.z = random.uniform(50, 150)


class StarWarsState:
    def __init__(self):
        self.stars = [Star() for _ in range(80)]


_state = StarWarsState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    cx = width // 2
    cy = height // 2
    
    accent = theme_manager.get_accent()
    
    # 1. HYPERSPACE STARFIELD
    for star in _state.stars:
        star.z -= 2.0  # Speed
        
        if star.z <= 1:
            star.reset()
            star.z = 150
        
        # Project to screen
        k = 128.0 / star.z
        sx = int(cx + star.x * k)
        sy = int(cy + star.y * k * 0.5)  # Flatten for perspective
        
        if 0 <= sx < width and 0 <= sy < height:
            # Streak based on depth
            if star.z < 30:
                char = '═' if abs(star.x) > abs(star.y) else '║'
            elif star.z < 60:
                char = '-' if abs(star.x) > abs(star.y) else '|'
            else:
                char = '*' if star.z < 100 else '·'
            
            z = int(star.z / 10)
            color = theme_manager.get_color_for_depth(z, 0, 15)
            buffer.set_pixel(sx, sy, char, z=z, color=color)
    
    # 2. CRAWL TEXT
    lines = [
        "",
        "EPISODE MMXXVI",
        "",
        "A NEW TIME",
        "",
        "It is a period of",
        "digital revolution.",
        "",
        "The clock strikes",
        "across the galaxy...",
        "",
        f"{now.strftime('%A').upper()}",
        f"{now.strftime('%B %d, %Y').upper()}",
        "",
        "",
        "",
    ]
    
    scroll_speed = 1.5
    total_scroll = len(lines) * 6
    scroll_pos = (t * scroll_speed) % (total_scroll + height)
    
    vanish_y = height // 4  # Horizon line
    
    for i, line in enumerate(lines):
        if not line:
            continue
        
        # Virtual Y position
        line_y = height + 5 - scroll_pos + i * 4
        
        # Skip if off screen
        if line_y < vanish_y - 5 or line_y > height + 10:
            continue
        
        # Perspective scale
        dist_from_vanish = line_y - vanish_y
        if dist_from_vanish <= 0:
            continue
        
        scale = min(2.0, 50.0 / dist_from_vanish)
        if scale < 0.2:
            continue
        
        screen_y = int(vanish_y + dist_from_vanish * 0.8)
        if not (0 <= screen_y < height):
            continue
        
        # Horizontal layout
        char_spacing = max(1, int(scale * 1.2))
        line_width = len(line) * char_spacing
        start_x = cx - line_width // 2
        
        z = int(15 - scale * 5)
        color = theme_manager.get_color_for_depth(z, 0, 15)
        
        for ci, char in enumerate(line):
            px = start_x + ci * char_spacing
            
            if 0 <= px < width:
                # Fade effect for distant text
                if scale < 0.5 and (px + screen_y) % 2 == 0:
                    continue
                
                buffer.set_pixel(px, screen_y, char, z=z, color=color)
                
                # Bold effect for close text
                if scale > 1.0 and px + 1 < width:
                    buffer.set_pixel(px + 1, screen_y, char, z=z, color=color)
    
    # 3. FIXED TIME DISPLAY (Always visible at bottom)
    time_str = now.strftime("%H:%M:%S")
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    # Position at bottom center
    tx = (width - text_w) // 2
    ty = height - text_h - 2
    
    # Background box for readability
    for y in range(ty - 1, ty + text_h + 1):
        for x in range(tx - 2, tx + text_w + 2):
            if 0 <= x < width and 0 <= y < height:
                buffer.set_pixel(x, y, ' ', z=-18, color=accent)
    
    # Draw time
    draw_text(buffer, tx, ty, time_str, font, accent, z=-20)
    
    # 4. SIDE DECORATIONS
    for y in range(0, height, 3):
        # Left border
        buffer.set_pixel(1, y, '│', z=-5, color=theme_manager.get_color_for_depth(-3, -5, 0))
        # Right border
        buffer.set_pixel(width - 2, y, '│', z=-5, color=theme_manager.get_color_for_depth(-3, -5, 0))
    
    return (-20, 15)
