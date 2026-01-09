"""
T-11: Planetary Clock
Solar System with colored planets orbiting the sun.
Enhanced: Vibrant RGB colors, thicker MEGA font, theme-colored time.
"""

import math
import random
from datetime import datetime
from ..utils.fonts import FONT_MEGA, draw_text, get_text_width, get_char_height

import sys
import os
# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from colors import fg_rgb


# Planet data: (name, orbit_ratio, size, speed, rgb_color)
# Colors bumped to be very vibrant
PLANETS = [
    ("Mercury", 1.0,  2, 4.0,   (180, 180, 180)),  # Gray
    ("Venus",   1.8,  3, 3.0,   (255, 160, 20)),   # Bright Orange
    ("Earth",   2.5,  3, 2.0,   (0, 100, 255)),    # Bright Blue
    ("Mars",    3.8,  3, 1.5,   (255, 30, 30)),    # Bright Red
    ("Jupiter", 7.0,  5, 0.7,   (255, 180, 100)),  # Peach/Orange
    ("Saturn",  10.0, 4, 0.4,   (255, 215, 0)),    # Gold
    ("Uranus",  15.0, 3, 0.25,  (0, 255, 255)),    # Cyan
    ("Neptune", 20.0, 3, 0.15,  (50, 100, 255)),   # Royal Blue
    ("Pluto",   25.0, 4, 0.08,  (180, 0, 255)),    # Bright Purple, Size 4
]


class Star:
    def __init__(self):
        self.x = random.uniform(0, 1)
        self.y = random.uniform(0, 1)
        self.phase = random.uniform(0, 6.28)
        self.speed = random.uniform(0.5, 2.5)
        self.char = random.choice(['.', '·', '*', '+'])
        # Star colors
        colors = [(255, 255, 255), (200, 220, 255), (255, 255, 200), (255, 220, 180)]
        self.color = random.choice(colors)


class PlanetaryState:
    def __init__(self):
        self.stars = [Star() for _ in range(100)]


_state = PlanetaryState()


def render(buffer, width, height, t, theme_manager):
    global _state
    
    now = datetime.now()
    
    cx = width // 2
    cy = height // 2
    
    # Calculate orbit scale to fill window
    margin_x = 6
    margin_y = 14  # More margin for top time
    available_w = (width - margin_x * 2) / 2
    available_h = (height - margin_y * 2)
    
    # Scale based on outermost planet (Pluto at ratio 25)
    max_orbit_ratio = 25.0
    scale_x = available_w / max_orbit_ratio
    scale_y = available_h / max_orbit_ratio
    orbit_scale = min(scale_x, scale_y)
    
    # Get a nice theme color for time (middle-bright part of gradient)
    # Ocean: Index 6-8 is nice bright blue/cyan
    grad_len = len(theme_manager.gradient)
    time_color_idx = int(grad_len * 0.7)  # 70% brightness
    time_color = theme_manager.gradient[time_color_idx]
    
    # 1. STARFIELD BACKGROUND
    for star in _state.stars:
        sx = int(star.x * width)
        sy = int(star.y * height)
        
        twinkle = math.sin(t * star.speed + star.phase)
        if twinkle > -0.3:
            char = star.char if twinkle > 0.5 else '.'
            r, g, b = star.color
            factor = 0.4 + twinkle * 0.4
            color = fg_rgb(int(r * factor), int(g * factor), int(b * factor))
            
            if 0 <= sx < width and 0 <= sy < height:
                buffer.set_pixel(sx, sy, char, z=25, color=color)
    
    # 2. SUN (Bright Yellow)
    sun_radius = max(2, int(orbit_scale * 0.4))
    sun_color = fg_rgb(255, 220, 0)
    
    for dy in range(-sun_radius, sun_radius + 1):
        for dx in range(-sun_radius * 2, sun_radius * 2 + 1):
            if (dx/2)**2 + dy**2 <= sun_radius**2:
                px = cx + dx
                py = cy + dy
                if 0 <= px < width and 0 <= py < height:
                    noise = math.sin(px * 0.3 + t * 2) * math.cos(py * 0.3 - t * 1.5)
                    char = '█' if noise > 0 else '▓'
                    buffer.set_pixel(px, py, char, z=5, color=sun_color)
    
    # 3. PLANETS WITH VIBRANT COLORS
    for name, orbit_ratio, size, speed, rgb_color in PLANETS:
        # Orbital angle
        if speed > 2.0:
            orbit_angle = -math.pi/2 + (now.second / 60) * 6.28 * speed
        elif speed > 0.5:
            orbit_angle = -math.pi/2 + (now.minute / 60) * 6.28 * speed
        else:
            orbit_angle = -math.pi/2 + (now.hour / 24) * 6.28 * speed
        
        orbit_angle += t * speed * 0.02
        
        orbit_r = orbit_ratio * orbit_scale
        px = cx + math.cos(orbit_angle) * orbit_r * 2
        py = cy + math.sin(orbit_angle) * orbit_r * 0.5
        pz = 10 + int(math.sin(orbit_angle) * 5)  # Behind time (z > 0)
        
        # Orbit path (dimly colored)
        r, g, b = rgb_color
        orbit_color = fg_rgb(r // 4, g // 4, b // 4)
        for i in range(0, 360, 8):
            th = math.radians(i)
            ox = int(cx + math.cos(th) * orbit_r * 2)
            oy = int(cy + math.sin(th) * orbit_r * 0.5)
            if 0 <= ox < width and 0 <= oy < height:
                buffer.set_pixel(ox, oy, '·', z=20, color=orbit_color)
        
        # Planet body
        planet_color = fg_rgb(r, g, b)
        half = size // 2
        
        for dy in range(-half, half + 1):
            for dx in range(-half * 2, half * 2 + 1):
                if (dx/2)**2 + dy**2 <= half**2 + 0.5:
                    ppx = int(px) + dx
                    ppy = int(py) + dy
                    if 0 <= ppx < width and 0 <= ppy < height:
                        # Lighting effect: simple single-source
                        lit = dx < 0
                        
                        if lit:
                            char = '█'
                            draw_color = planet_color
                        else:
                            char = '▓'
                            # Darker color for shadow
                            draw_color = fg_rgb(r // 2, g // 2, b // 2)
                        
                        buffer.set_pixel(ppx, ppy, char, z=pz, color=draw_color)
        
        # Saturn's rings
        if name == "Saturn":
            ring_color = fg_rgb(200, 180, 100)
            for ring_dx in range(-size - 3, size + 4):
                ring_x = int(px) + ring_dx
                if abs(ring_dx) > size and 0 <= ring_x < width:
                    buffer.set_pixel(ring_x, int(py), '─', z=pz + 1, color=ring_color)
        
        # Planet label
        label_x = int(px) + half + 2
        if 0 <= label_x < width and 0 <= int(py) < height:
            buffer.set_pixel(label_x, int(py), name[0], z=pz - 1, color=planet_color)
    
    # 4. TIME DISPLAY (Thick MEGA font, THEME COLORED, IN FRONT)
    font = FONT_MEGA
    full_time = now.strftime("%H:%M:%S")
    text_w = get_text_width(full_time, font)
    
    disp_x = (width - text_w) // 2
    disp_y = 3
    
    # Use calculated theme color (not accent) so it matches (e.g. Blue for Ocean)
    draw_text(buffer, disp_x, disp_y, full_time, font, time_color, z=-30)
    
    return (-30, 30)
