"""
Torus (Donut) Animation with True Lighting
The classic ASCII donut with proper surface normal lighting.
Enhanced with luminance-based shading for realistic 3D appearance.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import project_point


def render_torus(buffer, width, height, time, theme_manager):
    """
    Render a spinning torus (donut) with proper lighting.
    
    Uses surface normal calculations for realistic luminance shading.
    The donut appears to have a 3D "shine" effect.
    """
    # Donut Geometry
    R = 2.2   # Major radius (distance from center)
    r = 0.9   # Minor radius (thickness of tube)
    
    # Rotation
    A = time * 1.2  # X-axis rotation
    B = time * 0.7  # Z-axis rotation
    
    # Resolution
    theta_steps = 80  # Around the tube
    phi_steps = 50    # Around the torus ring
    
    # Luminance character ramp (dark to bright)
    chars = ".,-~:;=!*#$@"
    
    all_z = []

    for i in range(theta_steps):
        theta = 2 * math.pi * i / theta_steps
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)
        
        for j in range(phi_steps):
            phi = 2 * math.pi * j / phi_steps
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)
            
            # 1. 3D Coordinates before rotation
            circle_x = R + r * cos_theta
            circle_y = r * sin_theta
            
            x = circle_x * cos_phi
            y = circle_y
            z = circle_x * sin_phi
            
            # 2. Surface Normal (for lighting)
            nx = cos_theta * cos_phi
            ny = sin_theta
            nz = cos_theta * sin_phi
            
            # 3. Apply Rotation Matrices
            # Rotate around X (Angle A)
            cos_A, sin_A = math.cos(A), math.sin(A)
            y_rot = y * cos_A - z * sin_A
            z_rot = y * sin_A + z * cos_A
            y, z = y_rot, z_rot
            
            ny_rot = ny * cos_A - nz * sin_A
            nz_rot = ny * sin_A + nz * cos_A
            ny, nz = ny_rot, nz_rot

            # Rotate around Z (Angle B)
            cos_B, sin_B = math.cos(B), math.sin(B)
            x_rot = x * cos_B - y * sin_B
            y_rot = x * sin_B + y * cos_B
            x, y = x_rot, y_rot
            
            nx_rot = nx * cos_B - ny * sin_B
            ny_rot = nx * sin_B + ny * cos_B
            nx, ny = nx_rot, ny_rot
            
            # 4. Project to screen
            # Removed manual distance override to use global safe scaling
            proj = project_point(x, y, z, width, height)
            
            if proj:
                # 5. Calculate Luminance (Dot Product of Normal and Light)
                # Light direction: from top-front (0, 0.7, -0.7)
                luminance = ny * 0.7071 - nz * 0.7071
                
                # Only render front-facing surfaces (luminance > 0)
                if luminance > 0:
                    # Map luminance to character index
                    idx = int(luminance * (len(chars) - 1))
                    char = chars[max(0, min(len(chars) - 1, idx))]
                    
                    # Color based on depth for theme gradient
                    color = theme_manager.get_color_for_depth(z, -3, 3)
                    
                    buffer.set_pixel(proj[0], proj[1], char, z, color)
                    all_z.append(z)

    if not all_z:
        return (0, 1)
    return (min(all_z), max(all_z))
