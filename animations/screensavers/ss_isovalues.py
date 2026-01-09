"""
Isovalues / Contour Lines Screensaver
Numpy Optimized.
Based on Shadertoy 'isovalues 3' by FabriceNeyret2
https://www.shadertoy.com/view/ldfczS
"""

import numpy as np

def fract(x):
    """GLSL fract - fractional part of x."""
    return x - np.floor(x)

def smoothstep(edge0, edge1, x):
    """GLSL smoothstep implementation for NumPy arrays."""
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def hash3(px, py, pz):
    """
    Hash function for 3D noise.
    hash3(p) = fract(sin(1e3*dot(p,vec3(1,57,-13.7)))*4375.5453)
    """
    dot_val = px + 57.0 * py - 13.7 * pz
    return fract(np.sin(1e3 * dot_val) * 4375.5453)

def noise3(x, y, z):
    """
    3D noise function using trilinear interpolation of hash values.
    Based on IQ's noise implementation.
    """
    # Floor and fract
    px = np.floor(x)
    py = np.floor(y)
    pz = np.floor(z)
    
    fx = x - px
    fy = y - py
    fz = z - pz
    
    # Smoothstep the fractions
    fx = fx * fx * (3.0 - 2.0 * fx)
    fy = fy * fy * (3.0 - 2.0 * fy)
    fz = fz * fz * (3.0 - 2.0 * fz)
    
    # Trilinear interpolation of 8 corner hash values
    # mix(a, b, t) = a * (1-t) + b * t
    
    # z = 0 plane
    h000 = hash3(px, py, pz)
    h100 = hash3(px + 1, py, pz)
    h010 = hash3(px, py + 1, pz)
    h110 = hash3(px + 1, py + 1, pz)
    
    # z = 1 plane
    h001 = hash3(px, py, pz + 1)
    h101 = hash3(px + 1, py, pz + 1)
    h011 = hash3(px, py + 1, pz + 1)
    h111 = hash3(px + 1, py + 1, pz + 1)
    
    # Interpolate along x
    h00 = h000 * (1 - fx) + h100 * fx
    h10 = h010 * (1 - fx) + h110 * fx
    h01 = h001 * (1 - fx) + h101 * fx
    h11 = h011 * (1 - fx) + h111 * fx
    
    # Interpolate along y
    h0 = h00 * (1 - fy) + h10 * fy
    h1 = h01 * (1 - fy) + h11 * fy
    
    # Interpolate along z
    return h0 * (1 - fz) + h1 * fz

def noise(x, y, z):
    """
    Improved noise by averaging two offset samples.
    noise(x) = (noise3(x) + noise3(x+11.5)) / 2.0
    """
    return (noise3(x, y, z) + noise3(x + 11.5, y + 11.5, z + 11.5)) * 0.5

def approximate_fwidth(arr):
    """
    Approximate fwidth (screen-space derivative) using finite differences.
    fwidth = |ddx| + |ddy|
    """
    # Use numpy gradient for central differences
    ddy, ddx = np.gradient(arr)
    return np.abs(ddx) + np.abs(ddy)

