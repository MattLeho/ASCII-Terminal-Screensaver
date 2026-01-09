"""
Kleinian Limit Set Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_kleinian(u, v, t):
    # u, v are arrays
    z = (u * 2.5) + 1j * (v * 2.5)
    
    # Initial Iteration count array
    iters = np.zeros(u.shape, dtype=float)
    
    # Active mask (pixels that haven't escaped/settled yet? No, we iterate all)
    # Optimization: Only iterate points? Hard with array ops to handle branching.
    # We execute logic on full arrays and mask updates.
    
    # Circles
    root2 = np.sqrt(2.0)
    r = root2 / 2.0
    r_sq = r * r
    
    # Centers
    c1 = 1.0 + 0j
    c2 = -1.0 + 0j
    c3 = 0.0 + 1j
    c4 = 0.0 - 1j
    
    bases = np.array([c1, c2, c3, c4])
    
    # Animation: Rotate centers
    rot = np.exp(1j * t * 0.15)
    centers = bases * rot
    
    # Breathing
    breath = 1.0 + 0.1 * np.sin(t * 0.5)
    centers = centers * breath
    
    max_iter = 12 # Lower for numpy perf tradeoff (memory/compute)
    
    # We need to track who swapped to stop? 
    # Or just run fixed iterations.
    # Fixed iterations is faster in Numpy than masking per step usually for small N.
    
    current_z = z
    
    for _ in range(max_iter):
        swapped_any = False
        
        # We need to check all 4 circles
        # For each pixel, find if it's in ANY circle.
        # If in multiple? (Disjoint usually).
        
        # We can calculate distance to ALL 4 centers at once?
        # Z is (H,W), Centers is (4).
        # We need broadcast: (4, H, W)
        
        # Expand Z: (1, H, W)
        z_expanded = current_z[np.newaxis, :, :]
        # Expand Centers: (4, 1, 1)
        c_expanded = centers[:, np.newaxis, np.newaxis]
        
        dists_sq = np.abs(z_expanded - c_expanded)**2
        
        # Check condition < r_sq
        in_circle = dists_sq < r_sq
        
        # Indices of circles to swap (take first match?)
        # argmax gives index of first True. But if none? 
        # any() check.
        
        has_match = np.any(in_circle, axis=0)
        
        # Update iteration count for those that matched
        iters[has_match] += 1
        
        # Apply transformation for the matched circle
        # z' = c + r^2 / conj(z-c)
        
        # To do this vectorially:
        # We construct a "target_c" array for each pixel.
        # If not in circle, target_c doesn't matter (we won't update).
        
        # We pick the FIRST circle index that matched.
        first_match_idx = np.argmax(in_circle, axis=0) # indices 0..3
        
        # Gather corresponding centers
        # chosen_c = centers[first_match_idx] -- this works with numpy indexing
        chosen_c = centers[first_match_idx]
        
        # Perform inversion on ALL pixels (temp)
        dz = current_z - chosen_c
        # Prevent div by zero
        dz_conj = np.conj(dz)
        # Avoid zero division
        dz_conj[dz_conj == 0] = 1e-9
        
        new_z = chosen_c + r_sq / dz_conj
        
        # Only update where has_match is True
        current_z = np.where(has_match, new_z, current_z)
        
        # Break if no pixels updated? (Unlikely for full screen)
    
    # Coloring
    val = iters / max_iter
    val = np.power(val, 0.7)
    
    return val

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_kleinian)
