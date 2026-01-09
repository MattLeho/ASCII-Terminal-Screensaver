"""
Perlin Noise Terrain Animation
An infinite scrolling mountainscape.
Enhanced with larger scale and continuous scrolling motion.
"""

import math
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import rotate_x, rotate_y, project_point


class PerlinNoise:
    """Simple Perlin-like noise generator."""
    
    def __init__(self, seed=42):
        random.seed(seed)
        self.permutation = list(range(256))
        random.shuffle(self.permutation)
        self.permutation += self.permutation
    
    def fade(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, a, b, t):
        return a + t * (b - a)
    
    def grad(self, hash_val, x, y):
        h = hash_val & 3
        if h == 0:
            return x + y
        elif h == 1:
            return -x + y
        elif h == 2:
            return x - y
        else:
            return -x - y
    
    def noise2d(self, x, y):
        X = int(math.floor(x)) & 255
        Y = int(math.floor(y)) & 255
        
        x -= math.floor(x)
        y -= math.floor(y)
        
        u = self.fade(x)
        v = self.fade(y)
        
        p = self.permutation
        A = p[X] + Y
        B = p[X + 1] + Y
        
        return self.lerp(
            self.lerp(self.grad(p[A], x, y), self.grad(p[B], x - 1, y), u),
            self.lerp(self.grad(p[A + 1], x, y - 1), self.grad(p[B + 1], x - 1, y - 1), u),
            v
        )
    
    def octave_noise(self, x, y, octaves=4, persistence=0.5):
        total = 0
        amplitude = 1
        frequency = 1
        max_value = 0
        
        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= 2
        
        return total / max_value


_noise = PerlinNoise()


def render_terrain(buffer, width, height, time, theme_manager):
    """
    Render a scrolling Perlin noise terrain.
    
    Features:
    - Continuous scrolling motion
    - Slow rotation for 3D effect
    - Larger scale for visibility
    """
    # Terrain parameters - LARGER
    terrain_width = 40
    terrain_depth = 25
    height_scale = 3.0
    noise_scale = 0.12
    scroll_speed = 0.6
    
    # Viewing angles with slow rotation
    rot_x = 0.75
    rot_y = math.sin(time * 0.15) * 0.15  # Gentle side-to-side
    
    all_z = []
    points_to_draw = []
    
    # Continuous scroll offset
    scroll_offset = time * scroll_speed
    
    for i in range(terrain_depth):
        z_pos = i * 0.45
        
        for j in range(terrain_width):
            x_pos = (j - terrain_width / 2) * 0.28
            
            # Sample noise with scroll
            noise_x = j * noise_scale
            noise_y = (i + scroll_offset * 2) * noise_scale
            
            # Multi-octave noise for natural terrain
            height_val = _noise.octave_noise(noise_x, noise_y, octaves=4)
            
            y_pos = height_val * height_scale
            
            x = x_pos
            y = y_pos
            z = z_pos
            
            # Apply rotations
            point = rotate_x((x, y, z), rot_x)
            point = rotate_y(point, rot_y)
            x, y, z = point
            
            y -= 0.8
            
            projected = project_point(x, y, z, width, height, distance=5.0)
            if projected:
                all_z.append(z)
                points_to_draw.append((projected[0], projected[1], z, height_val))
    
    if not all_z:
        return (0, 1)
    
    z_min, z_max = min(all_z), max(all_z)
    
    # Height-based characters
    terrain_chars = "_.,-~:;!^*#A"
    
    heights = [p[3] for p in points_to_draw]
    if heights:
        h_min, h_max = min(heights), max(heights)
    else:
        h_min, h_max = -1, 1
    
    for screen_x, screen_y, z, h in points_to_draw:
        if h_max != h_min:
            h_normalized = (h - h_min) / (h_max - h_min)
        else:
            h_normalized = 0.5
        
        char_idx = int(h_normalized * (len(terrain_chars) - 1))
        char = terrain_chars[max(0, min(len(terrain_chars) - 1, char_idx))]
        
        color = theme_manager.get_color_for_depth(z, z_min, z_max)
        
        buffer.set_pixel(screen_x, screen_y, char, z, color)
    
    return (z_min, z_max)
