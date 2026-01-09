"""
Lissajous Knots Animation
Complex 3D curves from oscillating frequencies.
Enhanced with THICK connected curves and safe scaling.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, project_point


def render_lissajous(buffer, width, height, time, theme_manager):
    """
    Render a Lissajous knot with THICK curves.
    """
    # Fixed Scale
    SCALE = 2.8
    
    # Morphing parameters
    a = 3 + 0.5 * math.sin(time * 0.1)
    b = 2 + 0.3 * math.cos(time * 0.15)
    c = 5 + 0.4 * math.sin(time * 0.08)
    delta = time * 0.5
    
    rot_y = time * 0.4
    rot_x = 0.5 + math.sin(time * 0.2) * 0.2
    
    num_points = 200 # Lower point count if connecting lines
    
    points = []
    
    # Generate points
    for i in range(num_points + 1):
        t = 2 * math.pi * i / num_points
        
        x = math.sin(a * t + delta) * SCALE
        y = math.sin(b * t) * SCALE
        z = math.sin(c * t) * SCALE
        
        point = rotate_y((x, y, z), rot_y)
        point = rotate_x(point, rot_x)
        points.append(point)

    if not points:
        return (0, 1)

    z_vals = [p[2] for p in points]
    z_min, z_max = min(z_vals), max(z_vals)
    
    # Draw connected thick lines
    for i in range(len(points) - 1):
        p1 = points[i]
        p2 = points[i+1]
        
        proj1 = project_point(p1[0], p1[1], p1[2], width, height)
        proj2 = project_point(p2[0], p2[1], p2[2], width, height)
        
        if proj1 and proj2:
            avg_z = (p1[2] + p2[2]) / 2
            
            # Use thickness 2 for closer parts
            thickness = 2 if avg_z < 0 else 1
            char = "█" if thickness > 1 else "≡"
            color = theme_manager.get_color_for_depth(avg_z, z_min, z_max)
            
            buffer.draw_thick_line(proj1[0], proj1[1], proj2[0], proj2[1], char, avg_z, color, thickness=thickness)

    # Add some glow markers along the curve
    for i in range(0, len(points), 20):
        p = points[i]
        proj = project_point(p[0], p[1], p[2], width, height)
        if proj:
            buffer.set_pixel_with_glow(proj[0], proj[1], "@", p[2]-0.1, theme_manager.get_accent(), glow_radius=1, theme_manager=theme_manager)

    return (z_min, z_max)
