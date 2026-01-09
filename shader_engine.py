"""
Shader Engine for Terminal (Numpy Optimized)
Handles high-resolution "fragment shader" style rendering using Numpy vectorization.
Supports two rendering modes:
  - Block Mode: Uses ▀▄█ characters (2x vertical resolution)
  - Braille Mode: Uses Unicode Braille patterns U+2800-U+28FF (2x4 = 8 sub-pixels per cell)
"""

import sys
import numpy as np

# ============================================================================
# Braille Constants (from drawille library analysis)
# ============================================================================
# Braille dot layout:
#    ,___,
#    |1 4|  <- row 0
#    |2 5|  <- row 1
#    |3 6|  <- row 2
#    |7 8|  <- row 3
#    `````
# 
# Each dot maps to a specific bit:
#   Dot 1 = bit 0 (0x01), Dot 4 = bit 3 (0x08)
#   Dot 2 = bit 1 (0x02), Dot 5 = bit 4 (0x10)
#   Dot 3 = bit 2 (0x04), Dot 6 = bit 5 (0x20)
#   Dot 7 = bit 6 (0x40), Dot 8 = bit 7 (0x80)

BRAILLE_OFFSET = 0x2800

# Pixel map: [row][col] -> bit value
# Shape: (4, 2) for 4 rows x 2 cols per Braille cell
BRAILLE_PIXEL_MAP = np.array([
    [0x01, 0x08],  # Row 0: dots 1, 4
    [0x02, 0x10],  # Row 1: dots 2, 5
    [0x04, 0x20],  # Row 2: dots 3, 6
    [0x40, 0x80]   # Row 3: dots 7, 8
], dtype=np.uint8)


