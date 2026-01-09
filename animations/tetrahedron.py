"""
Tetrahedron Animation
A rotating 4-sided pyramid wireframe.
Enhanced with THICK edges and safe scaling.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


# Regular Tetrahedron geometry (Normalized)
SQRT2 = math.sqrt(2)
VERTICES = [
    (1, 0, -1/SQRT2),
    (-1, 0, -1/SQRT2),
    (0, 1, 1/SQRT2),
    (0, -1, 1/SQRT2)
]
EDGES = [
    (0, 1), (0, 2), (0, 3),
    (1, 2), (1, 3),
    (2, 3)
]


def render_tetrahedron(buffer, width, height, time, theme_manager):
    """
    Render a rotating tetrahedron with THICK edges.
    """
    # Fixed model scale
    SCALE = 4.0
    
    rot_x = time * 1.0
    rot_z = time * 0.7

    transformed = []
    for v in VERTICES:
        p = (v[0] * SCALE, v[1] * SCALE, v[2] * SCALE)
        p = rotate_x(p, rot_x)
        p = rotate_z(p, rot_z)
        transformed.append(p)
    
    z_vals = [t[2] for t in transformed]
    z_min, z_max = min(z_vals), max(z_vals)
    
    # Draw Edges (Thick)
    for edge in EDGES:
        p1 = transformed[edge[0]]
        p2 = transformed[edge[1]]
        
        proj1 = project_point(p1[0], p1[1], p1[2], width, height)
        proj2 = project_point(p2[0], p2[1], p2[2], width, height)
        
        if proj1 and proj2:
            sx1, sy1 = proj1
            sx2, sy2 = proj2
            
            avg_z = (p1[2] + p2[2]) / 2
            color = theme_manager.get_color_for_depth(avg_z, z_min, z_max)
            
            # Thick lines
            buffer.draw_thick_line(sx1, sy1, sx2, sy2, "█", avg_z, color, thickness=2)
    
    # Bright vertices with Glow
    for t in transformed:
        proj = project_point(t[0], t[1], t[2], width, height)
        if proj:
            sx, sy = proj
            color = theme_manager.get_color_for_depth(t[2], z_min, z_max)
            # Big glowing vertex
            buffer.set_pixel_with_glow(sx, sy, "●", t[2] - 0.2, theme_manager.get_accent(), glow_radius=2, theme_manager=theme_manager)

    return (z_min, z_max)
