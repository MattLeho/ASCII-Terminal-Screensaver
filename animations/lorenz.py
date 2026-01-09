"""
Lorenz Attractor Animation
The famous "chaos butterfly" from chaos theory.
Enhanced with GLOWing comet head and safe scaling.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, project_point


# Lorenz system parameters
SIGMA = 10.0
RHO = 28.0
BETA = 8.0 / 3.0


class LorenzState:
    """Persistent state for the Lorenz attractor animation."""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = 0.1
        self.y = 0
        self.z = 0
        self.trail = []
        self.MAX_TRAIL = 1800  # Longer trail


_lorenz_state = LorenzState()


def render_lorenz(buffer, width, height, time, theme_manager):
    """
    Render the Lorenz attractor with GLOWing comet head.
    
    Features:
    - Glowing head (comet effect)
    - Gradient trails
    - Thick lines
    - Dynamic rotation
    """
    global _lorenz_state
    state = _lorenz_state
    
    # Reset if trail is empty
    if len(state.trail) == 0:
        state.reset()
        state.x = 0.1
        state.y = 0
        state.z = 0
    
    # Integration
    dt = 0.015
    
    for _ in range(30):
        dx = SIGMA * (state.y - state.x)
        dy = state.x * (RHO - state.z) - state.y
        dz = state.x * state.y - BETA * state.z
        
        state.x += dx * dt
        state.y += dy * dt
        state.z += dz * dt
        
        state.trail.append((state.x, state.y, state.z))
        
        if len(state.trail) > state.MAX_TRAIL:
            state.trail.pop(0)
    
    if not state.trail:
        return (0, 1)
    
    # Rotation
    rot_y = time * 0.4
    
    # Scale factor to bring Lorenz coords (~ -20..20) to nice model space (~ -2..2)
    # This prevents clipping when we used fixed scaling
    MODEL_SCALE = 0.08
    
    all_z = []
    points_to_draw = []
    
    for i, (x, y, z) in enumerate(state.trail):
        # Center the attractor (Z is 0..50, center at 25)
        centered_z = z - 25
        
        px = x * MODEL_SCALE
        py = y * MODEL_SCALE
        pz = centered_z * MODEL_SCALE
        
        point = rotate_y((px, py, pz), rot_y)
        point = rotate_x(point, 0.3)
        px, py, pz = point
        
        # Use default safe projection
        projected = project_point(px, py, pz, width, height)
        
        if projected:
            age = i / len(state.trail)  # 0.0 = tail, 1.0 = head
            all_z.append(pz)
            points_to_draw.append((projected[0], projected[1], pz, age))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    # Character ramp
    chars = " .:-=+*#%@█"
    
    # Draw trail
    for screen_x, screen_y, z, age in points_to_draw:
        # Determine visual properties based on age (tail fade)
        if age < 0.1: continue # Skip very old tail
        
        char_idx = int(age * (len(chars) - 1))
        char = chars[max(0, min(len(chars) - 1, char_idx))]
        
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        # The "Comet Head"
        if age > 0.98:
            # Bright glow for head
            buffer.set_pixel_with_glow(screen_x, screen_y, "●", z, theme_manager.get_accent(), glow_radius=2, theme_manager=theme_manager)
        else:
            # Regular trail
            buffer.set_pixel(screen_x, screen_y, char, z, color)
            
            # Thick trail for recent parts
            if age > 0.8:
                 buffer.set_pixel(screen_x + 1, screen_y, char, z + 0.01, color)

    return (z_min, z_max)
