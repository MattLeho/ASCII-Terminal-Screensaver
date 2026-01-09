"""
Sine Wave Grid Animation
A rippling water surface effect.
Enhanced with larger scale and more dynamic waves.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, project_point


def render_wave_grid(buffer, width, height, time, theme_manager):
    """
    Render a grid of points that ripple like water.
    
    Features:
    - Multiple wave sources with interference
    - Continuous wave animation
    - Rotating view
    """
    # Grid parameters - LARGER
    grid_size = 35
    grid_spacing = 0.28
    wave_amplitude = 0.8
    wave_frequency = 1.8
    
    # Rotation for 3D view (tilted view of the surface)
    rot_x = 0.85  # Tilt to see the surface
    rot_y = time * 0.25  # Slow continuous rotation
    
    all_z = []
    points_to_draw = []
    
    # Wave sources (animated positions for dynamic effect)
    sources = [
        (0, 0, 1.0, 0),                                    # Center
        (3 * math.sin(time * 0.3), 3 * math.cos(time * 0.3), 0.6, math.pi/4),  # Orbiting
        (-3, -3, 0.5, math.pi/2),                          # Corner
    ]
    
    for i in range(grid_size):
        for j in range(grid_size):
            # Grid position (centered)
            gx = (i - grid_size / 2) * grid_spacing
            gy = (j - grid_size / 2) * grid_spacing
            
            # Calculate height from multiple wave sources
            gz = 0
            for sx, sy, amp, phase in sources:
                distance = math.sqrt((gx - sx) ** 2 + (gy - sy) ** 2)
                gz += amp * math.sin(distance * wave_frequency - time * 2.5 + phase)
            
            gz *= wave_amplitude / len(sources)
            
            # Swap y and z for proper visualization (grid is horizontal)
            x = gx
            y = gz  # Height becomes y
            z = gy  # Depth
            
            # Apply rotations
            point = rotate_x((x, y, z), rot_x)
            point = rotate_y(point, rot_y)
            x, y, z = point
            
            projected = project_point(x, y, z, width, height, distance=5.0)
            if projected:
                all_z.append(z)
                # Store original height for character selection
                points_to_draw.append((projected[0], projected[1], z, gz))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    # Height-based characters
    wave_chars = "~-=+*#@"
    
    # Get height range for character selection
    heights = [p[3] for p in points_to_draw]
    if heights:
        h_min, h_max = min(heights), max(heights)
    else:
        h_min, h_max = -1, 1
    
    for screen_x, screen_y, z, gz in points_to_draw:
        # Character based on wave height
        if h_max != h_min:
            h_normalized = (gz - h_min) / (h_max - h_min)
        else:
            h_normalized = 0.5
        
        char_idx = int(h_normalized * (len(wave_chars) - 1))
        char = wave_chars[max(0, min(len(wave_chars) - 1, char_idx))]
        
        # Color based on depth
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        buffer.set_pixel(screen_x, screen_y, char, z, color)
    
    return (z_min, z_max)
