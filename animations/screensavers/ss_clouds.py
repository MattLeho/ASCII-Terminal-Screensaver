"""
Tiny Planet Clouds Screensaver
Numpy Optimized.
Based on Shadertoy 'Tiny Planet Clouds' by nimitz
https://www.shadertoy.com/view/ldyXRw

This is a simplified version using vectorized raymarching.
Architecture: Fixed-iteration raymarch without loops in shader function.
"""

import numpy as np

# Constants
PLANET_RADIUS = 1.0
MAX_HEIGHT = 0.4
MAX_RAY_DIST = MAX_HEIGHT * 4.0
PI = 3.14159265359

def fract(x):
    """GLSL fract - fractional part."""
    return x - np.floor(x)

def mix(a, b, t):
    """GLSL mix - linear interpolation."""
    return a * (1.0 - t) + b * t

def clamp(x, low, high):
    """GLSL clamp."""
    return np.clip(x, low, high)

def normalize(v):
    """Normalize vectors along last axis."""
    norm = np.sqrt(np.sum(v**2, axis=-1, keepdims=True))
    return v / np.maximum(norm, 1e-9)

def length(v):
    """Vector length along last axis."""
    return np.sqrt(np.sum(v**2, axis=-1))

def dot(a, b):
    """Dot product along last axis."""
    return np.sum(a * b, axis=-1)

def hash_iq(n):
    """Simple hash function for noise."""
    return fract(np.sin(n) * 753.5453123)

def noise_iq(x, y, z):
    """
    3D value noise based on IQ's implementation.
    """
    px = np.floor(x)
    py = np.floor(y)
    pz = np.floor(z)
    
    fx = x - px
    fy = y - py
    fz = z - pz
    
    # Smooth interpolation
    fx = fx * fx * (3.0 - 2.0 * fx)
    fy = fy * fy * (3.0 - 2.0 * fy)
    fz = fz * fz * (3.0 - 2.0 * fz)
    
    # Hash based on position indices
    n = px + py * 157.0 + pz * 113.0
    
    # 8 corners
    h000 = hash_iq(n)
    h100 = hash_iq(n + 1.0)
    h010 = hash_iq(n + 157.0)
    h110 = hash_iq(n + 158.0)
    h001 = hash_iq(n + 113.0)
    h101 = hash_iq(n + 114.0)
    h011 = hash_iq(n + 270.0)
    h111 = hash_iq(n + 271.0)
    
    # Trilinear interpolation
    h00 = mix(h000, h100, fx)
    h10 = mix(h010, h110, fx)
    h01 = mix(h001, h101, fx)
    h11 = mix(h011, h111, fx)
    
    h0 = mix(h00, h10, fy)
    h1 = mix(h01, h11, fy)
    
    return mix(h0, h1, fz)

def fbm(x, y, z, octaves=4, lacunarity=2.0276, init_gain=0.5, gain=0.5):
    """Fractional Brownian Motion noise."""
    value = np.zeros_like(x)
    amplitude = init_gain
    freq = 1.0
    
    for _ in range(octaves):
        value = value + amplitude * noise_iq(x * freq, y * freq, z * freq)
        freq *= lacunarity
        amplitude *= gain
    
    return value

def fbm_clouds(x, y, z, octaves=4):
    """FBM for clouds using absolute noise (billowy look)."""
    value = np.zeros_like(x)
    amplitude = 0.5
    freq = 1.0
    
    for _ in range(octaves):
        # Absolute noise: abs(noise * 2 - 1)
        n = noise_iq(x * freq, y * freq, z * freq)
        n = np.abs(n * 2.0 - 1.0)
        value = value + amplitude * n
        freq *= 2.0276
        amplitude *= 0.5
    
    return value

def smoothstep(edge0, edge1, x):
    """GLSL smoothstep."""
    t = clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)

def band(start, peak, end, t):
    """Band function for height-based effects."""
    return smoothstep(start, peak, t) * (1.0 - smoothstep(peak, end, t))

