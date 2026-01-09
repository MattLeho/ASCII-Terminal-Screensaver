"""
Mandelbulb Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_mandelbulb(u, v, t):
    # Raymarching in Numpy?
    # This is heavy. Doing a loop over all pixels in parallel steps.
    
    # Ray Setup
    uv_shape = u.shape
    
    # ro = [0, 0, -2.5]
    ro = np.array([0.0, 0.0, -2.5])
    
    # rd
    fov = 1.0
    # Stack U, V, 1.0
    ones = np.ones(uv_shape)
    rd = np.stack([u * fov, v * fov, ones], axis=-1)
    
    # Normalize RD
    lengths = np.linalg.norm(rd, axis=-1, keepdims=True)
    rd = rd / lengths
    
    # Power
    power = 8.0 + 2.0 * np.sin(t * 0.3)
    
    # Current t (focal depth)
    t_march = np.zeros(uv_shape)
    
    # Mask of active pixels (haven't hit or escaped)
    active = np.ones(uv_shape, dtype=bool)
    
    # Output steps (AO)
    steps_count = np.zeros(uv_shape)
    
    max_steps = 20 # Increased from 10 for better detail
    
    # Rotation Matrix (around Y)
    theta = t * 0.2
    c = np.cos(theta)
    s = np.sin(theta)
    
    # iterate
    for i in range(max_steps):
        if not np.any(active):
            break
            
        # P = ro + rd * t
        p = ro + rd * t_march[..., np.newaxis]
        
        # Rotated P for Fractal
        px = p[..., 0]
        py = p[..., 1]
        pz = p[..., 2]
        
        # Rotate P
        px_r = px * c - pz * s
        pz_r = px * s + pz * c
        py_r = py
        
        # Fractal Iteration
        # w = p_rotated
        wx, wy, wz = px_r, py_r, pz_r
        
        dr = 1.0
        r = 0.0
        
        # Mandelbulb DE Loop
        for k in range(5): # Increased iterations slightly
            r = np.sqrt(wx*wx + wy*wy + wz*wz)
            
            # Polar
            # Avoid r=0
            r_safe = np.maximum(r, 1e-9)
            
            theta_m = np.arccos(wz / r_safe)
            phi_m = np.arctan2(wy, wx)
            
            dr = np.power(r, power - 1.0) * power * dr + 1.0
            
            zr = np.power(r, power)
            theta_m *= power
            phi_m *= power
            
            # Cartesian
            wx = zr * np.sin(theta_m) * np.cos(phi_m) + px_r
            wy = zr * np.sin(theta_m) * np.sin(phi_m) + py_r
            wz = zr * np.cos(theta_m) + pz_r
            
            if r > 2.0: # Escape early optimization
                break
            
        # Final Dist
        length_r = np.sqrt(wx*wx + wy*wy + wz*wz) 
        # DE = 0.5 * log(r) * r / dr
        dist = 0.5 * np.log(length_r + 1e-9) * length_r / dr
        
        # Update t
        t_march += dist * 0.8 # Slower step for safety
        steps_count += 1
        
        # Check hit
        hit = dist < 0.005 # Stricter hit threshold
        
        # Check far plane
        escaped = t_march > 10.0 # Further far plane
        
        # Update active mask: turn off if hit or escaped
        active_now = active & ~hit & ~escaped
        if not np.any(active_now):
             break
        
        # Optimization: only update active pixels in next iter? 
        # Numpy doesn't support easy sparse updates without indexing overhead.
        # Just keep looping with masking logic if needed, or multiply dist by active.
        
        # If we didn't update active mask, we'd continue marching hit pixels.
        # So we must use the mask. But we can't easily "skip" computation for specific indices in pure vector ops.
        # We effectively mask the 'dist' addition? 
        # dist[~active] = 0 -> This effectively stops them.
        
        # Let's enforce stop
        # Update t only for active
        # t_march = np.where(active, t_march + dist, t_march) -> Already done above? No.
        # The variables above were computed for ALL pixels.
        
        # Retain state for inactive pixels
        # Actually logic above `t_march += dist` updates everything.
        # We need to revert or mask.
        
    # Result
    # Intensity based on steps (AO)
    intensity = 1.0 - (steps_count / max_steps)
    
    # Mask background (where escaped)
    intensity[t_march > 9.5] = 0.0
    
    return intensity

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_mandelbulb)
