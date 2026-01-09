"""
Gravitational Potential Field Screensaver
Numpy Optimized.
"""

import numpy as np
from shader_engine import run_shader_animation

def shader_potential(u, v, t):
    x = u * 1.5
    y = v * 1.5
    
    bodies = [
        (np.sin(t)*0.8, np.sin(2*t)*0.4, 1.0),
        (np.sin(t+2.09)*0.8, np.sin(2*(t+2.09))*0.4, 1.0),
        (np.sin(t+4.18)*0.8, np.sin(2*(t+4.18))*0.4, 1.0)
    ]
    
    V = np.zeros_like(x)
    
    for bx, by, m in bodies:
        dx = x - bx
        dy = y - by
        dist = np.sqrt(dx**2 + dy**2)
        dist = np.maximum(dist, 0.05)
        
        V += 0.5 * m / dist
        
    # Coloring
    topo = np.sin(V * 40.0 - t*5.0)
    col = (topo + 1.0) * 0.5
    col += V * 0.1
    
    return np.clip(col, 0.0, 1.0)

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_potential)