class ShaderRenderer:
    def __init__(self, width, height, theme_manager, use_braille=False):
        """
        Initialize the shader renderer.
        
        Args:
            width: Terminal width in characters
            height: Terminal height in characters
            theme_manager: Theme manager for color gradients
            use_braille: If True, use Braille mode (2x4 sub-pixels per cell)
                         If False, use Block mode (1x2 sub-pixels per cell)
        """
        self.width = width
        self.height = height
        self.theme_manager = theme_manager
        self.use_braille = use_braille
        
        # Virtual resolution depends on mode
        if use_braille:
            # Braille: 2 horizontal x 4 vertical sub-pixels per cell
            self.virt_width = width * 2
            self.virt_height = height * 4
        else:
            # Block: 1 horizontal x 2 vertical sub-pixels per cell
            self.virt_width = width
            self.virt_height = height * 2
        
        # Precompute Bayer Matrix for dithering (4x4)
        self.bayer = np.array([
            [ 0,  8,  2, 10], 
            [12,  4, 14,  6], 
            [ 3, 11,  1,  9], 
            [15,  7, 13,  5]
        ]) * (1.0/16.0) - 0.5  # Center around 0
        
        # Precompute UV coordinates for all virtual pixels
        aspect = width / height
        
        # Y coordinates: y=0 -> 1.0 (top), y=virt_height -> -1.0 (bottom)
        y_indices = np.arange(self.virt_height)
        v = 1.0 - (y_indices / self.virt_height) * 2.0
        
        # X coordinates
        x_indices = np.arange(self.virt_width)
        u = (x_indices / self.virt_width) * 2.0 - 1.0
        u = u * aspect
        
        # Create Meshgrid
        self.U, self.V = np.meshgrid(u, v)
        
        # Tile bayer to match virtual size
        self.dither_map = np.tile(self.bayer, (self.virt_height // 4 + 1, self.virt_width // 4 + 1))
        self.dither_map = self.dither_map[:self.virt_height, :self.virt_width]
        self.dither_magnitude = 0.15  # Strength of dithering

    def render(self, buffer, time, shader_func):
        """
        Renders a frame using the provided shader function via Numpy.
        """
        # Call shader function with U, V arrays
        intensity = shader_func(self.U, self.V, time)
        
        is_rgb = (intensity.ndim == 3 and intensity.shape[-1] == 3)
        
        if is_rgb:
            # Compute luminance for masking
            luminance = (0.299 * intensity[..., 0] + 
                         0.587 * intensity[..., 1] + 
                         0.114 * intensity[..., 2])
            
            # Apply dithering
            luminance = luminance + self.dither_map * self.dither_magnitude
            luminance = np.clip(luminance, 0.0, 1.0)
            
            color_data = np.clip(intensity, 0.0, 1.0)
        else:
            # Monochrome
            luminance = intensity + self.dither_map * self.dither_magnitude
            luminance = np.clip(luminance, 0.0, 1.0)
            color_data = None
        
        # Route to appropriate rendering method
        if self.use_braille:
            self._render_braille(buffer, luminance, color_data, is_rgb)
        else:
            self._render_blocks(buffer, luminance, color_data, is_rgb)
    
    def _render_blocks(self, buffer, luminance, color_data, is_rgb):
        """
        Render using block characters (▀▄█).
        2 virtual rows -> 1 terminal row.
        """
        # Pack 2 virtual rows into 1 terminal row
        top_rows = luminance[0::2, :]
        bot_rows = luminance[1::2, :]
        
        threshold = 0.15
        is_top = top_rows > threshold
        is_bot = bot_rows > threshold
        
        # Mask encoding: 0=empty, 1=bot, 2=top, 3=both
        mask = (is_top.astype(int) * 2) + is_bot.astype(int)
        
        # Color handling
        if is_rgb:
            top_rgb = color_data[0::2, :, :]
            bot_rgb = color_data[1::2, :, :]
            
            cell_rgb = np.zeros_like(top_rgb)
            mask_expanded = mask[..., np.newaxis]
            
            # Case 3 (Both): Average
            cell_rgb = np.where(mask_expanded == 3, (top_rgb + bot_rgb) * 0.5, cell_rgb)
            # Case 2 (Top)
            cell_rgb = np.where(mask_expanded == 2, top_rgb, cell_rgb)
            # Case 1 (Bot)
            cell_rgb = np.where(mask_expanded == 1, bot_rgb, cell_rgb)
            
            cell_rgb_int = (cell_rgb * 255).astype(int)
        else:
            cell_intensity = np.zeros_like(top_rows)
            cell_intensity = np.where(mask == 3, (top_rows + bot_rows) * 0.5, cell_intensity)
            cell_intensity = np.where(mask == 2, top_rows, cell_intensity)
            cell_intensity = np.where(mask == 1, bot_rows, cell_intensity)
            
            grad_len = len(self.theme_manager.gradient)
            grad_indices = (cell_intensity * (grad_len - 1)).astype(int)
            grad_indices = np.clip(grad_indices, 0, grad_len - 1)
            gradient = np.array(self.theme_manager.gradient)
            colors_array = gradient[grad_indices]
        
        # Character array
        chars = np.full(mask.shape, ' ', dtype='<U1')
        chars[mask == 1] = '▄'
        chars[mask == 2] = '▀'
        chars[mask == 3] = '█'
        
        # Write to buffer
        self._write_to_buffer(buffer, chars, mask, is_rgb, 
                              cell_rgb_int if is_rgb else None,
                              colors_array if not is_rgb else None)
    
    def _render_braille(self, buffer, luminance, color_data, is_rgb):
        """
        Render using Braille characters (U+2800 to U+28FF).
        2x4 virtual pixels -> 1 terminal cell.
        """
        H, W = self.height, self.width
        
        # Binary threshold
        threshold = 0.3
        binary = (luminance > threshold).astype(np.uint8)
        
        # Reshape to group sub-pixels: (H, 4, W, 2)
        # From shape (H*4, W*2) to (H, 4, W, 2)
        grouped = binary.reshape(H, 4, W, 2)
        
        # Apply bitmask weights using einsum or broadcasting
        # BRAILLE_PIXEL_MAP has shape (4, 2)
        # We want to multiply grouped (H, 4, W, 2) by weights (4, 2) and sum over (4, 2) axes
        
        # Expand weights for broadcasting: (1, 4, 1, 2)
        weights = BRAILLE_PIXEL_MAP[np.newaxis, :, np.newaxis, :]
        
        # Multiply and sum: result shape (H, W)
        bitmasks = (grouped * weights).sum(axis=(1, 3)).astype(np.uint16)
        
        # Convert bitmasks to Braille Unicode characters
        # Using vectorized chr (via numpy char operations)
        chars = np.empty((H, W), dtype='<U1')
        for y in range(H):
            for x in range(W):
                chars[y, x] = chr(BRAILLE_OFFSET + bitmasks[y, x])
        
        # Mask: any subpixel lit = cell active
        mask = (bitmasks > 0).astype(int)
        
        # Color handling
        if is_rgb:
            # Reshape color data: (H*4, W*2, 3) -> (H, 4, W, 2, 3)
            grouped_rgb = color_data.reshape(H, 4, W, 2, 3)
            
            # Average color per cell
            cell_rgb = grouped_rgb.mean(axis=(1, 3))  # (H, W, 3)
            cell_rgb_int = (np.clip(cell_rgb, 0, 1) * 255).astype(int)
            colors_array = None
        else:
            # Use gradient based on average luminance per cell
            grouped_lum = luminance.reshape(H, 4, W, 2)
            cell_intensity = grouped_lum.mean(axis=(1, 3))
            
            grad_len = len(self.theme_manager.gradient)
            grad_indices = (cell_intensity * (grad_len - 1)).astype(int)
            grad_indices = np.clip(grad_indices, 0, grad_len - 1)
            gradient = np.array(self.theme_manager.gradient)
            colors_array = gradient[grad_indices]
            cell_rgb_int = None
        
        # Write to buffer
        self._write_to_buffer(buffer, chars, mask, is_rgb, cell_rgb_int, colors_array)
    
    def _write_to_buffer(self, buffer, chars, mask, is_rgb, cell_rgb_int, colors_array):
        """
        Write computed characters and colors to the screen buffer.
        """
        from colors import fg_rgb
        
        h, w = mask.shape
        
        for y in range(h):
            row_chars = chars[y]
            row_mask = mask[y]
            
            if is_rgb:
                row_rgb_vals = cell_rgb_int[y]
            else:
                row_colors = colors_array[y]
            
            active_indices = np.where(row_mask > 0)[0]
            
            for x in active_indices:
                buffer.chars[y][x] = row_chars[x]
                
                if is_rgb:
                    r, g, b = row_rgb_vals[x]
                    buffer.colors[y][x] = fg_rgb(r, g, b)
                else:
                    buffer.colors[y][x] = row_colors[x]
                
                buffer.z_buffer[y][x] = 1.0


def run_shader_animation(buffer, width, height, time, theme_manager, shader_func, use_braille=False):
    """
    Convenience function to run a shader animation.
    
    Args:
        buffer: Screen buffer to render to
        width, height: Terminal dimensions
        time: Current animation time
        theme_manager: Theme manager for colors
        shader_func: Function(U, V, time) -> intensity array
        use_braille: Enable Braille rendering mode for 4x resolution
    
    Returns:
        Tuple for engine compatibility (rotation_x, rotation_y)
    """
    renderer = ShaderRenderer(width, height, theme_manager, use_braille=use_braille)
    renderer.render(buffer, time, shader_func)
    return (0, 1)
