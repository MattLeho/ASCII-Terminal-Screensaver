"""
ECG / Electrocardiogram Screensaver
Numpy Optimized.
Based on Shadertoy 'Electrocardiogram_Loewe' by Loewe
https://www.shadertoy.com/view/XsyGzD
"""

import numpy as np

def smoothstep(edge0, edge1, x):
    """GLSL smoothstep implementation for NumPy arrays."""
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def length(v):
    """Vector length along last axis."""
    return np.sqrt(np.sum(v**2, axis=-1))

def shader_ecg(u, v, t):
    """
    ECG shader function.
    u, v: Normalized coordinates from shader engine
    t: Time in seconds
    Returns: RGB array of shape (H, W, 3)
    """
    # Get aspect ratio from u coordinates
    # u is already scaled by aspect in shader_engine
    aspect = np.max(np.abs(u)) if u.size > 0 else 1.6
    
    # uv2 is used for the travelling glow effect
    # uv2.x += iResolution.x/iResolution.y (add aspect)
    # uv2.x -= 2.0*mod(iTime, 1.0*iResolution.x/iResolution.y)
    
    u2 = u + aspect
    travel_period = aspect * 2.0  # Full width travel
    u2 = u2 - 2.0 * (t % travel_period)
    
    # Width calculation for glow: width = -(1.0/(25.0*uv2.x))
    # Need to handle division by near-zero
    u2_safe = np.where(np.abs(u2) < 0.01, 0.01 * np.sign(u2 + 1e-9), u2)
    width = -1.0 / (25.0 * u2_safe)
    
    # Glow intensity multipliers for RGB
    l_r = width
    l_g = width * 1.9
    l_b = width * 1.5
    
    # ---------------------------------------------------------
    # Premium High-Detail ECG
    # ---------------------------------------------------------
    
    # 1. Background Grid (Millimeter Paper effect)
    # ---------------------------------------------------------
    grid_x = np.abs(np.sin(u * 40.0))
    grid_y = np.abs(np.sin(v * 40.0 * 0.6)) # Aspect correction approx
    
    # sharp grid lines
    grid_x = smoothstep(0.95, 1.0, grid_x)
    grid_y = smoothstep(0.95, 1.0, grid_y)
    
    grid = np.maximum(grid_x, grid_y) * 0.1 # Dim grid
    
    # 2. Main ECG Trace (High Detail)
    # ---------------------------------------------------------
    v_scaled = v * 2.0
    
    # Amplitude modulation
    u_clamped = np.maximum(np.abs(u), 0.3)
    xx = np.abs(1.0 / (20.0 * u_clamped))
    
    # Complex waveform (Sum of Sines)
    u_wave = u * 3.0
    ecg_wave = (np.sin(u_wave) + 
                3.0 * np.sin(2.0 * u_wave) + 
                2.0 * np.sin(3.0 * u_wave) + 
                np.sin(4.0 * u_wave))
                
    # High frequency noise for "realism" (sensor noise)
    sensor_noise = np.sin(u * 200.0) * 0.05 * np.cos(t * 10.0)
    
    dist_curve = np.abs(v_scaled - xx * ecg_wave - sensor_noise)
    
    # Thicker, glowing line
    # Core (White hot)
    core = 0.08 / (dist_curve + 0.02)
    core = np.power(core, 2.0)
    
    # Glow (Green halo)
    glow = 0.2 / (dist_curve + 0.1)
    
    # 3. Traveling Pulse / Scanline
    # ---------------------------------------------------------
    u2 = u + aspect
    travel_dist = aspect * 2.0
    u2 = u2 - 2.0 * (t % travel_dist)
    
    # Pulse trigger (where u2 is near 0)
    # Use a smooth bell curve for the pulse head
    pulse_pos = -u2
    # Only show pulse if passed (positive)
    trace_active = smoothstep(-0.1, 0.0, pulse_pos) # Hard cut at lead
    trace_fade = np.exp(-pulse_pos * 2.0) # Long fade tail
    
    trace_intensity = trace_active * trace_fade
    
    # 4. Compositing
    # ---------------------------------------------------------
    # Base color (Grid + faint static trace)
    r = grid * 0.2
    g = grid * 0.5 + core * 0.1 # Faint green trace always visible
    b = grid * 0.2
    
    # Pulse Colors (Bright Green + White Hot Core)
    pulse_r = (core * 1.0 + glow * 0.2) * trace_intensity
    pulse_g = (core * 1.0 + glow * 0.8) * trace_intensity
    pulse_b = (core * 1.0 + glow * 0.2) * trace_intensity
    
    # Add pulse
    r += pulse_r
    g += pulse_g
    b += pulse_b
    
    # Vignette
    vignette = 1.0 - 0.4 * length(np.stack((u*0.5, v*0.5), axis=-1))
    
    r *= vignette
    g *= vignette
    b *= vignette
    
    # Clip
    r = np.clip(r, 0.0, 1.0)
    g = np.clip(g, 0.0, 1.0)
    b = np.clip(b, 0.0, 1.0)
    
    return np.stack((r, g, b), axis=-1)

def render(buffer, width, height, time, theme_manager):
    """Standard render function for integration with shader engine."""
    from shader_engine import run_shader_animation
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_ecg)
