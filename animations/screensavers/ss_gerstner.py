"""
Gerstner Wave Ocean Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_gerstner(u, v, t):
    # u, v are arrays (mesh grids)
    
    # World Coords
    x = u * 4.0
    # Move Z with time for forward flight
    z = v * 4.0 + t * 0.5
    
    # Waves Parameters (Dx, Dz, Q, A, w, phi)
    waves = [
        (0.8, 0.6, 1.0, 0.4, 1.2, 2.0),
        (-0.7, 0.7, 0.8, 0.25, 2.0, 3.5),
        (0.2, -0.9, 0.6, 0.15, 3.5, 5.0),
        (0.5, 0.3, 0.5, 0.1, 5.0, 6.0)
    ]
    
    # Accumulators
    offset_x = np.zeros_like(x)
    offset_z = np.zeros_like(z) # Not really used for height, but logic consistent
    height = np.zeros_like(x)
    
    # Normal components
    d_x = np.zeros_like(x) # partial x
    d_z = np.zeros_like(x) # partial z
    
    # Jacobian (simplified: sum of derivatives)
    jacobian = np.ones_like(x)
    
    for dx_dir, dz_dir, q, a, w, phi in waves:
        phase = w * (dx_dir * x + dz_dir * z) + phi * t
        
        c = np.cos(phase)
        s = np.sin(phase)
        
        # Accumulate Height
        height += a * s
        
        # For simple lighting/normal aproximation without full vector math:
        # We can approximate slopes.
        # Slope X += w * A * D_x * cos
        wa = w * a
        d_x += dx_dir * wa * c
        d_z += dz_dir * wa * c
        
        # Jacobian check for choppiness
        # J = 1 - sum(Q * w * A * sin) ? for 1D
        # For foam, we check high slope or concavity
        jacobian -= q * wa * s
        
    # Approximate Normal N = normalize(-slope_x, 1, -slope_z)
    mag = np.sqrt(d_x*d_x + 1.0 + d_z*d_z)
    nx = -d_x / mag
    ny = 1.0 / mag
    nz = -d_z / mag
    
    # Light Dir
    lx, ly, lz = 0.577, 0.577, 0.577 # normalized (1,1,1)
    
    dot = nx*lx + ny*ly + nz*lz
    
    # Color base
    val = (dot + 1.0) * 0.5
    
    # Foam
    val = np.where(jacobian < 0.0, val + 0.4, val) # Breaking waves
    
    # Peaks highlight
    val = np.where(height > 0.4, val + 0.2, val)
    
    return val

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_gerstner)
