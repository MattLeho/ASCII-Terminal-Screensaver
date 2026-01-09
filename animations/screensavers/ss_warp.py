"""
Domain Warping Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def noise_np(x, y):
    # Vectorized noise
    ix = np.floor(x)
    iy = np.floor(y)
    fx = x - ix
    fy = y - iy
    
    # Hash
    n = (ix + iy * 57).astype(int)
    n = (n << 13) ^ n
    # int overflow handling in python? numpy int32/64 handles it but wrapping logic implies 32bit noise
    # Standard pseudo noise:
    
    # Numpy ints might overflow differently unless we mask.
    mask = 0x7fffffff
    
    # Do math in float to avoid overflow errs or use proper numpy int types?
    # Actually Python ints are arbitrary precision. Numpy are fixed.
    # Let's use simple sin based noise for speed and safety in Numpy
    
    return np.sin(x * 12.9898 + y * 78.233) * 43758.5453 % 1.0

def smooth_noise(x, y):
    # Interpolated noise
    ix = np.floor(x)
    iy = np.floor(y)
    fx = x - ix
    fy = y - iy
    
    # Smoothstep
    u = fx * fx * (3.0 - 2.0 * fx)
    v = fy * fy * (3.0 - 2.0 * fy)
    
    # Neighbors
    a = noise_np(ix, iy)
    b = noise_np(ix + 1, iy)
    c = noise_np(ix, iy + 1)
    d = noise_np(ix + 1, iy + 1)
    
    return a + (b - a)*u + (c - a)*v + (a - b - c + d)*u*v

def fbm(x, y):
    val = 0.0
    amp = 0.5
    scale = 1.0
    
    # 4 Octaves
    for _ in range(4):
        val += amp * smooth_noise(x * scale, y * scale)
        amp *= 0.5
        scale *= 2.0
    return val

def shader_warp(u, v, t):
    # Domain Warping
    scale = 3.0
    px = u * scale
    py = v * scale
    
    # f(p)
    # We can use simple offsets for speed
    fx = fbm(px, py)
    fy = fbm(px + 5.2, py + 1.3)
    
    # g(p + f(p) + t)
    gx_in_x = px + fx + t * 0.2
    gx_in_y = py + fy + t * 0.2
    
    # Single octave shortcut for G to save FPS if needed, but FBM looks better
    gx = fbm(gx_in_x, gx_in_y)
    gy = fbm(gx_in_x + 8.3, gx_in_y + 2.8)
    
    # h(p + g(p) - t)
    hx_in_x = px + gx - t * 0.2
    hx_in_y = py + gy - t * 0.2
    
    h = fbm(hx_in_x, hx_in_y)
    
    # Color
    col = h
    g_mag = np.sqrt(gx**2 + gy**2)
    col = col * 0.6 + g_mag * 0.4
    
    # Contrast
    col = col * col * (3.0 - 2.0 * col)
    
    return col

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_warp)
