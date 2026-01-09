"""
Core Rendering Engine
Handles 3D projection, screen buffering, timing, and the main render loop.
Enhanced with bloom/glow effects, thick lines, and safe scaling.
"""

import os
import sys
import time
import math
from colors import ThemeManager, RESET, clear_screen, hide_cursor, show_cursor, move_cursor, set_title, LUMINANCE_CHARS, fg_rgb

# Try to import msvcrt for Windows keyboard input
try:
    import msvcrt
    WINDOWS = True
except ImportError:
    WINDOWS = False
    import select
    import tty
    import termios


# Unicode block characters for sub-pixel rendering
BLOCK_CHARS = {
    'full': '█',
    'top': '▀',
    'bottom': '▄',
    'left': '▌',
    'right': '▐',
    'light': '░',
    'medium': '▒',
    'dark': '▓',
}


class ScreenBuffer:
    """
    A 2D buffer for building the frame before printing.
    Stores both characters and their z-depths for proper depth sorting.
    Enhanced with bloom/glow support and thick lines.
    """
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.chars = [[' ' for _ in range(width)] for _ in range(height)]
        self.z_buffer = [[float('inf') for _ in range(width)] for _ in range(height)]
        self.colors = [[None for _ in range(width)] for _ in range(height)]
        self.intensity = [[0.0 for _ in range(width)] for _ in range(height)]  # For bloom
    
    def clear(self):
        """Clear the buffer for a new frame."""
        for y in range(self.height):
            for x in range(self.width):
                self.chars[y][x] = ' '
                self.z_buffer[y][x] = float('inf')
                self.colors[y][x] = None
                self.intensity[y][x] = 0.0
    
    def set_pixel(self, x, y, char, z=0, color=None, intensity=1.0):
        """
        Set a pixel in the buffer with z-depth testing.
        Only draws if the new z is closer than existing.
        """
        x, y = int(x), int(y)
        # Bounds check
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        
        # Z-buffer test (lower z = closer to camera)
        if z < self.z_buffer[y][x]:
            self.chars[y][x] = char
            self.z_buffer[y][x] = z
            self.colors[y][x] = color
            self.intensity[y][x] = intensity
            return True
        return False
    
    def set_pixel_with_glow(self, x, y, char, z=0, color=None, glow_radius=1, theme_manager=None):
        """
        Set a pixel with a glow effect around it.
        Creates a halo of dimmer characters in adjacent cells.
        """
        x, y = int(x), int(y)
        # Draw main pixel
        self.set_pixel(x, y, char, z, color, intensity=1.0)
        
        if glow_radius <= 0 or theme_manager is None:
            return
        
        # Glow characters from bright to dim
        glow_chars = ".:·"
        
        # Draw glow halo
        for dy in range(-glow_radius, glow_radius + 1):
            for dx in range(-glow_radius, glow_radius + 1):
                if dx == 0 and dy == 0:
                    continue
                
                gx, gy = x + dx, y + dy
                if gx < 0 or gx >= self.width or gy < 0 or gy >= self.height:
                    continue
                
                # Calculate intensity falloff: I = 1 / (distance^2)
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > glow_radius:
                    continue
                    
                glow_intensity = 1.0 / (dist * dist + 1)
                
                # Only draw glow if cell is empty or has lower intensity
                if self.chars[gy][gx] == ' ' or self.intensity[gy][gx] < glow_intensity:
                    char_idx = min(len(glow_chars) - 1, int((1 - glow_intensity) * len(glow_chars)))
                    glow_char = glow_chars[char_idx]
                    # Use a dimmer version of the color
                    self.chars[gy][gx] = glow_char
                    self.z_buffer[gy][gx] = z + 0.1  # Slightly behind main pixel
                    self.colors[gy][gx] = color
                    self.intensity[gy][gx] = glow_intensity
    
    def draw_line(self, x1, y1, x2, y2, char='*', z=0, color=None):
        """Draw a line using Bresenham's algorithm."""
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        while True:
            self.set_pixel(x1, y1, char, z, color)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy

    def draw_thick_line(self, x1, y1, x2, y2, char='*', z=0, color=None, thickness=1):
        """
        Draw a thicker line by drawing parallel lines.
        Thickness 1 = standard line.
        Thickness 2+ = adds adjacent pixels.
        """
        self.draw_line(x1, y1, x2, y2, char, z, color)
        
        if thickness > 1:
            # Simple approach: Draw adjacent lines
            # For more robustness, we could compute normal, but this is fast
            self.draw_line(x1 + 1, y1, x2 + 1, y2, char, z + 0.01, color)
            
            if thickness > 2:
                self.draw_line(x1, y1 + 1, x2, y2 + 1, char, z + 0.01, color)
                self.draw_line(x1 + 1, y1 + 1, x2 + 1, y2 + 1, char, z + 0.01, color)

    def draw_line_subpixel(self, x1, y1, x2, y2, z=0, color=None):
        """
        Draw a line with sub-pixel anti-aliasing using Unicode block characters.
        Effectively doubles vertical resolution.
        """
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        length = max(abs(x2 - x1), abs(y2 - y1))
        if length < 1:
            length = 1
        
        steps = int(length * 2)  # Higher resolution
        for i in range(steps + 1):
            t = i / max(steps, 1)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            
            ix = int(x)
            iy = int(y)
            
            # Sub-pixel: use block chars based on fractional part
            frac_y = y - int(y)
            if frac_y > 0.5:
                char = BLOCK_CHARS['bottom']
            else:
                char = BLOCK_CHARS['top']
            
            self.set_pixel(ix, iy, char, z, color)
    
    def render(self, theme_manager=None):
        """Convert buffer to a single string for printing."""
        lines = []
        for y in range(self.height):
            line_parts = []
            current_color = None
            for x in range(self.width):
                char = self.chars[y][x]
                color = self.colors[y][x]
                
                if color != current_color:
                    if color:
                        line_parts.append(color)
                    elif current_color:
                        line_parts.append(RESET)
                    current_color = color
                
                line_parts.append(char)
            
            if current_color:
                line_parts.append(RESET)
            lines.append(''.join(line_parts))
        
        return '\n'.join(lines)


