import numpy as np
from shader_engine import run_shader_animation

def generate_betta_fish_lines(t):
    """
    Generates line segments for the Betta Fish based on Hamid Naderi Yeganeh's method.
    Using parametric equations for k=1..2000 to define endpoints of lines.
    
    We generate a list of (x1, y1, x2, y2, color) tuples.
    """
    
    k = np.arange(1, 4001) # More lines for density
    
    # Time injection for animation (undulation)
    # Varies parameters slightly over time
    
    # Formula structure inspired by Yeganeh's "Bird in Flight" and "Fish"
    # We construct a composite body and tail.
    
    # Normalized params
    u = k / 4000.0 * 2 * np.pi
    
    # Body/Tail Oscillation
    wave = np.sin(u * 5 + t * 2) * 0.1
    
    # Endpoint 1 (Body Spine/Upper)
    # x = cos(u) - ...
    x1 = np.cos(u) + 0.5 * np.cos(3*u) 
    y1 = np.sin(u) + 0.5 * np.sin(3*u) + wave
    
    # Endpoint 2 (Fins/Tail Extremities)
    # Detailed parametric scattering
    r2 = 1.5 + 0.5 * np.cos(10*u + t)
    x2 = x1 + r2 * np.cos(u + np.pi + np.sin(5*u)*0.5)
    y2 = y1 + r2 * np.sin(u + np.pi + np.cos(5*u)*0.5)
    
    # Color mapping based on k (u)
    # Betta fish are often Blue/Red/Purple
    # We'll map k to a color gradient 0..1 RGB
    
    # R: 0.2 + 0.8*sin(u)
    # G: 0.1
    # B: 0.5 + 0.5*cos(u)
    
    r_val = 0.4 + 0.6 * np.sin(u)
    g_val = 0.2 + 0.2 * np.cos(u * 3)
    b_val = 0.6 + 0.4 * np.cos(u + 2)
    
    # Stack coords [N, 4]
    coords = np.column_stack((x1, y1, x2, y2))
    colors = np.column_stack((r_val, g_val, b_val))
    
    return coords, colors

def shader_betta_fish(u, v, t):
    """
    Renders the Betta Fish using line rasterization onto the pixel grid.
    Since 'u, v' are grid coordinates, we need to draw the lines onto this grid.
    Input u,v shape: (H, W)
    """
    h, w = u.shape
    
    # Initialize black canvas
    canvas = np.zeros((h, w, 3), dtype=np.float32)
    
    # Generate lines
    lines, line_colors = generate_betta_fish_lines(t)
    
    # Transform lines to Screen Space
    # u range approx [-aspect, aspect], v range [-1, 1]
    # We need to map world coordinates [-2, 2] to pixel indices [0, W], [0, H]
    
    # Aspect ratio
    aspect = w / h
    scale_x = w / (4.0 * aspect) # Zoom to fit [-2*asp, 2*asp] horiz
    scale_y = h / 4.0            # Zoom to fit [-2, 2] vert
    
    center_x = w / 2.0
    center_y = h / 2.0
    
    # Vectorized Line Rasterization (Naive/Splatting)
    # For performance in Python, we can't draw 4000 lines with Bresenham individually in a loop efficiently.
    # Instead, we compute points along the lines and splat them?
    # Or simplified: Compute distance from each pixel to the set of lines? Too slow (H*W*Lines).
    
    # Scatter approach:
    # 1. Sample points ALONG each line.
    # 2. Project points to grid indices.
    # 3. Accumulate colors.
    
    # Discretize lines into points
    steps = 20 # points per line
    alpha = np.linspace(0, 1, steps)
    
    # Broadcasting to create all points
    # lines shape (N, 4) -> x1, y1, x2, y2
    # alpha shape (S,)
    
    # x_points = x1 + (x2-x1)*alpha
    x1 = lines[:, 0:1]
    y1 = lines[:, 1:2]
    x2 = lines[:, 2:3]
    y2 = lines[:, 3:4]
    
    # Resulting shape (N, S)
    batch_x = x1 + (x2 - x1) * alpha
    batch_y = y1 + (y2 - y1) * alpha
    
    # Flatten
    all_x = batch_x.flatten()
    all_y = batch_y.flatten()
    
    # Expand colors to match points (Repeat N colors, S times each)
    # colors shape (N, 3)
    # We need (N*S, 3)
    # np.repeat repeats elements, we need repeat rows
    all_r = np.repeat(line_colors[:, 0], steps)
    all_g = np.repeat(line_colors[:, 1], steps)
    all_b = np.repeat(line_colors[:, 2], steps)
    
    # Map to screen indices
    scr_x = (all_x * scale_x + center_x).astype(int)
    scr_y = (all_y * scale_y + center_y).astype(int)
    
    # Bounds check
    valid = (scr_x >= 0) & (scr_x < w) & (scr_y >= 0) & (scr_y < h)
    
    scr_x = scr_x[valid]
    scr_y = scr_y[valid]
    r_pts = all_r[valid]
    g_pts = all_g[valid]
    b_pts = all_b[valid]
    
    # Accumulate (Splatting)
    # We can use np.add.at for unbuffered accumulation
    # Note: canvas is (H, W, 3)
    
    # We need flattened indices for add.at
    # flat_idx = y * w + x
    flat_indices = scr_y * w + scr_x
    
    # Flatten canvas for operation
    canvas_r = canvas[:,:,0].reshape(-1)
    canvas_g = canvas[:,:,1].reshape(-1)
    canvas_b = canvas[:,:,2].reshape(-1)
    
    np.add.at(canvas_r, flat_indices, r_pts * 0.1) # low alpha for accumulation
    np.add.at(canvas_g, flat_indices, g_pts * 0.1)
    np.add.at(canvas_b, flat_indices, b_pts * 0.1)
    
    # Reshape back
    canvas[:,:,0] = canvas_r.reshape(h, w)
    canvas[:,:,1] = canvas_g.reshape(h, w)
    canvas[:,:,2] = canvas_b.reshape(h, w)
    
    # Clip and Gamma correct?
    # Log compression allows seeing faint structure
    canvas = np.tanh(canvas * 2.0) # Soft clamp
    
    return canvas

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_betta_fish)
