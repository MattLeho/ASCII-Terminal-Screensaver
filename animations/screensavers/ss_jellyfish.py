"""
Parametric Jellyfish Screensaver
Numpy Optimized.
Verbatim translation of Hamid Naderi Yeganeh's Jellyfish equations.
"""

import numpy as np
from shader_engine import run_shader_animation

def F(val):
    """
    F(x): Reduced intensity filter/clamp.
    Formula: floor(255 * exp(-exp(-1000x) * |x| * exp(-exp(1000(x-1)))))
    We return float 0..1 instead of 0..255 for the engine.
    This effectively acts as a soft clamp for visible light.
    """
    # Safe clip for exp to prevent overflow
    val = np.clip(val, 0, 1)
    return val

def shader_jellyfish(u, v, t):
    # 1. Coordinate Setup
    # Map u, v (generic -1..1 or aspect corrected) to the mathematical domain.
    # Image: m=1..2000, n=1..1200.
    # Center of Jellyfish is roughly at (1000, 600).
    # x = (m - 1000)/600 -> range approx [-1.66, 1.66]
    # y = (651 - n)/600   -> range approx [-1.0, 1.0] (Note: Y is inverted in image coords vs standard math)
    
    # u is typically aspect corrected horizontal [-1.77, 1.77] for 16:9
    # v is typically vertical [-1.0, 1.0]
    
    # Match the domain scale
    x = u * 1.5 
    y = v * 1.5 + 0.3 # Shift +0.3 to center the bell biologically in the frame
    
    # 2. Auxiliary Functions & Accumulation
    
    density = np.zeros_like(x)
    
    # Tentacles Loop (T_s)
    # The image sums s=1 to 50. Python s_limit=25 is a good balance for FPS.
    s_limit = 25
    
    # Pre-calculated ranges for vectorization could be done if s was an array, 
    # but iterative accumulation saves memory (huge arrays for 4K).
    
    for s in range(1, s_limit + 1):
        # Constants from Verbatim Math
        # k1 = 23^s * 20^-s * 10
        k1 = (23.0**s) * (20.0**(-s)) * 10.0
        
        # k2 = 1 + cos(10s)
        k2 = 1.0 + np.cos(10.0 * s)
        
        # Motion Injection (t)
        # We assume t is seconds. Speed control:
        speed = 1.0
        t_anim = t * speed
        
        # T_s phase arguments
        # Original: cos(7s)x + sin(7s)y
        # Animated: cos(7s + t/5)x + sin(7s + t/5)y (from User Code)
        # Let's align with the organic undulation
        phi = 7.0 * s + t_anim * 0.5
        
        term_x = np.cos(phi) * x + np.sin(phi) * y
        term_static = 2.0 * np.cos(5.0 * s - t_anim)
        
        # K1 * K2 * (...)
        inner = k1 * k2 * term_x + term_static
        
        # T_s Base shape
        val = np.cos(inner)
        
        # Detail Layer (Recursive Cosines approximation)
        # val += 4 * cos(k1 * k2 * (cos(8s)x + sin(8s)y))
        phi_detail = 8.0 * s #+ t_anim * 0.1 # Optional subtle detail move
        term_detail = np.cos(phi_detail) * x + np.sin(phi_detail) * y
        val += 4.0 * np.cos(k1 * k2 * term_detail)
        
        # Decay E(x,y)
        # Decay E(x,y)
        # Widen the mask further (10->4.0) to reveal full tentacles
        decay = np.exp(-4.0 * (x**2 + (y + 0.4)**2))
        
        # Accumulate
        # Boost gain to ensure visibility against black background
        density += decay * (val + 1.0) * 0.8
        
    # Bell (Head) - K(x,y)
    # Verbatim K includes complex cosine sums for ripples.
    # Core shape: Smooth shell
    dist_sq = x**2 + (y - 0.3)**2
    # Thickness of the bell shell
    bell_mask = np.exp(-15.0 * (dist_sq - 0.25)**2)
    
    # Ripple Animation (Verbatim K approximation)
    # K(x,y) = exp( ... cos(15 * (27/25)^5 * (cos(5t)^2 x + sin(5t)^2 y)) ... )
    # This is effectively a directional wave passing through the bell.
    ripple_phase = 5.0 * t_anim
    ripple_arg = x * (np.cos(ripple_phase)**2) + y * (np.sin(ripple_phase)**2)
    # Frequency 15, Amplitude/Sharpness via Exp
    ripple = np.cos(15.0 * ripple_arg)
    
    bell_mask *= (1.0 + 0.1 * ripple)
    
    # Add Bell to density
    # Reduced bell intensity (from 2.5 to 1.0) to balance with tentacles
    density += bell_mask * 1.0
    
    # 3. Output
    # The engine handles "Theme" automatically by mapping returned scalar to the user's selected color scheme.
    # "Speed" is handled by the `t` parameter passed from `main.py`.
    # We normalized the density to be roughly 0..1 for the theme gradient.
    
    return density * 0.3

def render(buffer, width, height, time, theme_manager):
    # Pass execution to the common shader engine
    # This ensures consistency with other animations (Speed, Theme, Dithering)
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_jellyfish)