def get_terminal_size():
    """Get terminal dimensions, with fallback."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines - 1  # Leave room for status line
    except OSError:
        return 80, 24


def rotate_x(point, angle):
    """Rotate a 3D point around the X axis."""
    x, y, z = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (x, y * cos_a - z * sin_a, y * sin_a + z * cos_a)


def rotate_y(point, angle):
    """Rotate a 3D point around the Y axis."""
    x, y, z = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a)


def rotate_z(point, angle):
    """Rotate a 3D point around the Z axis."""
    x, y, z = point
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (x * cos_a - y * sin_a, x * sin_a + y * cos_a, z)


def project_point(x, y, z, width, height, scale=None, distance=5):
    """
    Project a 3D point to 2D screen coordinates.
    Uses perspective projection with proper aspect ratio correction.
    
    Returns (screen_x, screen_y) or None if behind camera.
    """
    # Improved scaling: use normalized coordinates approach
    if scale is None:
        # Reduced default scale factor to 0.3 to prevent clipping
        scale = min(width, height * 2) * 0.3
    
    # Prevent division by zero or negative (behind camera)
    if z + distance <= 0.1:
        return None
    
    factor = scale / (z + distance)
    
    # Aspect ratio correction: characters are ~2x taller than wide
    screen_x = int(x * factor * 2 + width / 2)
    screen_y = int(y * factor + height / 2)
    
    return screen_x, screen_y


def project_point_normalized(x, y, z, width, height, distance=5):
    """
    Project using normalized coordinates [-1, 1].
    Better for consistent sizing across different terminal sizes.
    """
    if z + distance <= 0.1:
        return None
    
    factor = 1.0 / (z + distance)
    
    # Scale factor based on terminal size (REDUCED)
    scale_factor = min(width, height * 2) * 0.3
    
    # Project with aspect ratio correction
    screen_x = int(x * factor * scale_factor * 2 + width / 2)
    screen_y = int(y * factor * scale_factor + height / 2)
    
    return screen_x, screen_y


def check_key():
    """
    Check if a key has been pressed (non-blocking).
    Returns the key character or None.
    """
    if WINDOWS:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            # Handle special keys
            if key == b'\xe0':  # Arrow keys prefix
                key = msvcrt.getch()
                return f"special_{key.decode('latin-1', errors='ignore')}"
            try:
                return key.decode('utf-8')
            except:
                return key.decode('latin-1', errors='ignore')
    else:
        # Unix/Linux
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
    return None


class AnimationEngine:
    """
    Main animation engine that manages the render loop,
    timing, and user input.
    """
    
    def __init__(self):
        self.theme_manager = ThemeManager("matrix")
        self.speed = 0.5  # Slower default to reduce flashing
        self.target_fps = 20  # Lower FPS for smoother rendering
        self.paused = False
        self.running = False
        self.time = 0
        self.frame_count = 0
        self.show_stats = True
        
        # Speed presets
        self.speed_presets = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
        self.speed_index = 1  # Default to 0.5x
    
    def set_speed(self, speed):
        """Set animation speed multiplier."""
        self.speed = max(0.1, min(10.0, speed))
    
    def increase_speed(self):
        """Increase speed to next preset."""
        if self.speed_index < len(self.speed_presets) - 1:
            self.speed_index += 1
            self.speed = self.speed_presets[self.speed_index]
        return self.speed
    
    def decrease_speed(self):
        """Decrease speed to previous preset."""
        if self.speed_index > 0:
            self.speed_index -= 1
            self.speed = self.speed_presets[self.speed_index]
        return self.speed
    
    def set_fps(self, fps):
        """Set target frames per second."""
        self.target_fps = max(10, min(120, fps))
    
    def toggle_pause(self):
        """Toggle pause state."""
        self.paused = not self.paused
        return self.paused
    
    def toggle_stats(self):
        """Toggle stats display."""
        self.show_stats = not self.show_stats
        return self.show_stats
    
    def run_animation(self, render_func, animation_name="Animation"):
        """
        Main animation loop.
        
        render_func should be a function that takes:
            (buffer, width, height, time, theme_manager) -> (z_min, z_max)
        """
        self.running = True
        self.time = 0
        self.frame_count = 0
        frame_time = 1.0 / self.target_fps
        
        hide_cursor()
        set_title(f"Terminal Animation - {animation_name}")
        clear_screen()  # Initial clear to remove menu
        
        try:
            while self.running:
                frame_start = time.perf_counter()
                
                # Handle input
                key = check_key()
                if key:
                    self._handle_key(key)
                
                if not self.paused:
                    # Get terminal size
                    width, height = get_terminal_size()
                    
                    # Create buffer
                    buffer = ScreenBuffer(width, height)
                    
                    # Render the animation
                    try:
                        z_range = render_func(buffer, width, height, self.time, self.theme_manager)
                    except Exception as e:
                        # If render fails, show error
                        clear_screen()
                        print(f"Render error: {e}")
                        time.sleep(1)
                        continue
                    
                    # Draw stats bar at bottom
                    if self.show_stats and height > 2:
                        stats = self._get_stats_line(animation_name, width)
                        for i, char in enumerate(stats[:width]):
                            buffer.set_pixel(i, height - 1, char, z=-1000, 
                                           color=self.theme_manager.get_accent())
                    
                    # Output frame - use cursor home to prevent scrolling
                    move_cursor(1, 1)  # Move to top-left instead of clear
                    sys.stdout.write(buffer.render())
                    sys.stdout.flush()
                    
                    # Update time
                    self.time += (1.0 / self.target_fps) * self.speed
                    self.frame_count += 1
                
                # Frame rate limiting
                elapsed = time.perf_counter() - frame_start
                sleep_time = frame_time - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        finally:
            show_cursor()
            clear_screen()
    
    def _handle_key(self, key):
        """Process keyboard input."""
        key_lower = key.lower() if isinstance(key, str) else key
        
        if key_lower in ('q', '\x1b'):  # Q or ESC
            self.running = False
        elif key_lower == ' ':  # Space
            self.toggle_pause()
        elif key_lower == '+' or key_lower == '=':
            self.increase_speed()
        elif key_lower == '-' or key_lower == '_':
            self.decrease_speed()
        elif key_lower == 't':
            self.theme_manager.next_theme()
        elif key_lower == 'r':
            self.theme_manager.prev_theme()
        elif key_lower == 's':
            self.toggle_stats()
    
    def _get_stats_line(self, name, width):
        """Generate the stats line for display."""
        theme_name = self.theme_manager.theme["name"]
        paused_str = " [PAUSED]" if self.paused else ""
        stats = f" {name} | Theme: {theme_name} | Speed: {self.speed:.2f}x | [Q]uit [SPACE]Pause [T]heme [+/-]Speed{paused_str} "
        
        # Pad or truncate to width
        if len(stats) < width:
            stats = stats + ' ' * (width - len(stats))
        else:
            stats = stats[:width]
        
        return stats


# Utility math functions for animations
def lerp(a, b, t):
    """Linear interpolation between a and b."""
    return a + (b - a) * t


def smoothstep(t):
    """Smooth interpolation curve."""
    return t * t * (3 - 2 * t)


def clamp(value, min_val, max_val):
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def map_range(value, in_min, in_max, out_min, out_max):
    """Map a value from one range to another."""
    if in_max == in_min:
        return out_min
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def distance_3d(p1, p2):
    """Calculate 3D distance between two points."""
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)


def normalize_3d(v):
    """Normalize a 3D vector."""
    length = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if length == 0:
        return (0, 0, 0)
    return (v[0]/length, v[1]/length, v[2]/length)


def dot_product(v1, v2):
    """Calculate dot product of two 3D vectors."""
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]


# SDF (Signed Distance Field) functions for raymarching
def sdf_sphere(point, center, radius):
    """Signed distance to a sphere."""
    return distance_3d(point, center) - radius


def sdf_box(point, center, size):
    """Signed distance to a box."""
    dx = abs(point[0] - center[0]) - size[0]
    dy = abs(point[1] - center[1]) - size[1]
    dz = abs(point[2] - center[2]) - size[2]
    return max(dx, dy, dz)


def sdf_union(d1, d2):
    """Union of two SDFs."""
    return min(d1, d2)


def sdf_intersection(d1, d2):
    """Intersection of two SDFs."""
    return max(d1, d2)


def sdf_difference(d1, d2):
    """Difference of two SDFs (d1 - d2)."""
    return max(d1, -d2)