def sdf_terrain(pos_x, pos_y, pos_z):
    """
    Signed distance to terrain surface.
    Returns (distance, height_fraction)
    """
    # Terrain = sphere + FBM displacement
    r = np.sqrt(pos_x**2 + pos_y**2 + pos_z**2)
    
    # FBM terrain (High Detail)
    # Increased octaves to 5 for max detail
    h0 = fbm(pos_x * 2.0987, pos_y * 2.0987, pos_z * 2.0987, octaves=5)
    n0 = smoothstep(0.35, 1.0, h0)
    
    # Ridged noise for mountains (High Detail)
    h1_raw = fbm(pos_x * 1.50987 + 1.9489, pos_y * 1.50987 + 2.435, pos_z * 1.50987 + 0.5483, octaves=5)
    h1 = 1.0 - np.abs(h1_raw * 2.0 - 1.0)  # Ridged
    n1 = smoothstep(0.6, 1.0, h1)
    
    n = n0 + n1
    
    distance = r - PLANET_RADIUS - n * MAX_HEIGHT
    height_frac = n / MAX_HEIGHT
    
    return distance, height_frac

def intersect_sphere(ray_origin, ray_dir, radius):
    """
    Ray-sphere intersection at origin.
    Returns t (distance) or inf if no hit.
    """
    # Quadratic: |o + t*d|^2 = r^2
    # t^2*|d|^2 + 2t*(o.d) + |o|^2 - r^2 = 0
    
    a = dot(ray_dir, ray_dir)
    b = 2.0 * dot(ray_origin, ray_dir)
    c = dot(ray_origin, ray_origin) - radius * radius
    
    discriminant = b * b - 4.0 * a * c
    
    # No intersection where discriminant < 0
    valid = discriminant >= 0
    
    sqrt_disc = np.sqrt(np.maximum(discriminant, 0))
    t0 = (-b - sqrt_disc) / (2.0 * a)
    t1 = (-b + sqrt_disc) / (2.0 * a)
    
    # Take nearest positive t
    t = np.where(t0 > 0, t0, t1)
    t = np.where(valid & (t > 0), t, np.inf)
    
    return t

