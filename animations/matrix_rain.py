"""
Matrix Rain 3D Animation
Falling characters in a 3D tunnel effect.
Enhanced with denser rain and better trail effects.
"""

import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import project_point


class MatrixRainState:
    """Persistent state for matrix rain."""
    def __init__(self):
        self.drops = []
        self.initialized = False


_matrix_state = MatrixRainState()


def render_matrix_rain(buffer, width, height, time, theme_manager):
    """
    Render 3D matrix-style falling characters.
    
    Features:
    - Characters fall in 3D space continuously
    - Trail effect with fading
    - Denser rain for better effect
    """
    global _matrix_state
    state = _matrix_state
    
    # Matrix characters
    ascii_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    # Initialize drops - MORE for denser rain
    if not state.initialized or len(state.drops) < 200:
        state.drops = []
        for _ in range(200):
            state.drops.append({
                'x': random.uniform(-4, 4),
                'y': random.uniform(-5, 5),
                'z': random.uniform(0, 12),
                'speed': random.uniform(0.08, 0.18),
                'char': random.choice(ascii_chars),
                'change_rate': random.randint(2, 8),
                'frame': 0,
            })
        state.initialized = True
    
    all_z = []
    points_to_draw = []
    
    # Update and draw drops
    for drop in state.drops:
        # Move drop toward camera continuously
        drop['z'] -= drop['speed']
        drop['frame'] += 1
        
        # Change character occasionally
        if drop['frame'] % drop['change_rate'] == 0:
            drop['char'] = random.choice(ascii_chars)
        
        # Reset if passed camera
        if drop['z'] < 0.3:
            drop['z'] = random.uniform(10, 14)
            drop['x'] = random.uniform(-4, 4)
            drop['y'] = random.uniform(-5, 5)
            drop['speed'] = random.uniform(0.08, 0.18)
        
        # Project to screen
        projected = project_point(drop['x'], drop['y'], drop['z'], width, height, distance=1.5)
        if projected:
            all_z.append(drop['z'])
            points_to_draw.append((
                projected[0], projected[1], 
                drop['z'], drop['char'], True  # True = main drop
            ))
    
    # Add trail effect - ghost characters behind main drops
    for drop in state.drops:
        for trail in range(4):
            trail_z = drop['z'] + (trail + 1) * 0.35
            if trail_z < 14:
                projected = project_point(drop['x'], drop['y'], trail_z, width, height, distance=1.5)
                if projected:
                    all_z.append(trail_z)
                    # Dimmer characters for trail
                    if trail == 0:
                        trail_char = ':'
                    elif trail == 1:
                        trail_char = '.'
                    else:
                        trail_char = ' '
                    points_to_draw.append((
                        projected[0], projected[1],
                        trail_z, trail_char, False  # False = trail
                    ))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    for screen_x, screen_y, z, char, is_main in points_to_draw:
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        buffer.set_pixel(screen_x, screen_y, char, z, color)
    
    return (z_min, z_max)
