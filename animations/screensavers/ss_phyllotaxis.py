"""
Dynamic Phyllotaxis Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_phyllotaxis(u, v, t):
    # Polar
    r = np.sqrt(u**2 + v**2)
    theta = np.arctan2(v, u)
    
    mask = r < 1.0
    
    # Invert to n
    c = 0.02
    n_approx = (r / c) ** 2
    n_base = np.round(n_approx)
    
    # Angle
    delta = 2.0 * np.sin(t * 0.2)
    angle_rad = np.radians(137.5 + delta)
    
    # Check neighbors -1, 0, 1
    # We want min distance to ANY seed
    
    best_dist = np.full_like(r, 100.0)
    
    for offset in [-1, 0, 1]:
        n = n_base + offset
        # Mask valid n
        valid = n >= 0
        
        # Calculate seed pos for this n
        r_n = c * np.sqrt(n)
        theta_n = n * angle_rad
        
        # Diff angle
        diff = theta - theta_n
        diff = (diff + np.pi) % (2*np.pi) - np.pi
        
        # Dist
        dr = r - r_n
        d_arc = r * diff
        
        dist = np.sqrt(dr**2 + d_arc**2)
        
        # Update best
        best_dist = np.minimum(best_dist, dist)
        
    return np.where(best_dist < 0.015, 1.0 - r*0.5, 0.0)

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_phyllotaxis)
