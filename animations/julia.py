"""
Julia Set Fractal Animation
3D projection of the classic Julia set fractal with zooming.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import project_point


def render_julia(buffer, width, height, time, theme_manager):
    """
    Render a Julia set fractal that morphs and zooms.
    
    Features:
    - Morphing Julia constant creates organic movement
    - Iteration count maps to color depth
    - Simulated 3D by mapping iterations to height
    """
    # Julia set constant - morphs over time for animation
    # Classic interesting values: (-0.7, 0.27015), (0.355, 0.355), (-0.8, 0.156)
    cr = -0.7 + 0.2 * math.sin(time * 0.3)
    ci = 0.27015 + 0.1 * math.cos(time * 0.4)
    
    # Zoom and pan
    zoom = 1.5 + 0.5 * math.sin(time * 0.1)
    pan_x = 0.1 * math.sin(time * 0.2)
    pan_y = 0.1 * math.cos(time * 0.15)
    
    max_iter = 50
    
    # Character ramp for iteration depth
    chars = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    
    all_points = []
    
    # Sample the fractal at screen resolution
    for py in range(height - 1):
        for px in range(width):
            # Map pixel to complex plane
            # Adjust for aspect ratio
            x0 = (px - width / 2) / (width / 4) / zoom + pan_x
            y0 = (py - height / 2) / (height / 2) / zoom + pan_y
            
            x, y = x0, y0
            iteration = 0
            
            # Julia set iteration: z = z^2 + c
            while x*x + y*y <= 4 and iteration < max_iter:
                xtemp = x*x - y*y + cr
                y = 2*x*y + ci
                x = xtemp
                iteration += 1
            
            if iteration < max_iter:
                # Map iteration to character and color
                # Smooth coloring
                log_zn = math.log(x*x + y*y) / 2
                nu = math.log(log_zn / math.log(2)) / math.log(2) if log_zn > 0 else 0
                iteration = iteration + 1 - nu
                
                # Normalize iteration for color mapping
                normalized = iteration / max_iter
                
                # Get character based on iteration
                char_idx = int(normalized * (len(chars) - 1))
                char_idx = max(0, min(len(chars) - 1, char_idx))
                char = chars[char_idx]
                
                # Use iteration as pseudo-depth for 3D effect
                z_depth = 1.0 - normalized  # Higher iteration = further away
                
                color = theme_manager.get_color_for_depth(z_depth, 0, 1)
                buffer.set_pixel(px, py, char, z_depth, color)
    
    return (0, 1)


def render_mandelbrot(buffer, width, height, time, theme_manager):
    """
    Render a Mandelbrot set with animated zoom.
    
    Features:
    - Continuous zoom into interesting regions
    - Smooth coloring
    - Color cycling
    """
    # Interesting zoom targets in the Mandelbrot set
    # Seahorse Valley: (-0.75, 0.1)
    # Elephant Valley: (0.275, 0)
    # Spiral: (-0.761574, -0.0847596)
    
    target_x = -0.761574
    target_y = -0.0847596
    
    # Exponential zoom
    zoom = 0.5 * math.exp(time * 0.1)
    zoom = min(zoom, 1000)  # Cap zoom
    
    max_iter = 80
    
    chars = " .:-=+*#%@"
    
    for py in range(height - 1):
        for px in range(width):
            # Map to complex plane with zoom
            x0 = (px - width / 2) / (width / 4) / zoom + target_x
            y0 = (py - height / 2) / (height / 2) / zoom + target_y
            
            x, y = 0.0, 0.0
            iteration = 0
            
            # Mandelbrot iteration: z = z^2 + c where c is the point
            while x*x + y*y <= 4 and iteration < max_iter:
                xtemp = x*x - y*y + x0
                y = 2*x*y + y0
                x = xtemp
                iteration += 1
            
            if iteration < max_iter:
                # Smooth coloring
                normalized = iteration / max_iter
                
                # Color cycling effect
                hue_shift = (time * 0.5) % 1.0
                normalized = (normalized + hue_shift) % 1.0
                
                char_idx = int(normalized * (len(chars) - 1))
                char = chars[max(0, min(len(chars) - 1, char_idx))]
                
                z_depth = 1.0 - (iteration / max_iter)
                color = theme_manager.get_color_for_depth(z_depth, 0, 1)
                buffer.set_pixel(px, py, char, z_depth, color)
    
    return (0, 1)
