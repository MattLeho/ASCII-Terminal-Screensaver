"""
T-14: Snow Clock
Peaceful snowfall with ground accumulation.
Translated from deybacsi/asciiclock backg_snow.cpp
- Each snowflake has individual speed
- Ground accumulation with density tracking
- Horizontal wobble: x += rand() % 3 - 1
- Snow "stacks" when hitting ground or other snow
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_OUTLINE, draw_text, get_text_width, get_char_height


class Snowflake:
    def __init__(self, x, y, max_width, max_height):
        self.x = x
        self.y = y
        self.spd = random.randint(0, 2)  # Speed type 0, 1, 2
        self.spdcounter = 0


# Snow characters by speed: * + .
SNOW_CHARS = ['*', '+', '.']

# Ground snow characters by density: _ . x X
SNOW_GROUND_CHARS = [' ', '_', '.', 'x', 'X']
MAX_SNOW_DENSITY = len(SNOW_GROUND_CHARS) - 1


class SnowState:
    def __init__(self):
        self.flakes = []
        self.ground = {}  # (x, y) -> density
        self.w = 0
        self.h = 0


_state = SnowState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    # Initialize
    if _state.w != width or _state.h != height:
        _state.w = width
        _state.h = height
        _state.flakes = []
        _state.ground = {}
        
        # Create snowflakes (100 from original MAXSNOW)
        for _ in range(100):
            _state.flakes.append(Snowflake(
                random.randint(0, width - 1),
                random.randint(0, height - 1),
                width, height
            ))
        
        # Initial ground line (from original)
        for x in range(width):
            _state.ground[(x, height - 1)] = 1
    
    accent = theme_manager.get_accent()
    
    # Update snowflakes (from original calc_bg_snow)
    for flake in _state.flakes:
        flake.spdcounter += 1
        
        # If counter hits speed threshold, move flake
        if flake.spdcounter > flake.spd + 2:
            flake.spdcounter = 0
            flake.y += 1  # Go down
            
            # Horizontal wobble (from original: x += rand() % 3 - 1)
            flake.x += random.randint(-1, 1)
            
            # Wrap horizontally
            if flake.x < 0:
                flake.x = width - 1
            elif flake.x >= width:
                flake.x = 0
            
            # Check if reached bottom
            if flake.y >= height:
                # Reset to top
                flake.x = random.randint(0, width - 1)
                flake.y = 0
            else:
                # Check collision with ground snow
                if 0 <= flake.x < width and 0 <= flake.y < height:
                    if _state.ground.get((flake.x, flake.y), 0) > 0:
                        # Increase density at landing spot (from inc_snow_bg)
                        for dx in [-1, 0, 1]:
                            nx = flake.x + dx
                            if 0 <= nx < width:
                                key = (nx, flake.y)
                                old_density = _state.ground.get(key, 0)
                                new_density = min(old_density + 1, MAX_SNOW_DENSITY)
                                _state.ground[key] = new_density
                                
                                # Stack upward if full
                                if new_density >= MAX_SNOW_DENSITY and flake.y > 0:
                                    up_key = (nx, flake.y - 1)
                                    _state.ground[up_key] = min(_state.ground.get(up_key, 0) + 1, MAX_SNOW_DENSITY)
    
    # Render snowflakes
    for flake in _state.flakes:
        if 0 <= flake.x < width and 0 <= flake.y < height:
            char = SNOW_CHARS[flake.spd]
            z = 5 - flake.spd  # Faster = closer
            color = theme_manager.get_color_for_depth(z, 0, 8)
            buffer.set_pixel(int(flake.x), int(flake.y), char, z=z, color=color)
    
    # Render ground snow
    for (x, y), density in _state.ground.items():
        if density > 0 and 0 <= x < width and 0 <= y < height:
            char = SNOW_GROUND_CHARS[min(density, MAX_SNOW_DENSITY)]
            buffer.set_pixel(x, y, char, z=10, color=theme_manager.get_color_for_depth(12, 0, 15))
    
    # Time display
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    font = FONT_OUTLINE
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2 - 3  # Above center to avoid ground
    
    tx += int(math.sin(t * 0.5) * 2)
    
    draw_text(buffer, tx, ty, time_str, font, accent, z=-15)
    
    return (-15, 15)
