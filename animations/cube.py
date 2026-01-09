"""
Rotating Cube Animation
A 3D wireframe cube rotating on all axes.
Enhanced with THICK edges and safe scaling.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


# Cube Geometry (Normalized size 1)
VERTICES = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
]
EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # Back Face
    (4, 5), (5, 6), (6, 7), (7, 4),  # Front Face
    (0, 4), (1, 5), (2, 6), (3, 7)   # Connecting Edges
]


def render_cube(buffer, width, height, time, theme_manager):
    """
    Render a rotating wireframe cube with THICK edges.
    """
    # Fixed model scale - let engine handle terminal scaling
    SCALE = 3.5 
    
    # Rotation
    rot_x = time * 0.8
    rot_y = time * 0.6
    rot_z = time * 0.3

    # Transform vertices
    transformed = []
    for v in VERTICES:
        x, y, z = v[0] * SCALE, v[1] * SCALE, v[2] * SCALE
        point = rotate_x((x, y, z), rot_x)
        point = rotate_y(point, rot_y)
        point = rotate_z(point, rot_z)
        transformed.append(point)

    z_vals = [t[2] for t in transformed]
    z_min, z_max = min(z_vals), max(z_vals)
    
    # Create Z range for depth coloring
    z_range = z_max - z_min
    if z_range < 0.1: z_range = 1.0
    
    # Draw Edges (Thick)
    for edge in EDGES:
        p1 = transformed[edge[0]]
        p2 = transformed[edge[1]]
        
        proj1 = project_point(p1[0], p1[1], p1[2], width, height)
        proj2 = project_point(p2[0], p2[1], p2[2], width, height)
        
        if not proj1 or not proj2:
            continue
        
        sx1, sy1 = proj1
        sx2, sy2 = proj2
        
        avg_z = (p1[2] + p2[2]) / 2
        color = theme_manager.get_color_for_depth(avg_z, z_min, z_max)
        
        # Thicker lines for front edges (closer z)
        thickness = 2 if avg_z < 0 else 1
        
        # Use box drawing chars for cleaner lines if simple chars requested
        # But theme manager handles chars. We'll use a solid block for structure.
        char = "█" if thickness > 1 else "≡"
        
        buffer.draw_thick_line(sx1, sy1, sx2, sy2, char, avg_z, color, thickness=2)

    # Draw Vertices (Glowing)
    for p in transformed:
        proj = project_point(p[0], p[1], p[2], width, height)
        if proj:
            sx, sy = proj
            color = theme_manager.get_color_for_depth(p[2], z_min, z_max)
            # Big glowing vertex
            buffer.set_pixel_with_glow(sx, sy, "●", p[2] - 0.2, theme_manager.get_accent(), glow_radius=2, theme_manager=theme_manager)

    return (z_min, z_max)
