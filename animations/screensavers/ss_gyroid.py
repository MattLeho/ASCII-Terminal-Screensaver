"""
Isosurface Gyroid Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_gyroid(u, v, t):
    # Ray Setup
    # Simpler raymarching step for numpy
    
    ones = np.ones_like(u)
    # ro = [0, 0, t]
    ro_x = 0
    ro_y = 0
    ro_z = t * 1.0
    
    fov = 1.5
    # RD normalized
    norm = np.sqrt((u*fov)**2 + (v*fov)**2 + 1.0)
    rd_x = (u*fov) / norm
    rd_y = (v*fov) / norm
    rd_z = 1.0 / norm
    
    t_march = np.zeros_like(u)
    active = np.ones_like(u, dtype=bool)
    
    level = np.sin(t * 0.2) * 0.8
    level = np.clip(level, -0.9, 0.9)
    
    shift = t * 1.5
    
    # Fixed step count
    for i in range(15):
        if not np.any(active): break
        
        # P
        px = ro_x + rd_x * t_march
        py = ro_y + rd_y * t_march
        pz = ro_z + rd_z * t_march
        
        # Gyroid
        scale = 3.0
        sx, sy, sz = px*scale, py*scale, pz*scale
        
        val = np.sin(sx + shift)*np.cos(sy) + \
              np.sin(sy + shift)*np.cos(sz) + \
              np.sin(sz + shift)*np.cos(sx)
        
        d = np.abs(val - level) / 1.5
        d -= 0.05 # thickness
        
        t_march += d * 0.8
        
        # Hit
        hit = d < 0.02
        # Escaped
        escaped = t_march > 15.0
        
        # Done
        done = hit | escaped
        
        # Freeze t_march for done pixels? 
        # No need, we just stop updating 'active' ones ideally but array logic dictates we calc all
        # To optimize, we could multiply update by 'active'.
        
    # Result
    hit = t_march < 15.0
    intensity = 1.0 / (1.0 + t_march * t_march * 0.05)
    
    return np.where(hit, intensity, 0.0)

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_gyroid)
