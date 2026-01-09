"""
Rose Curves (3D) Animation
Mathematical flower patterns in 3D space.
Enhanced with THICK connected lines and safe scaling.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


def render_rose(buffer, width, height, time, theme_manager):
    """
    Render 3D rose curves with thick connected lines.
    """
    # Animate k for morphing petals
    k = 3 + 2 * math.sin(time * 0.2)
    
    # Larger fixed scale
    SCALE = 2.8
    height_scale = 0.8
    
    rot_z = time * 0.6
    rot_x = 0.9 + 0.2 * math.sin(time * 0.3)
    
    num_curves = 6
    points_per_curve = 100 # Lower density for connected lines
    
    all_z = []
    
    for curve in range(num_curves):
        # Each curve at different phase and height
        phase = curve * math.pi / num_curves
        base_z = (curve - num_curves / 2) * height_scale * 0.4
        
        curve_points = []
        
        # Generate points for this petal layer
        for i in range(points_per_curve + 1):
            theta = 2 * math.pi * i / points_per_curve * (k if k == int(k) else 4)
            
            # Rose curve equation
            r = math.cos(k * theta + phase + time) * SCALE
            
            # Convert to Cartesian
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            z = base_z + 0.4 * math.sin(theta * 3 + time * 2)
            
            # Apply rotations
            point = rotate_z((x, y, z), rot_z)
            point = rotate_x(point, rot_x)
            
            curve_points.append(point)
            all_z.append(point[2])
            
        # Draw this petal layer as connected lines
        for i in range(len(curve_points) - 1):
            p1 = curve_points[i]
            p2 = curve_points[i+1]
            
            # Skip if r was very small (center clutter)
            # Actually with lines it looks okay, like a flower center
            
            proj1 = project_point(p1[0], p1[1], p1[2], width, height)
            proj2 = project_point(p2[0], p2[1], p2[2], width, height)
            
            if proj1 and proj2:
                avg_z = (p1[2] + p2[2]) / 2
                color = theme_manager.get_color_for_depth(avg_z, -2, 2)
                
                # Bloom effect on tips (further from center)
                dist_from_center = math.sqrt(p1[0]**2 + p1[1]**2)
                
                # Thickness
                thick = 2 if avg_z < 0 and dist_from_center > 1.0 else 1
                char = "█" if thick > 1 else "*"
                
                buffer.draw_thick_line(proj1[0], proj1[1], proj2[0], proj2[1], char, avg_z, color, thickness=thick)

    # Draw Center Stem (Thick)
    stem_top = rotate_x((0, 0, 1.5), rot_x)
    stem_bottom = rotate_x((0, 0, -1.5), rot_x)
    
    p1 = project_point(stem_top[0], stem_top[1], stem_top[2], width, height)
    p2 = project_point(stem_bottom[0], stem_bottom[1], stem_bottom[2], width, height)
    
    if p1 and p2:
        buffer.draw_thick_line(p1[0], p1[1], p2[0], p2[1], "|", 0, theme_manager.get_accent(), thickness=2)

    if not all_z:
        return (0, 1)
    return (min(all_z), max(all_z))
