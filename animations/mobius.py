"""
Möbius Strip Animation
A surface with only one side and one edge.
Enhanced with edge highlighting to show the twist clearly.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


def render_mobius(buffer, width, height, time, theme_manager):
    """
    Render a rotating Möbius strip with highlighted edges.
    """
    # Möbius strip parameters 
    RADIUS = 2.2
    
    rot_x = time * 0.5
    rot_z = time * 0.3
    
    u_steps = 100 # Increased density
    v_steps = 20
    
    all_z = []
    points_to_draw = []
    
    for i in range(u_steps):
        u = 2 * math.pi * i / u_steps
        
        for j in range(v_steps):
            v = -1 + 2 * j / (v_steps - 1)
            
            # Parametric Mobius
            half_u = u / 2
            cos_half_u = math.cos(half_u)
            sin_half_u = math.sin(half_u)
            
            tmp = (1 + (v / 2.0) * cos_half_u)
            
            x = RADIUS * tmp * math.cos(u)
            y = RADIUS * tmp * math.sin(u)
            z = RADIUS * (v / 2.0) * sin_half_u
            
            point = rotate_x((x, y, z), rot_x)
            point = rotate_z(point, rot_z)
            x, y, z = point
            
            # Uses safe scaling
            projected = project_point(x, y, z, width, height)
            if projected:
                # Edge detection
                is_edge = abs(v) > 0.8
                all_z.append(z)
                points_to_draw.append((projected[0], projected[1], z, is_edge))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    surface_chars = " .:-=+"
    
    for screen_x, screen_y, z, is_edge in points_to_draw:
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        if is_edge:
            # Thick Edge
            char = '█'
            buffer.set_pixel_with_glow(screen_x, screen_y, char, z, theme_manager.get_accent(), glow_radius=1, theme_manager=theme_manager)
        else:
            # Surface
            z_norm = (z - z_min) / (z_max - z_min) if z_max != z_min else 0.5
            idx = int(z_norm * (len(surface_chars) - 1))
            char = surface_chars[max(0, min(len(surface_chars) - 1, idx))]
            buffer.set_pixel(screen_x, screen_y, char, z, color)
    
    return (z_min, z_max)
