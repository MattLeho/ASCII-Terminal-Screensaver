"""
T-01: Gravity Clock
Floating digits with physics, particle sparks, trails, and variable gravity.
Enhanced: Motion blur trails, better collisions, ambient particles.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_DIGITAL, draw_text, get_text_width, get_char_height


class Particle:
    def __init__(self, x, y, vx, vy, life, char, color):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.char = char
        self.color = color


class DigitBody:
    def __init__(self, char, x, y, home_x):
        self.char = char
        self.x = float(x)
        self.y = float(y)
        self.home_x = float(home_x)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(-0.3, 0.3)
        self.trail = []  # (x, y, age)
        self.rotation = random.uniform(0, 6.28)
        self.spin = random.uniform(-0.1, 0.1)


class GravityState:
    def __init__(self):
        self.digits = {}
        self.particles = []
        self.ambient = []
        self.last_time = ""
        self.initialized = False


_state = GravityState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    time_str = now.strftime("%H:%M:%S") if width > 50 else now.strftime("%H:%M")
    
    if not _state.initialized or time_str != _state.last_time:
        _update_digits(time_str, width, height)
        _state.last_time = time_str
        _state.initialized = True
    
    # Ambient floating particles
    if len(_state.ambient) < 20:
        _state.ambient.append(Particle(
            random.uniform(0, width), random.uniform(0, height),
            random.uniform(-0.2, 0.2), random.uniform(-0.2, 0.2),
            random.uniform(2, 5), '·', None
        ))
    
    # Variable gravity
    gx = math.sin(t * 0.4) * 0.03
    gy = math.cos(t * 0.25) * 0.03
    
    accent = theme_manager.get_accent()
    
    # Physics update
    for key, digit in _state.digits.items():
        # Trail
        digit.trail.append((digit.x, digit.y, 0))
        digit.trail = [(x, y, age + 1) for x, y, age in digit.trail if age < 8]
        
        # Forces
        digit.vx += gx
        digit.vy += gy
        
        # Tether spring
        digit.vx -= (digit.x - digit.home_x) * 0.003
        
        # Damping
        digit.vx *= 0.995
        digit.vy *= 0.995
        
        digit.x += digit.vx
        digit.y += digit.vy
        digit.rotation += digit.spin
        
        # Walls
        char_w, char_h = 6, 7
        if digit.x < 1:
            digit.x = 1; digit.vx = abs(digit.vx) * 0.8
            _spawn_sparks(digit.x, digit.y + 3, 4, accent)
        elif digit.x > width - char_w:
            digit.x = width - char_w; digit.vx = -abs(digit.vx) * 0.8
            _spawn_sparks(digit.x + char_w, digit.y + 3, 4, accent)
        if digit.y < 1:
            digit.y = 1; digit.vy = abs(digit.vy) * 0.8
            _spawn_sparks(digit.x + 3, digit.y, 4, accent)
        elif digit.y > height - char_h:
            digit.y = height - char_h; digit.vy = -abs(digit.vy) * 0.8
            _spawn_sparks(digit.x + 3, digit.y + char_h, 4, accent)
    
    # Inter-digit collisions
    keys = list(_state.digits.keys())
    for i, k1 in enumerate(keys):
        for k2 in keys[i+1:]:
            d1, d2 = _state.digits[k1], _state.digits[k2]
            dx = d2.x - d1.x
            dy = d2.y - d1.y
            dist = math.sqrt(dx*dx + dy*dy) + 0.1
            if dist < 8:
                nx, ny = dx/dist, dy/dist
                overlap = (8 - dist) / 2
                d1.x -= nx * overlap
                d1.y -= ny * overlap
                d2.x += nx * overlap
                d2.y += ny * overlap
                # Momentum exchange
                d1.vx, d2.vx = d2.vx * 0.9, d1.vx * 0.9
                d1.vy, d2.vy = d2.vy * 0.9, d1.vy * 0.9
                _spawn_sparks((d1.x + d2.x)/2 + 3, (d1.y + d2.y)/2 + 3, 3, accent)
    
    # Update particles
    active = []
    for p in _state.particles:
        p.x += p.vx
        p.y += p.vy
        p.vy += 0.1
        p.life -= 0.1
        if p.life > 0 and 0 <= p.x < width and 0 <= p.y < height:
            active.append(p)
            char = '*' if p.life > 0.5 else '·'
            buffer.set_pixel(int(p.x), int(p.y), char, z=5, color=p.color)
    _state.particles = active
    
    # Update ambient
    active_amb = []
    for p in _state.ambient:
        p.x += p.vx + math.sin(t + p.y) * 0.1
        p.y += p.vy
        p.life -= 0.02
        if p.life > 0:
            if p.x < 0: p.x = width
            elif p.x >= width: p.x = 0
            if p.y < 0: p.y = height
            elif p.y >= height: p.y = 0
            active_amb.append(p)
            buffer.set_pixel(int(p.x), int(p.y), '·', z=15, color=theme_manager.get_color_for_depth(15, 0, 20))
    _state.ambient = active_amb
    
    # Render digits with trails
    for key, digit in _state.digits.items():
        # Trail (motion blur)
        for tx, ty, age in digit.trail:
            alpha = 1.0 - age / 8
            if alpha > 0.2:
                trail_color = theme_manager.get_color_for_depth(int(age * 2), 0, 15)
                char = '░' if age > 4 else '▒'
                for dy in range(7):
                    for dx in range(6):
                        buffer.set_pixel(int(tx) + dx, int(ty) + dy, char, z=10 + age, color=trail_color)
        
        # Main digit
        if digit.char in FONT_DIGITAL:
            draw_text(buffer, int(digit.x), int(digit.y), digit.char, FONT_DIGITAL, accent, z=-5)
    
    return (-5, 20)


def _update_digits(time_str, width, height):
    global _state
    new_digits = {}
    char_w = 7
    total_w = len(time_str) * char_w
    start_x = (width - total_w) // 2
    
    for i, char in enumerate(time_str):
        key = f"d{i}"
        home_x = start_x + i * char_w
        if key in _state.digits and _state.digits[key].char == char:
            new_digits[key] = _state.digits[key]
            new_digits[key].home_x = home_x
        else:
            new_digits[key] = DigitBody(char, home_x, height // 2, home_x)
    _state.digits = new_digits


def _spawn_sparks(x, y, count, color):
    for _ in range(count):
        _state.particles.append(Particle(
            x, y,
            random.uniform(-1.5, 1.5), random.uniform(-2, 0),
            random.uniform(0.5, 1.0), '*', color
        ))
