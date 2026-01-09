"""
Superformula Animation
A mathematical formula that can generate many different shapes.
Enhanced with larger scale and smoother morphing.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_y, rotate_x, rotate_z, project_point


def superformula(phi, a, b, m, n1, n2, n3):
    """
    Calculate r using the Superformula.
    
    r(phi) = [|cos(m*phi/4)/a|^n2 + |sin(m*phi/4)/b|^n3]^(-1/n1)
    """
    t = m * phi / 4
    
    term1 = abs(math.cos(t) / a) ** n2
    term2 = abs(math.sin(t) / b) ** n3
    
    total = term1 + term2
    
    if total == 0:
        return 1
    
    return total ** (-1 / n1)


def render_superformula(buffer, width, height, time, theme_manager):
    """
    Render a 3D superformula shape that morphs between forms.
    
    Features:
    - Continuously morphing shape parameters
    - Rotating on multiple axes
    - Larger scale for visibility
    """
    # Animate parameters for smooth morphing effect
    m1 = 4 + 3 * math.sin(time * 0.3)    # Controls number of "bumps"
    m2 = 4 + 3 * math.cos(time * 0.25)
    
    n1_1 = 1 + 0.5 * math.sin(time * 0.2)
    n2_1 = 1 + 0.5 * math.cos(time * 0.15)
    n3_1 = 1 + 0.5 * math.sin(time * 0.25)
    
    n1_2 = 1 + 0.5 * math.cos(time * 0.22)
    n2_2 = 1 + 0.5 * math.sin(time * 0.18)
    n3_2 = 1 + 0.5 * math.cos(time * 0.28)
    
    a = 1
    b = 1
    
    # LARGER scale
    scale = 2.2
    
    # Continuous rotation
    rot_y = time * 0.5
    rot_x = time * 0.3 + 0.3
    
    all_z = []
    points_to_draw = []
    
    # Higher resolution for smoother surface
    theta_steps = 50
    phi_steps = 50
    
    for i in range(theta_steps):
        theta = -math.pi / 2 + math.pi * i / (theta_steps - 1)  # -π/2 to π/2
        
        for j in range(phi_steps):
            phi = -math.pi + 2 * math.pi * j / (phi_steps - 1)  # -π to π
            
            # Calculate superformula radii
            r1 = superformula(theta, a, b, m1, n1_1, n2_1, n3_1)
            r2 = superformula(phi, a, b, m2, n1_2, n2_2, n3_2)
            
            # Convert to Cartesian using spherical coordinates
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)
            cos_phi = math.cos(phi)
            sin_phi = math.sin(phi)
            
            x = r1 * cos_theta * r2 * cos_phi * scale
            y = r1 * sin_theta * scale
            z = r1 * cos_theta * r2 * sin_phi * scale
            
            # Apply rotations
            point = rotate_y((x, y, z), rot_y)
            point = rotate_x(point, rot_x)
            x, y, z = point
            
            projected = project_point(x, y, z, width, height, distance=4.0)
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
