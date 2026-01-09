"""
Starfield / Warp Speed Animation
Flying through space at high speed.
Enhanced with GLOW, lens flares, and warp streaks.
"""

import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import project_point


class StarfieldState:
    """Persistent state for starfield."""
    def __init__(self):
        self.stars = []
        self.initialized = False


_starfield_state = StarfieldState()


def render_starfield(buffer, width, height, time, theme_manager):
    """
    Render a starfield with GLOW and warp speed effect.
    
    Features:
    - Glowing stars (pseudo-HDR bloom)
    - Warp streaks for motion blur
    - Pulsing acceleration
    - Dense star clusters
    """
    global _starfield_state
    state = _starfield_state
    
    num_stars = 300
    max_z = 25
    min_z = 0.5
    
    # Initialize stars
    if not state.initialized or len(state.stars) < num_stars:
        state.stars = []
        for _ in range(num_stars):
            state.stars.append({
                'x': random.uniform(-10, 10),
                'y': random.uniform(-8, 8),
                'z': random.uniform(min_z, max_z),
            })
        state.initialized = True
    
    # Speed with pulsing warp effect
    base_speed = 0.5
    # Sine wave acceleration for "warp pulses"
    speed = base_speed * (1 + 0.6 * math.sin(time * 0.6))
    
    all_z = []
    points_to_draw = []
    streaks_to_draw = []
    
    for star in state.stars:
        # Store previous position for streaks
        prev_z = star['z']
        prev_proj = project_point(star['x'], star['y'], prev_z, width, height, distance=1.0)
        
        # Move star toward camera
        star['z'] -= speed
        
        # Reset if past camera
        if star['z'] < min_z:
            star['z'] += max_z
            # Randomize XY again to avoid tunneling patterns (or keep for tunnel effect)
            star['x'] = random.uniform(-10, 10)
            star['y'] = random.uniform(-8, 8)
            prev_proj = None # Don't draw streak across screen on reset
        
        # Project to screen
        projected = project_point(star['x'], star['y'], star['z'], width, height, distance=1.0)
        
        if projected:
            all_z.append(star['z'])
            
            # If we had a previous valid projection, draw motion streak
            if prev_proj and star['z'] < max_z * 0.8:
                streaks_to_draw.append((
                    prev_proj[0], prev_proj[1],
                    projected[0], projected[1],
                    star['z']
                ))
            
            points_to_draw.append((projected[0], projected[1], star['z']))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    # Draw streaks (motion blur)
    for x1, y1, x2, y2, z in streaks_to_draw:
        # Number of steps proportional to length
        dist_sq = (x2-x1)**2 + (y2-y1)**2
        steps = min(int(math.sqrt(dist_sq)), 30)
        if steps < 1: steps = 1

        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        for i in range(steps):
            t = i / steps
            sx = int(x1 + (x2 - x1) * t)
            sy = int(y1 + (y2 - y1) * t)
            
            # Fading trail
            trail_char = '.' if i % 2 == 0 else ' '
            if z < 5: trail_char = '-'
            
            buffer.set_pixel(sx, sy, trail_char, z + 0.1, color)

    # Draw stars with GLOW
    for sx, sy, z in points_to_draw:
        # Normalized depth (0 = close, 1 = far)
        z_norm = (z - z_min) / (z_max - z_min + 0.001)
        z_norm = max(0, min(1, z_norm))
        
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        # Close stars get big sprites and glow
        if z < 4.0:
            char = "★" if z < 2.0 else "*"
            # Intense glow for very close stars
            glow_rad = 2 if z < 2.0 else 1
            buffer.set_pixel_with_glow(sx, sy, char, z, color, glow_radius=glow_rad, theme_manager=theme_manager)
            
        elif z < 10.0:
            char = "+"
            buffer.set_pixel(sx, sy, char, z, color)
        
        else:
            char = "."
            buffer.set_pixel(sx, sy, char, z, color)

    return (z_min, z_max)
