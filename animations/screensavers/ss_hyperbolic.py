"""
Hyperbolic Flight (Poincaré Disk) Screensaver
Numpy Optimized with fix for static behavior (Periodic domain).
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_hyperbolic(u, v, t):
    # u, v are numpy arrays
    
    # Scale coordinates
    # u, v are in [-aspect, aspect] and [-1, 1] roughly.
    scale = 1.1
    u = u * scale
    v = v * scale
    
    # Complex z
    z = u + 1j * v
    
    # Mask for Unit Disk
    r_sq = u*u + v*v
    mask = r_sq < 1.0
    
    # Points outside result in 0
    # We'll compute only for valid points or mask later
    
    # Fix for static: 
    # Instead of boosting Z -> 1 (infinity), map to Half-Plane and scroll periodically.
    
    # 1. Map Disk to Upper Half Plane (UHP)
    # w = i * (1 + z) / (1 - z)
    
    # Avoid div by zero at z=1 (handled by mask mostly)
    denom = 1.0 - z
    # Tiny epsilon to avoid hard crash
    denom[np.abs(denom) < 1e-9] = 1e-9
    
    w = 1j * (1.0 + z) / denom
    
    # 2. Infinite Scroll
    # In UHP, dilation corresponds to hyperbolic translation.
    # w_new = w * exp(velocity * t)
    # This blows up w.
    # But the tiling pattern depends on log(Im(w)) and Re(w).
    # log(Im(w_new)) = log(Im(w) * exp(vt)) = log(Im(w)) + vt
    # This is additive! So we can use modulo to keep it bounded.
    
    flight_speed = 0.8
    offset = t * flight_speed
    
    # We analyze w properties directly
    re = w.real
    im = w.imag
    
    # Log-height for vertical tiling
    log_im = np.log(np.abs(im) + 1e-9)
    
    # Apply scroll
    # Moving "forward" (towards boundary z=1) means looking at smaller and smaller features in Disk?
    # Or flowing out?
    # Usually tunnel effect: things come from infinity.
    # So we add t.
    
    scrolled_log_im = log_im + offset
    
    # Grid Pattern
    # Checkerboard in (Re, LogIm) space
    
    # Frequency
    freq_x = 2.0
    freq_y = 2.0
    
    p_x = np.sin(re * freq_x * np.pi)
    p_y = np.sin(scrolled_log_im * freq_y * np.pi)
    
    # Checkers
    val = np.where(p_x * p_y > 0, 0.8, 0.2)
    
    # Fade edges (Limit Circle)
    # 1 - |z|
    dist_edge = 1.0 - np.sqrt(r_sq)
    
    # Glow ring
    val = np.where(dist_edge < 0.05, val + 0.5, val)
    
    # Apply Mask (void outside disk)
    val = np.where(mask, val, 0.0)
    
    return val

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_hyperbolic)
