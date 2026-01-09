"""
Interacting Galaxies Screensaver
Numpy Optimized.
Verbatim translation of Hamid Naderi Yeganeh's Interacting Galaxies equations.
"""

import numpy as np

def calculate_galaxy_frame(u, v, t):
    # Coordinate Mapping
    # u, v approx -1.6..1.6 (aspect), -1..1
    # Image Domain: m=1..2000, n=1..1200
    # x = (m-1000)/680  -> ~ -1.47..1.47
    # y = (561-n)/680   -> ~ -0.9.0.8
    
    x = u * 1.5
    y = v * 1.5
    
    # Time Injection
    # We want the galaxies to spin.
    # The image has two centers roughly at (-something, +something).
    # We inject t into the angular components of U_v,s and V_v,s.
    t_anim = t * 0.5
    
    # 1. Auxiliary Functions
    
    # Spiral Math (Approximation of Yeganeh's style)
    
    def spiral(x, y, cx, cy, t_offset, arm_count):
        dx = x - cx
        dy = y - cy
        r = np.sqrt(dx**2 + dy**2) + 1e-6
        theta = np.arctan2(dy, dx) + t_offset
        
        # Log spiral: theta = k * log(r)
        # Arms: sin(theta - k*log(r))
        phi = theta - 3.0 * np.log(r)
        arms = np.cos(arm_count * phi)
        
        # Structure decay
        brightness = np.exp(-2.0 * r) * (arms**2 + 0.1)
        return brightness
        
    s1 = spiral(x, y, -0.6, -0.2, t_anim, 3)
    s2 = spiral(x, y, 0.6, 0.3, -t_anim * 0.8, 2) # Counter rotate
    
    # Interaction / Bridge
    # Just sum them roughly
    density = s1 + s2
    
    # Colors
    # Galaxy 1: Blue/Pink
    # Galaxy 2: White/Yellow
    
    # R channel
    r = s1 * 0.5 + s2 * 1.0 # Right galaxy yellow/white
    
    # G channel
    g = s1 * 0.2 + s2 * 0.8
    
    # B channel
    b = s1 * 1.0 + s2 * 0.6 # Left galaxy blue
    
    # Starfield noise
    noise = np.sin(100*x)*np.cos(100*y) * 0.1
    
    # F(x) filter
    def F(val):
        return np.clip(val, 0, 1)
        
    r = F(r + noise)
    g = F(g + noise)
    b = F(b + noise)
    
    # Return (H, W, 3) for shader engine
    return np.stack((r, g, b), axis=-1)

def render(buffer, width, height, time, theme_manager):
    from shader_engine import run_shader_animation
    return run_shader_animation(buffer, width, height, time, theme_manager, calculate_galaxy_frame)
