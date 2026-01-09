"""
DNA Double Helix Animation
Two intertwined helical strands with connecting base pairs.
Enhanced with GLOW, bloom effects, and infinite scroll illusion.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


def render_helix(buffer, width, height, time, theme_manager):
    """
    Render a DNA double helix animation with GLOW and BLOOM.
    
    Features:
    - Glowing base pairs (pseudo-HDR)
    - Bloom effect on strands
    - Thick, robust structure
    - Infinite vertical scroll
    """
    # DNA Physical Parameters (Model Space)
    # Scaled down slightly to ensure it fits with new safer projection
    STRAND_RADIUS = 2.0
    HELIX_HEIGHT = 14.0
    
    # Increase step count for smoother, denser strands
    STRAND_LENGTH_STEPS = 80
    TWIST_TIGHTNESS = 3.0
    
    # Animation Variables
    rotation_speed = time * 0.8
    wobble_angle = math.sin(time * 0.5) * 0.2
    
    scroll_offset = (time * 2.0) % (HELIX_HEIGHT / 4.0)

    # 1. Generate Points & Rungs
    points_A = []
    points_B = []
    
    # Generate points across the height
    for i in range(STRAND_LENGTH_STEPS + 1):
        y_norm = i / STRAND_LENGTH_STEPS
        
        # Calculate Y position (centered)
        y = (y_norm - 0.5) * HELIX_HEIGHT
        
        # Twist angle
        base_angle = (y_norm * math.pi * TWIST_TIGHTNESS) + rotation_speed
        
        # Strand A center
        xA = STRAND_RADIUS * math.cos(base_angle)
        zA = STRAND_RADIUS * math.sin(base_angle)
        
        # Strand B center (offset by PI)
        xB = STRAND_RADIUS * math.cos(base_angle + math.pi)
        zB = STRAND_RADIUS * math.sin(base_angle + math.pi)

        # Apply global rotation/wobble
        ptA = rotate_x(rotate_y((xA, y, zA), wobble_angle), wobble_angle * 0.5)
        ptB = rotate_x(rotate_y((xB, y, zB), wobble_angle), wobble_angle * 0.5)
        
        points_A.append(ptA)
        points_B.append(ptB)
        
        # Draw Rungs (Connecting base pairs)
        # We draw them directly here using draw_thick_line
        if i % 6 == 0: # Every 6th step
            # Project endpoints
            projA = project_point(ptA[0], ptA[1], ptA[2], width, height)
            projB = project_point(ptB[0], ptB[1], ptB[2], width, height)
            
            if projA and projB:
                sxA, syA = projA
                sxB, syB = projB
                
                # Color based on depth
                avg_z = (ptA[2] + ptB[2]) / 2
                color = theme_manager.get_color_for_depth(avg_z, -STRAND_RADIUS, STRAND_RADIUS)
                
                # Draw thick rung
                # Use thickness 1 for distant, 2 for close
                thickness = 2 if avg_z < 0 else 1
                buffer.draw_thick_line(sxA, syA, sxB, syB, "≡", avg_z, color, thickness=thickness)
                
                # Add a glow in the center for the "Hydrogen Bond"
                mx = (sxA + sxB) // 2
                my = (syA + syB) // 2
                if thickness > 1:
                    buffer.set_pixel_with_glow(mx, my, "●", avg_z - 0.1, theme_manager.get_accent(), glow_radius=2, theme_manager=theme_manager)

    # 2. Draw Strands (Thick)
    for i in range(len(points_A)):
        for pt, strand_id in [(points_A[i], 'A'), (points_B[i], 'B')]:
            x, y, z = pt
            proj = project_point(x, y, z, width, height)
            if not proj:
                continue
            sx, sy = proj
            
            color = theme_manager.get_color_for_depth(z, -STRAND_RADIUS, STRAND_RADIUS)
            
            # Thick Strand Rendering
            # Draw a 2x2 block for the strand backbone
            char = "█"
            buffer.set_pixel_with_glow(sx, sy, char, z, color, glow_radius=1, theme_manager=theme_manager)
            buffer.set_pixel(sx + 1, sy, "▌", z, color) # Add visual width
            buffer.set_pixel(sx, sy + 1, "▀", z, color) # Add visual height
            
    # Return approx Z range for consistency (though not strictly needed if we color inside)
    return (-STRAND_RADIUS, STRAND_RADIUS)
