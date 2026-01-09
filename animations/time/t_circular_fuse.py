"""
T-08: Circular Fuse
Spark traveling around countdown circle with particle effects.
Enhanced: Burnt sections disappear, fire burst on reset.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class Spark:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = 1.0


class Smoke:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 1.0


class FireParticle:
    """Fire particle for reset burst effect."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, 6.28)
        speed = random.uniform(1, 4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed - 1.5
        self.life = random.uniform(0.5, 1.0)
        self.heat = random.uniform(0.7, 1.0)


class FuseState:
    def __init__(self):
        self.sparks = []
        self.smoke = []
        self.fire = []
        self.mode = 0
        self.last_sec = -1
        self.reset_burst = False


_state = FuseState()

FIRE_CHARS = ' .+xX█'


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    
    # Detect reset
    if now.second == 0 and _state.last_sec == 59:
        _state.reset_burst = True
    _state.last_sec = now.second
    
    val = now.second + now.microsecond / 1e6
    total = 60.0
    progress = val / total
    
    cx = width // 2
    cy = height // 2
    
    rx = min(width // 2 - 4, 28)
    ry = min(height // 2 - 4, 14)
    
    current_angle = -math.pi / 2 + progress * 2 * math.pi
    
    accent = theme_manager.get_accent()
    
    spark_x = cx + math.cos(current_angle) * rx * 2
    spark_y = cy + math.sin(current_angle) * ry
    
    # Fire burst on reset
    if _state.reset_burst:
        for _ in range(60):
            angle = random.uniform(0, 6.28)
            fx = cx + math.cos(angle) * rx * 2
            fy = cy + math.sin(angle) * ry
            _state.fire.append(FireParticle(fx, fy))
        _state.reset_burst = False
    
    # Update fire
    active_fire = []
    for f in _state.fire:
        f.x += f.vx
        f.y += f.vy
        f.vy += 0.15
        f.life -= 0.04
        f.heat -= 0.02
        
        if f.life > 0 and 0 <= f.x < width and 0 <= f.y < height:
            active_fire.append(f)
            char_idx = int(f.heat * (len(FIRE_CHARS) - 1))
            char_idx = max(0, min(len(FIRE_CHARS) - 1, char_idx))
            char = FIRE_CHARS[char_idx]
            if char != ' ':
                z = int(5 - f.life * 5)
                color = theme_manager.get_color_for_depth(z - 5, -10, 5)
                buffer.set_pixel(int(f.x), int(f.y), char, z=z, color=color)
    
    _state.fire = active_fire
    
    # Emit sparks
    for _ in range(3):
        angle = random.uniform(0, 6.28)
        speed = random.uniform(0.5, 2)
        _state.sparks.append(Spark(
            spark_x, spark_y,
            math.cos(angle) * speed,
            math.sin(angle) * speed - 0.5
        ))
    
    if random.random() < 0.3:
        _state.smoke.append(Smoke(spark_x, spark_y))
    
    # Update sparks
    active_sparks = []
    for s in _state.sparks:
        s.x += s.vx
        s.y += s.vy
        s.vy += 0.1
        s.life -= 0.08
        
        if s.life > 0 and 0 <= s.x < width and 0 <= s.y < height:
            active_sparks.append(s)
            char = '*' if s.life > 0.5 else '·'
            z = int(5 - s.life * 5)
            buffer.set_pixel(int(s.x), int(s.y), char, z=z, color=accent)
    
    _state.sparks = active_sparks
    
    # Update smoke
    active_smoke = []
    for s in _state.smoke:
        s.x += random.uniform(-0.3, 0.3)
        s.y -= 0.3
        s.life -= 0.03
        
        if s.life > 0 and 0 <= s.y < height:
            active_smoke.append(s)
            char = '░' if s.life > 0.5 else '·'
            buffer.set_pixel(int(s.x), int(s.y), char, z=8, color=theme_manager.get_color_for_depth(10, 0, 15))
    
    _state.smoke = active_smoke
    
    # Draw fuse ring - burnt sections DISAPPEAR
    steps = 120
    for i in range(steps):
        step_progress = i / steps
        theta = -math.pi / 2 + step_progress * 2 * math.pi
        
        px = int(cx + math.cos(theta) * rx * 2)
        py = int(cy + math.sin(theta) * ry)
        
        if not (0 <= px < width and 0 <= py < height):
            continue
        
        if step_progress < progress:
            # Burnt - only show short trail
            dist_from_spark = progress - step_progress
            
            if dist_from_spark < 0.02:
                buffer.set_pixel(px, py, '█', z=-3, color=accent)
            elif dist_from_spark < 0.05:
                buffer.set_pixel(px, py, '▓', z=2, color=theme_manager.get_color_for_depth(3, 0, 10))
            elif dist_from_spark < 0.10:
                buffer.set_pixel(px, py, '░', z=5, color=theme_manager.get_color_for_depth(8, 0, 12))
            # else: disappeared
        else:
            # Unburnt
            buffer.set_pixel(px, py, '█', z=-5, color=theme_manager.get_color_for_depth(-5, -10, 0))
    
    # Spark glow
    buffer.set_pixel_with_glow(int(spark_x), int(spark_y), '✸', z=-10, color=accent,
                               glow_radius=2, theme_manager=theme_manager)
    
    # Time display
    time_str = now.strftime("%H:%M:%S")
    font = FONT_DIGITAL
    text_w = get_text_width(time_str, font)
    text_h = get_char_height(font)
    
    tx = cx - text_w // 2
    ty = cy - text_h // 2
    
    draw_text(buffer, tx, ty, time_str, font, accent, z=-15)
    
    # Countdown
    remaining = 60 - now.second
    countdown_str = f"{remaining:02d}s"
    countdown_x = cx - len(countdown_str) // 2
    countdown_y = cy + text_h // 2 + 2
    
    if countdown_y < height:
        for i, ch in enumerate(countdown_str):
            buffer.set_pixel(countdown_x + i, countdown_y, ch, z=-5, 
                           color=theme_manager.get_color_for_depth(-3, -5, 0))
    
    return (-15, 15)
