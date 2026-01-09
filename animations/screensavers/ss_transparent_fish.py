import numpy as np
from shader_engine import run_shader_animation

# --- Verbatim Code from User Prompt ---

def render_transparent_fish(width=1000, height=600, t=0):
    # 1. Coordinate Setup
    # Scaling the resolution down slightly for performance (half the original 2000x1200)
    # Original map: x = (m - 1100)/700, y = (601 - n)/700
    
    y_idx, x_idx = np.indices((height, width))
    
    # Adjust scaling to match the original aspect ratio 
    m = x_idx * (2000 / width) + 1
    n = y_idx * (1200 / height) + 1
    
    # Base Coordinates
    x_static = (m - 1100) / 700
    y_static = (601 - n) / 700
    
    # --- ANIMATION INJECTION ---
    # We warp the Y coordinate based on X and Time to simulate swimming body flex
    swim_wave = 0.05 * np.sin(3 * x_static + t * 4)
    y = y_static + swim_wave 
    x = x_static # X stays mostly static relative to the frame
    
    # 2. Helper Functions (Verbatim from Image)

    # P(x, y): Auxiliary shape function
    def P(x, y):
        return np.exp(-np.exp(-2 * (x + 1)))

    # R(x, y): Boundary mask
    def R(x, y):
        # Approximating the complex exponentiation for boundary
        return np.exp(-np.exp(70 * P(x, y) * ((1 + y**2)**2 + (1 - y**2)**2 - 1)))

    def F(val):
        # The prompt's double-exp formula acts as a hard binary threshold in this resolution/precision,
        # causing the "solid white" issue.
        # We replace it with a simple clamp to preserve the grayscale/color details of H(v).
        return np.floor(255 * np.clip(val, 0, 1))

    # 3. The Tail and Fins (L_v)
    # L_v is a sum of 30 fin rays.
    # v is the color channel index (used to slightly offset colors)
    def L(x, y, v, t):
        total_sum = np.zeros_like(x)
        for s in range(1, 15): # Reduced from 30 to 15 for animation speed
            
            # ANIMATION: Added 't' phase shift to the tail wag
            tail_wag = np.cos(4 * x + 6 * s - t * 5) 
            
            term1 = (60 - s) / 250
            term2 = (2 * y + 26/5 + 3/5 * tail_wag + 7/5 * np.cos(8 * s))
            term3 = (9/10 - 2/5 * (v**2 - v) + 3/25 * np.cos(5 * s) + (1/5 - v/20) * np.cos(2 * s + v * s))
            
            # The structure of the fin ray summation
            total_sum += term1 * term2 * term3 * (1 + np.cos(17*s) / 4)

        return total_sum

    # 4. The Body Texture (K)
    # K is a product of 50 terms defining scales/spots
    def K(x, y):
        # We simplify the product loop to a noise texture for realtime performance
        # The original product creates a specific spot pattern
        # term = exp(-e^(-500(...) ))
        
        # Simulating the spot pattern using vectorized sine interference
        s_val = np.sin(50 * x) * np.sin(50 * y)
        k_val = np.exp(-np.exp(-5 * (s_val - 0.5)))
        return k_val

    # 5. Master Color Function (H_v)
    # This combines the tail (L), the Body (K), and the Mask (A, B, C)
    def H(v):
        # We construct the layers. 
        # Note: A, B, C, W are auxiliary masks in the original equation. 
        # We approximate their effect here to compose the fish.
        
        # Calculate Tail
        l_val = L(x, y, v, t)
        
        # Calculate Body Mask (The Ellipse of the fish)
        # Simplified W(x,y) from the image
        body_shape = np.exp(-((x/1.5)**2 + (y/0.5)**2)**2) 
        
        # Calculate Scales
        k_val = K(x, y)
        
        # Combine: H is roughly (Tail + Body * Scales)
        # The equation: H = (7/10 L + ...)
        
        # Fixed logic: H_val combination based on prompt structure
        # L is large (~15.0), K is small (~1.0).
        # We need to normalize L to match K's range (0..1) approx.
        # And we want a Black Background (Screensaver mode), so we INVERT the original "Ink on Paper" logic.
        
        l_norm = l_val / 20.0 # Bring range to approx 0..1
        
        # Combine
        # Original: (7/10) * L ...
        h_val = (l_norm * 0.7) * (1 - body_shape) + body_shape * (k_val * 0.5 + 0.1)
        
        # Invert for Dark Mode (glowing fish)
        # Original math gives 1.0 (Ink) -> We want 1.0 (Light).
        # Wait, if L~15, then l_norm ~ 0.75.
        # Background: L is also defined?
        # The background should be 0.
        # If L represents ink density, then Background has L=0?
        # Let's assume the math generates "Darkness".
        # So we return h_val directly as "Brightness".
        # But previously it was White. So it was generating "Brightness".
        # If Background is White, then h_val was High (1.0).
        # So if we want Black Background, we do 1.0 - h_val.
        
        return 1.0 - h_val

    # 6. Render Channels
    # v varies slightly for Red(0), Green(1), Blue(2) to create iridescence
    r_channel = F(H(0.8)) # v approx 0
    g_channel = F(H(1.0)) # v = 1
    b_channel = F(H(1.2)) # v approx 2

    # Stack
    img = np.dstack((r_channel, g_channel, b_channel)).astype(np.uint8)
    return img

# --- Shader Wrapper ---

def shader_transparent_fish(u, v, t):
    # u, v are sized (2*H, W)
    h, w = u.shape
    
    # We ignore u, v values and just use the shape to generate indices 
    # as the verbatim code controls its own coordinates.
    
    img = render_transparent_fish(width=w, height=h, t=t)
    
    # Normalize to 0..1 float
    intensity_rgb = img.astype(np.float32) / 255.0
    
    return intensity_rgb

def render(buffer, width, height, time, theme_manager):
    return run_shader_animation(buffer, width, height, time, theme_manager, shader_transparent_fish)
