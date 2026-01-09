"""
Wireframe Sphere Animation
A rotating globe with latitude and longitude lines.
Enhanced with THICK connected lines and safe scaling.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


def render_sphere(buffer, width, height, time, theme_manager):
    """
    Render a wireframe sphere with thick connected lines.
    """
    # Fixed Radius
    RADIUS = 3.2
    
    # Rotation angles
    rot_y = time * 0.4
    rot_x = math.sin(time * 0.2) * 0.4  # Tilt
    rot_z = math.sin(time * 0.3) * 0.1
    
    # Generate geometry for lines
    # We will generate vertices and transform them, then draw lines
    
    # 1. Longitude Lines (Vertical)
    num_long = 12
    points_per_long = 18
    
    for i in range(num_long):
        theta = (2 * math.pi * i) / num_long
        
        # Line strip for longitude
        strip = []
        for j in range(points_per_long):
            phi = (math.pi * j) / (points_per_long - 1)
            
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.cos(phi)
            z = RADIUS * math.sin(phi) * math.sin(theta)
            
            p = rotate_z(rotate_x(rotate_y((x,y,z), rot_y), rot_x), rot_z)
            strip.append(p)
            
        # Draw strip using thick lines
        for k in range(len(strip) - 1):
            p1 = strip[k]
            p2 = strip[k+1]
            draw_thick_segment(buffer, width, height, p1, p2, theme_manager, RADIUS)

    # 2. Latitude Lines (Horizontal)
    num_lat = 8
    points_per_lat = 24
    
    for i in range(1, num_lat):
        phi = (math.pi * i) / num_lat
        current_rad = RADIUS * math.sin(phi)
        y_pos = RADIUS * math.cos(phi)
        
        strip = []
        for j in range(points_per_lat + 1): # +1 to close loop
            theta = (2 * math.pi * j) / points_per_lat
            x = current_rad * math.cos(theta)
            y = y_pos
            z = current_rad * math.sin(theta)
            
            p = rotate_z(rotate_x(rotate_y((x,y,z), rot_y), rot_x), rot_z)
            strip.append(p)
            
        for k in range(len(strip) - 1):
            p1 = strip[k]
            p2 = strip[k+1]
            draw_thick_segment(buffer, width, height, p1, p2, theme_manager, RADIUS)

    return (-RADIUS, RADIUS)

def draw_thick_segment(buffer, width, height, p1, p2, theme_manager, radius):
    """Helper to draw a thick line segment."""
    proj1 = project_point(p1[0], p1[1], p1[2], width, height)
    proj2 = project_point(p2[0], p2[1], p2[2], width, height)
    
    if proj1 and proj2:
        sx1, sy1 = proj1
        sx2, sy2 = proj2
        
        avg_z = (p1[2] + p2[2]) / 2
        color = theme_manager.get_color_for_depth(avg_z, -radius, radius)
        
        # Thickness based on depth
        thickness = 2 if avg_z < 0 else 1
        char = "█" if thickness > 1 else "≡"
        
        # Don't draw too thick for sphere network or it gets messy
        # Just use subpixel or single thickness for far, double for near
        if thickness > 1:
             buffer.draw_thick_line(sx1, sy1, sx2, sy2, char, avg_z, color, thickness=2)
        else:
             buffer.draw_line_subpixel(sx1, sy1, sx2, sy2, avg_z, color)