def shader_isovalues(u, v, t):
    """
    Isovalues shader function.
    Draws contour lines of a noise field.
    u, v: Normalized coordinates from shader engine
    t: Time in seconds
    Returns: RGB array of shape (H, W, 3)
    """
    # Scale coordinates
    # U*8./R.y where R.y normalizes... u,v already normalized
    # Scale coordinates
    # U*8./R.y where R.y normalizes... u,v already normalized
    # REDUCED SCALE: 8.0 was too high for terminal, causing aliasing noise.
    # 2.5 gives nice large organic shapes.
    # ---------------------------------------------------------
    # Premium Isovalues with DOMAIN WARPING
    # ---------------------------------------------------------
    
    # Coordinates
    scale = 3.5  # Zoom level
    p = np.stack((u * scale, v * scale, np.full_like(u, t * 0.1)), axis=-1)
    
    # 1. Domain Warping FBM
    # q = fbm(p)
    # r = fbm(p + q)
    # noise = fbm(p + r)
    
    # We need a vectorized FBM helper inside here or global
    # Let's do a simple 2-octave warp inline for performance/detail balance
    
    # Octave 1
    q_x = noise(p[..., 0], p[..., 1], p[..., 2])
    q_y = noise(p[..., 0] + 5.2, p[..., 1] + 1.3, p[..., 2] + 2.8)
    q_z = noise(p[..., 0] - 2.2, p[..., 1] - 3.5, p[..., 2] - 1.2)
    
    # Warp magnitude
    warp_mag = 1.0
    p_warped_x = p[..., 0] + q_x * warp_mag
    p_warped_y = p[..., 1] + q_y * warp_mag
    p_warped_z = p[..., 2] + q_z * warp_mag
    
    # Octave 2 (The actual pattern)
    # Get noise from warped coordinates
    # We mix two frequencies for detail
    n_base = noise(p_warped_x, p_warped_y, p_warped_z)
    n_detail = noise(p_warped_x * 2.0, p_warped_y * 2.0, p_warped_z * 2.0)
    
    n = n_base * 0.7 + n_detail * 0.3
    
    # 2. Contour Lines
    # ---------------------------------------------------------
    # Frequency of lines
    oscillation = np.sin(6.28318 * 8.0 * n + t * 0.5)
    
    # Derivative approx
    fw = approximate_fwidth(oscillation)
    # SHARPER LINES: Reduce min width from 0.02 to 0.01 for crisper look on Braille
    fw = np.maximum(fw, 0.01) 
    
    # Thin, sharp lines for premium look
    # Sharpen edge: smoothstep(1.0, 0.0) -> smoothstep(0.8, 0.0)
    contour = smoothstep(0.8, 0.0, 0.4 * np.abs(oscillation) / fw)
    
    # ---------------------------------------------------------
    # Theme Handling
    # ---------------------------------------------------------
    
    # Check current theme (set by render function)
    current_theme = globals().get('CURRENT_THEME_NAME', 'isovalues')
    
    if current_theme == 'isovalues':
        # PREMIUM RGB MODE (Plasma)
        # IQ Palette: a + b*cos(6.28318*(c*t+d))
        col_t = n + t * 0.1
        color_r = 0.5 + 0.5 * np.cos(6.28318 * (col_t + 0.00))
        color_g = 0.5 + 0.5 * np.cos(6.28318 * (col_t + 0.33))
        color_b = 0.5 + 0.5 * np.cos(6.28318 * (col_t + 0.67))
        
        # Dark voids between lines
        bg_r = 0.05
        bg_g = 0.05
        bg_b = 0.1
        
        # Mix
        r = contour * color_r + (1 - contour) * bg_r
        g = contour * color_g + (1 - contour) * bg_g
        b = contour * color_b + (1 - contour) * bg_b
        
        # Add brightness boost to lines
        r += contour * 0.4
        g += contour * 0.4
        b += contour * 0.4
        
        # Gamma
        r = np.power(np.clip(r, 0, 1), 0.8)
        g = np.power(np.clip(g, 0, 1), 0.8)
        b = np.power(np.clip(b, 0, 1), 0.8)
        
        return np.stack((r, g, b), axis=-1)
        
    else:
        # MONOCHROME MODE (For Engine Theme Coloring)
        # Return single channel intensity map
        # intensity = contour + noise detail
        intensity = contour * 1.0 + n * 0.2
        return np.clip(intensity, 0.0, 1.0)

# Global to track theme state
CURRENT_THEME_NAME = 'isovalues'

def render(buffer, width, height, time, theme_manager):
    """Standard render function for integration with shader engine."""
    from shader_engine import run_shader_animation
    
    # Inject current theme name for the shader to read
    global CURRENT_THEME_NAME
    CURRENT_THEME_NAME = theme_manager.current_theme
    
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_isovalues)
