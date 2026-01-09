"""
Klein Bottle Animation
A 4D shape that passes through itself when projected to 3D.
Enhanced with larger scale and better visibility.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


def render_klein(buffer, width, height, time, theme_manager):
    """
    Render a rotating Klein bottle.
    
    Features:
    - Continuous rotation on all axes
    - Larger scale for visibility
    - Depth-based shading
    """
    # Parameters - LARGER scale
    scale = 1.6
    
    # Continuous rotation on multiple axes
    rot_y = time * 0.5
    rot_x = time * 0.3 + 0.3
    rot_z = time * 0.2
    
    all_z = []
    points_to_draw = []
    
    # Higher resolution for smoother appearance
    u_steps = 60
    v_steps = 30
    
    for i in range(u_steps):
        u = 2 * math.pi * i / u_steps
        
        for j in range(v_steps):
            v = 2 * math.pi * j / v_steps
            
            # Klein bottle "figure-8" parametric equations
            cos_u = math.cos(u)
            sin_u = math.sin(u)
            cos_v = math.cos(v)
            sin_v = math.sin(v)
            
            # Modified Klein bottle equations for better visualization
            r = 4 * (1 - cos_u / 2)
            
            if u < math.pi:
                x = 6 * cos_u * (1 + sin_u) + r * cos_u * cos_v
                y = 16 * sin_u + r * sin_u * cos_v
            else:
                x = 6 * cos_u * (1 + sin_u) + r * cos_v * math.cos(u - math.pi)
                y = 16 * sin_u
            
            z = r * sin_v
            
            # Scale down but larger than before
            x *= 0.10 * scale
            y *= 0.10 * scale
            z *= 0.10 * scale
            
            # Center vertically
            y -= 0.6
            
            # Apply rotations for continuous movement
            point = rotate_z((x, y, z), rot_z)
            point = rotate_y(point, rot_y)
            point = rotate_x(point, rot_x)
            x, y, z = point
            
            projected = project_point(x, y, z, width, height, distance=4.5)
            if projected:
                all_z.append(z)
                points_to_draw.append((projected[0], projected[1], z))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    chars = " .:-=+*#%@"
    
    for screen_x, screen_y, z in points_to_draw:
        char, color = theme_manager.get_char_for_depth(z, z_min, z_max, chars)
        buffer.set_pixel(screen_x, screen_y, char, z, color)
    
    return (z_min, z_max)