def shader_clouds(u, v, t):
    """
    Tiny Planet Clouds shader.
    Uses vectorized raymarching to render a small planet with terrain and clouds.
    """
    H, W = u.shape
    
    # Camera setup (looking at planet from distance)
    cam_dist = 2.5
    fov = np.tan(np.radians(30))
    
    # Ray origin (camera position)
    ray_origin = np.zeros((H, W, 3))
    ray_origin[..., 2] = -cam_dist  # Camera at z = -2.5
    
    # Ray direction (perspective projection)
    ray_dir = np.zeros((H, W, 3))
    ray_dir[..., 0] = u * fov
    ray_dir[..., 1] = v * fov
    ray_dir[..., 2] = 1.0
    ray_dir = normalize(ray_dir)
    
    # Rotation matrices for animation
    angle_y = t * -12.0 * PI / 180.0  # Slow rotation
    angle_x = t * 8.0 * PI / 180.0
    
    cos_y, sin_y = np.cos(angle_y), np.sin(angle_y)
    cos_x, sin_x = np.cos(angle_x), np.sin(angle_x)
    
    # Intersect with atmosphere (planet + max_height)
    atmo_radius = PLANET_RADIUS + MAX_HEIGHT
    t_hit = intersect_sphere(ray_origin, ray_dir, atmo_radius)
    
    # Initialize output color (sky background)
    sky_color = np.zeros((H, W, 3))
    sky_color[..., 0] = 0.0
    sky_color[..., 1] = 0.05
    sky_color[..., 2] = 0.2
    
    # Sun effect
    sun_amount = ray_dir[..., 2]  # Facing forward = towards sun
    sun_color = np.zeros((H, W, 3))
    sun_color[..., 0] = 1.0
    sun_color[..., 1] = 0.9
    sun_color[..., 2] = 0.55
    
    sun_glow = np.clip(sun_amount ** 10 * 0.6, 0, 1)
    for c in range(3):
        sky_color[..., c] = sky_color[..., c] + sun_color[..., c] * sun_glow
    
    # Hit mask
    hit_atmo = t_hit < np.inf
    
    # Get hit positions
    # sanitize t_hit: replace inf with 0.0 (or max dist) to prevent NaNs in hit_pos
    t_safe = np.where(hit_atmo, t_hit, 0.0)
    hit_pos = ray_origin + ray_dir * t_safe[..., np.newaxis]
    
    # Vectorized raymarching (20 steps)
    RAYMARCH_STEPS = 20
    step_size = MAX_RAY_DIST / RAYMARCH_STEPS
    
    # Initialize march distance
    march_t = np.zeros((H, W))
    final_dist = np.full((H, W), np.inf)
    final_height = np.zeros((H, W))
    
    # RELAXED TOLERANCE for terminal rendering
    MIN_DIST = 0.02
    
    for i in range(RAYMARCH_STEPS):
        # Current position along ray
        pos = hit_pos + ray_dir * march_t[..., np.newaxis]
        
        # Apply rotation to position (rotate terrain under camera)
        # Simplified rotation: Y-axis
        pos_x = pos[..., 0] * cos_y + pos[..., 2] * sin_y
        pos_z = -pos[..., 0] * sin_y + pos[..., 2] * cos_y
        pos_y = pos[..., 1]
        
        # Get SDF
        dist, height = sdf_terrain(pos_x, pos_y, pos_z)
        
        # Update march distance
        march_t = march_t + np.maximum(dist, 0.005) * 0.7 # Safer step
        
        # Record hit
        # Relaxed condition: dist < MIN_DIST and inside atmosphere
        hit_terrain = (dist < MIN_DIST) & hit_atmo & (final_dist == np.inf)
        final_dist = np.where(hit_terrain, march_t, final_dist)
        final_height = np.where(hit_terrain, height, final_height)
    
    # Terrain coloring
    h = final_height
    
    # Material colors
    c_water = np.array([0.015, 0.110, 0.455])
    c_grass = np.array([0.086, 0.132, 0.018])
    c_beach = np.array([0.153, 0.172, 0.121])
    c_rock = np.array([0.080, 0.050, 0.030])
    c_snow = np.array([0.600, 0.600, 0.600])
    
    # Height-based material blending
    terrain_color = np.zeros((H, W, 3))
    
    # Water to shore
    for c in range(3):
        shore = mix(c_beach[c], c_grass[c], smoothstep(0.17, 0.21, h))
        rock = mix(shore, c_rock[c], smoothstep(0.21, 0.35, h))
        snow = mix(rock, c_snow[c], smoothstep(0.5, 0.7, h))
        water = mix(c_water[c] * 0.5, c_water[c], smoothstep(0.0, 0.05, h))
        terrain_color[..., c] = mix(water, snow, smoothstep(0.05, 0.17, h))
    
    # Simple lighting
    terrain_color = terrain_color * (0.5 + 0.5 * final_height[..., np.newaxis])
    
    # Cloud layer (simplified)
    cloud_dens = fbm_clouds(
        hit_pos[..., 0] * 3.2343 + 0.35,
        hit_pos[..., 1] * 3.2343 + 13.35,
        hit_pos[..., 2] * 3.2343 + 2.67 + t * 0.1,
        octaves=3
    )
    
    # Coverage threshold
    cloud_vis = smoothstep(0.3, 0.5, cloud_dens)
    
    # Apply clouds on top of terrain
    cloud_color = np.ones((H, W, 3)) * 0.9  # White clouds
    
    # Composite
    hit_terrain_mask = (final_dist < np.inf)
    
    output_color = sky_color.copy()
    for c in range(3):
        # Terrain where hit
        output_color[..., c] = np.where(hit_terrain_mask, terrain_color[..., c], output_color[..., c])
        
        # Clouds on top
        # Mix cloud color based on visibility and atmosphere hit
        current = output_color[..., c]
        clouded = mix(current, cloud_color[..., c], cloud_vis * 0.7)
        output_color[..., c] = np.where(hit_atmo, clouded, current)
    
    # Atmospheric Halo / Glow
    # Vectorized Atmosphere Glow
    
    # Calculate sphere normal at hit
    sp_norm = normalize(hit_pos)
    dot_view = dot(sp_norm, -ray_dir)
    # Rim lighting
    rim = np.power(1.0 - np.maximum(dot_view, 0.0), 3.0)
    
    halo_color = np.array([0.4, 0.6, 1.0]) # Blue atmosphere
    
    # Add rim glow
    rim_mask = hit_atmo & (final_dist < np.inf) # Only on planet
    
    for c in range(3):
        output_color[..., c] = np.where(rim_mask, 
            output_color[..., c] + halo_color[c] * rim * 0.5,
            output_color[..., c])
    
    # Gamma correction (linear to sRGB)
    output_color = np.clip(output_color, 0.0, 1.0)
    output_color = output_color ** (1.0 / 2.2)
    
    return output_color

def render(buffer, width, height, time, theme_manager):
    """Standard render function for integration with shader engine."""
    from shader_engine import run_shader_animation
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_clouds)
