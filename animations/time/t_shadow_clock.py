"""
T-04: Shadow Clock
Rotating light source casting dramatic shadows.
Enhanced: Volumetric rays, dust particles, gradient sky, clear time overlay.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class DustParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.1, 0.1)
        self.vy = random.uniform(-0.05, 0.05)
        self.life = random.uniform(2, 5)


class ShadowState:
    def __init__(self):
        self.dust = []


_state = ShadowState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")
    
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    tx = (width - text_w) // 2
    ty = (height - text_h) // 2
    
    # Build solid pixel set for shadow casting
    solid = set()
    cursor_x = tx
    for char in time_str:
        if char in font:
            bitmap = font[char]
            for row_idx, row_str in enumerate(bitmap):
                for col_idx, pixel in enumerate(row_str):
                    if pixel != ' ':
                        solid.add((cursor_x + col_idx, ty + row_idx))
            cursor_x += len(bitmap[0]) + 1
        else:
            cursor_x += 3
    
    # Light source orbit
    orbit_r = min(width, height) * 0.45
    sun_x = width / 2 + math.cos(t * 0.3) * orbit_r
    sun_y = height / 2 + math.sin(t * 0.3) * orbit_r * 0.5
    
    accent = theme_manager.get_accent()
    
    # Spawn dust
    if len(_state.dust) < 30:
        _state.dust.append(DustParticle(random.uniform(0, width), random.uniform(0, height)))
    
    # 1. GRADIENT SKY BACKGROUND
    for y in range(height):
        sky_val = 1.0 - (y / height)
        if sky_val > 0.7:
            for x in range(0, width, 3):
                buffer.set_pixel(x, y, '·', z=20, color=theme_manager.get_color_for_depth(20, 0, 25))
    
    # 2. RENDER SCENE
    for y in range(height):
        for x in range(width):
            # Sun body
            dx = x - sun_x
            dy = y - sun_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < 3:
                char = '☼' if dist < 1 else ('*' if dist < 2 else '·')
                buffer.set_pixel_with_glow(x, y, char, z=-15, color=accent, 
                                          glow_radius=2, theme_manager=theme_manager)
                continue
            
            # Skip solid pixels (handled later)
            if (x, y) in solid:
                continue
            
            # Shadow raycast
            if dist > 0:
                step_x = dx / dist
                step_y = dy / dist
                
                in_shadow = False
                for i in range(1, 20):
                    sx = int(x + step_x * i)
                    sy = int(y + step_y * i)
                    if (sx, sy) in solid:
                        in_shadow = True
                        break
                
                if in_shadow:
                    # Shadow with penumbra
                    buffer.set_pixel(x, y, '░', z=8, color=theme_manager.get_color_for_depth(12, 0, 15))
                else:
                    # Volumetric god rays
                    angle = math.atan2(dy, dx)
                    ray = math.sin(angle * 15 + t * 2) + math.sin(angle * 7 - t)
                    if ray > 1.2:
                        buffer.set_pixel(x, y, '·', z=5, color=theme_manager.get_color_for_depth(5, 0, 10))
    
    # 3. DUST PARTICLES IN LIGHT
    active_dust = []
    for p in _state.dust:
        p.x += p.vx + math.sin(t + p.y * 0.1) * 0.05
        p.y += p.vy
        p.life -= 0.02
        
        if p.life > 0:
            if p.x < 0: p.x = width
            elif p.x >= width: p.x = 0
            if p.y < 0: p.y = height
            elif p.y >= height: p.y = 0
            active_dust.append(p)
            
            # Only visible in light
            px, py = int(p.x), int(p.y)
            dx = sun_x - px
            dy = sun_y - py
            dist = math.sqrt(dx*dx + dy*dy)
            
            in_shadow = False
            if dist > 0:
                step_x = dx / dist
                step_y = dy / dist
                for i in range(1, 15):
                    sx = int(px + step_x * i)
                    sy = int(py + step_y * i)
                    if (sx, sy) in solid:
                        in_shadow = True
                        break
            
            if not in_shadow and 0 <= px < width and 0 <= py < height:
                buffer.set_pixel(px, py, '·', z=2, color=accent)
    
    _state.dust = active_dust
    
    # 4. SOLID TIME DIGITS (Always on top)
    draw_text(buffer, tx, ty, time_str, font, accent, z=-10)
    
    # 5. FLOOR TEXTURE
    floor_y = height - 3
    for y in range(floor_y, height):
        for x in range(width):
            if (x + y) % 4 == 0:
                buffer.set_pixel(x, y, '·', z=15, color=theme_manager.get_color_for_depth(15, 0, 20))
    
    return (-15, 20)
