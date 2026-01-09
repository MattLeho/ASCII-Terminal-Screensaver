"""
Neon Synthwave Terrain Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_synthwave(u, v, t):
    # Split Sky / Ground
    horizon = 0.15
    mask_ground = v <= horizon
    mask_sky = ~mask_ground
    
    # Initialize output
    output = np.zeros_like(u)
    
    # --- SKY ---
    if np.any(mask_sky):
        u_sky = u[mask_sky]
        v_sky = v[mask_sky]
        
        # Sun
        sun_y = 0.6
        dy = v_sky - sun_y
        dist = np.sqrt(u_sky**2 + dy**2)
        
        # Base sky
        sky_val = np.zeros_like(u_sky)
        
        # Sun Logic
        in_sun = dist < 0.35
        # Blinds
        blinds = np.sin(v_sky * 40.0 - t) > 0.2
        
        # Sun Gradient
        sun_col = 1.0 - (dy + 0.35)
        
        # Apply Logic: In sun AND (blinds OR top)
        sun_active = in_sun & blinds
        
        sky_val[sun_active] = sun_col[sun_active]
        
        # Starfield (simple noise)
        stars = (np.sin(u_sky*80) * np.cos(v_sky*90)) > 0.98
        sky_val[stars & ~in_sun] = 0.7
        
        output[mask_sky] = sky_val
        
    # --- GROUND ---
    if np.any(mask_ground):
        u_g = u[mask_ground]
        v_g = v[mask_ground]
        
        # Perspective Z
        # z = cam_h / (horizon - v)
        denom = horizon - v_g
        denom[denom < 1e-4] = 1e-4 # Clamp
        z = 1.0 / denom
        x = u_g * z
        
        # Motion
        z_moved = z + t * 3.0
        
        # Fourier Height
        height = 0.3 * np.sin(0.5 * x) * np.cos(0.4 * z_moved) + \
                 0.1 * np.sin(1.5 * x) * np.cos(1.5 * z_moved)
                 
        # Grid Glow
        # Modulo
        grid_width = 0.1
        grid_x = np.abs(x) % 1.0
        grid_z = z_moved % 1.0
        
        is_grid = (grid_x < grid_width) | (grid_z < grid_width)
        
        ground_col = np.maximum(0.0, height * 0.5)
        ground_col[is_grid] = 1.0
        
        output[mask_ground] = ground_col
        
    return output

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_synthwave)
