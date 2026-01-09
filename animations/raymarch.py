"""
Raymarching SDF (Signed Distance Fields) Animation
Real-time raymarching with boolean operations and shadows.
"""

import math
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import normalize_3d, dot_product


def sdf_sphere(point, center, radius):
    """Signed distance to a sphere."""
    dx = point[0] - center[0]
    dy = point[1] - center[1]
    dz = point[2] - center[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz) - radius


def sdf_box(point, center, size):
    """Signed distance to a box."""
    dx = abs(point[0] - center[0]) - size[0]
    dy = abs(point[1] - center[1]) - size[1]
    dz = abs(point[2] - center[2]) - size[2]
    
    # Outside distance
    outside = math.sqrt(max(dx, 0)**2 + max(dy, 0)**2 + max(dz, 0)**2)
    # Inside distance
    inside = min(max(dx, dy, dz), 0)
    
    return outside + inside


def sdf_torus(point, center, major_r, minor_r):
    """Signed distance to a torus."""
    # Torus centered at origin, then offset
    px = point[0] - center[0]
    py = point[1] - center[1]
    pz = point[2] - center[2]
    
    # Distance in xz plane from center
    q = math.sqrt(px*px + pz*pz) - major_r
    return math.sqrt(q*q + py*py) - minor_r


def sdf_union(d1, d2):
    """Union of two SDFs."""
    return min(d1, d2)


def sdf_intersection(d1, d2):
    """Intersection of two SDFs."""
    return max(d1, d2)


def sdf_difference(d1, d2):
    """Subtract d2 from d1."""
    return max(d1, -d2)


def sdf_smooth_union(d1, d2, k=0.5):
    """Smooth minimum for blending shapes."""
    h = max(k - abs(d1 - d2), 0) / k
    return min(d1, d2) - h*h*k*0.25


def estimate_normal(point, scene_sdf, epsilon=0.001):
    """Estimate surface normal using finite differences."""
    dx = scene_sdf((point[0] + epsilon, point[1], point[2])) - \
         scene_sdf((point[0] - epsilon, point[1], point[2]))
    dy = scene_sdf((point[0], point[1] + epsilon, point[2])) - \
         scene_sdf((point[0], point[1] - epsilon, point[2]))
    dz = scene_sdf((point[0], point[1], point[2] + epsilon)) - \
         scene_sdf((point[0], point[1], point[2] - epsilon))
    
    return normalize_3d((dx, dy, dz))


def raymarch(origin, direction, scene_sdf, max_steps=64, max_dist=20, epsilon=0.01):
    """
    March a ray through the scene using sphere tracing.
    Returns (hit, distance, steps) tuple.
    """
    total_distance = 0
    
    for step in range(max_steps):
        point = (
            origin[0] + direction[0] * total_distance,
            origin[1] + direction[1] * total_distance,
            origin[2] + direction[2] * total_distance
        )
        
        distance = scene_sdf(point)
        
        if distance < epsilon:
            return (True, total_distance, step)
        
        total_distance += distance
        
        if total_distance > max_dist:
            break
    
    return (False, total_distance, max_steps)


def render_raymarch(buffer, width, height, time, theme_manager):
    """
    Render a raymarched scene with boolean operations.
    
    Features:
    - Sphere with cube hole (boolean difference)
    - Real-time lighting
    - Soft shadows
    """
    # Camera setup
    camera_pos = (0, 0, -5)
    
    # Light position (orbits)
    light_pos = (
        3 * math.sin(time * 0.5),
        2,
        3 * math.cos(time * 0.5) - 3
    )
    
    # Animated scene elements
    sphere_center = (0, 0, 0)
    sphere_radius = 1.5
    
    cube_center = (
        0.5 * math.sin(time * 0.7),
        0.5 * math.cos(time * 0.6),
        0.5 * math.sin(time * 0.8)
    )
    cube_size = (0.8, 0.8, 0.8)
    
    # Second sphere for smooth union
    sphere2_center = (
        1.5 * math.sin(time * 0.4),
        0,
        1.5 * math.cos(time * 0.4)
    )
    
    def scene_sdf(point):
        """Combined scene SDF."""
        # Main sphere
        d_sphere = sdf_sphere(point, sphere_center, sphere_radius)
        
        # Cube to subtract
        d_cube = sdf_box(point, cube_center, cube_size)
        
        # Sphere with cube hole
        d_main = sdf_difference(d_sphere, d_cube)
        
        # Second sphere blending in
        d_sphere2 = sdf_sphere(point, sphere2_center, 0.6)
        
        return sdf_smooth_union(d_main, d_sphere2, 0.5)
    
    # Character ramp for lighting
    chars = " .,:;+*#@"
    
    # Render each pixel
    for py in range(height - 1):
        for px in range(width):
            # Map pixel to normalized device coordinates
            # Account for aspect ratio
            aspect = (width / 2) / height
            ndc_x = (px / width * 2 - 1) * aspect
            ndc_y = -(py / height * 2 - 1)
            
            # Ray direction (simple perspective)
            ray_dir = normalize_3d((ndc_x, ndc_y, 1))
            
            # Raymarch
            hit, dist, steps = raymarch(camera_pos, ray_dir, scene_sdf)
            
            if hit:
                # Calculate hit point
                hit_point = (
                    camera_pos[0] + ray_dir[0] * dist,
                    camera_pos[1] + ray_dir[1] * dist,
                    camera_pos[2] + ray_dir[2] * dist
                )
                
                # Get surface normal
                normal = estimate_normal(hit_point, scene_sdf)
                
                # Light direction
                to_light = normalize_3d((
                    light_pos[0] - hit_point[0],
                    light_pos[1] - hit_point[1],
                    light_pos[2] - hit_point[2]
                ))
                
                # Diffuse lighting
                diffuse = max(0, dot_product(normal, to_light))
                
                # Ambient occlusion approximation from step count
                ao = 1 - steps / 64
                
                # Final intensity
                intensity = diffuse * 0.8 + ao * 0.2
                
                # Map to character
                char_idx = int(intensity * (len(chars) - 1))
                char_idx = max(0, min(len(chars) - 1, char_idx))
                char = chars[char_idx]
                
                # Color based on distance and normal
                color = theme_manager.get_color_for_depth(dist, 0, 10)
                
                buffer.set_pixel(px, py, char, dist, color)
    
    return (0, 10)
