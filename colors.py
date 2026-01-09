"""
ANSI Color System and Theme Management
Provides color codes, themes, and depth-based shading for ASCII animations.
Enhanced with more gradient steps for better 3D topology visualization.
"""

# ANSI Escape Codes
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

# Foreground Colors (Standard)
BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# Foreground Colors (Bright)
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

# Background Colors
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

# 256 Color Support
def fg_256(n):
    """Foreground color from 256-color palette"""
    return f"\033[38;5;{n}m"

def bg_256(n):
    """Background color from 256-color palette"""
    return f"\033[48;5;{n}m"

# RGB Color Support (True Color)
def fg_rgb(r, g, b):
    """Foreground color from RGB values"""
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb(r, g, b):
    """Background color from RGB values"""
    return f"\033[48;2;{r};{g};{b}m"

# Luminance characters for depth shading (sparse to dense)
LUMINANCE_CHARS = " .,-~:;=!*#$@"
LUMINANCE_CHARS_SIMPLE = " .:+*#@"
LUMINANCE_CHARS_DETAILED = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

# Pre-defined Color Themes
# Each theme has 10 gradient stops for smooth depth-based coloring
THEMES = {
    "matrix": {
        "name": "Matrix",
        "description": "Classic hacker green terminal",
        "gradient": [
            fg_rgb(0, 30, 0),       # Far (very dark green)
            fg_rgb(0, 50, 0),
            fg_rgb(0, 75, 0),
            fg_rgb(0, 100, 0),
            fg_rgb(0, 130, 0),
            fg_rgb(0, 160, 0),
            fg_rgb(0, 190, 0),
            fg_rgb(0, 220, 0),
            fg_rgb(50, 240, 50),
            fg_rgb(100, 255, 100),  # Near (bright green)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_WHITE,
    },
    "fire": {
        "name": "Fire",
        "description": "Warm flames from red to yellow",
        "gradient": [
            fg_rgb(40, 0, 0),       # Far (dark red)
            fg_rgb(80, 10, 0),
            fg_rgb(120, 25, 0),
            fg_rgb(160, 45, 0),
            fg_rgb(200, 70, 0),
            fg_rgb(230, 100, 0),
            fg_rgb(255, 130, 0),
            fg_rgb(255, 170, 20),
            fg_rgb(255, 210, 60),
            fg_rgb(255, 255, 100),  # Near (bright yellow)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_WHITE,
    },
    "ocean": {
        "name": "Ocean",
        "description": "Cool blue depths",
        "gradient": [
            fg_rgb(0, 10, 40),      # Far (deep blue)
            fg_rgb(0, 25, 70),
            fg_rgb(0, 45, 100),
            fg_rgb(0, 70, 130),
            fg_rgb(0, 100, 160),
            fg_rgb(0, 130, 190),
            fg_rgb(30, 160, 210),
            fg_rgb(70, 190, 230),
            fg_rgb(120, 220, 245),
            fg_rgb(180, 255, 255),  # Near (bright cyan)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_WHITE,
    },
    "neon": {
        "name": "Neon",
        "description": "Cyberpunk magenta and purple",
        "gradient": [
            fg_rgb(20, 0, 40),      # Far (dark purple)
            fg_rgb(40, 0, 70),
            fg_rgb(70, 0, 100),
            fg_rgb(100, 0, 140),
            fg_rgb(140, 20, 170),
            fg_rgb(170, 50, 200),
            fg_rgb(200, 80, 220),
            fg_rgb(220, 120, 240),
            fg_rgb(240, 160, 250),
            fg_rgb(255, 200, 255),  # Near (bright pink)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_CYAN,
    },
    "void": {
        "name": "Void",
        "description": "Minimalist grayscale",
        "gradient": [
            fg_rgb(20, 20, 20),     # Far (near black)
            fg_rgb(45, 45, 45),
            fg_rgb(70, 70, 70),
            fg_rgb(95, 95, 95),
            fg_rgb(120, 120, 120),
            fg_rgb(150, 150, 150),
            fg_rgb(180, 180, 180),
            fg_rgb(210, 210, 210),
            fg_rgb(235, 235, 235),
            fg_rgb(255, 255, 255),  # Near (white)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_WHITE,
    },
    "sunset": {
        "name": "Sunset",
        "description": "Warm orange to purple gradient",
        "gradient": [
            fg_rgb(30, 0, 50),      # Far (deep purple)
            fg_rgb(60, 0, 70),
            fg_rgb(100, 15, 70),
            fg_rgb(140, 35, 60),
            fg_rgb(180, 60, 45),
            fg_rgb(210, 90, 30),
            fg_rgb(235, 130, 20),
            fg_rgb(250, 170, 40),
            fg_rgb(255, 200, 80),
            fg_rgb(255, 230, 140),  # Near (golden)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_YELLOW,
    },
    "arctic": {
        "name": "Arctic",
        "description": "Icy blue and white",
        "gradient": [
            fg_rgb(10, 20, 50),     # Far (dark ice)
            fg_rgb(25, 45, 80),
            fg_rgb(45, 75, 120),
            fg_rgb(70, 110, 160),
            fg_rgb(100, 145, 195),
            fg_rgb(130, 175, 220),
            fg_rgb(165, 200, 235),
            fg_rgb(195, 220, 245),
            fg_rgb(220, 240, 252),
            fg_rgb(245, 252, 255),  # Near (white ice)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_CYAN,
    },
    "forest": {
        "name": "Forest",
        "description": "Natural green and brown",
        "gradient": [
            fg_rgb(20, 10, 5),      # Far (dark earth)
            fg_rgb(35, 25, 10),
            fg_rgb(50, 45, 15),
            fg_rgb(60, 70, 25),
            fg_rgb(75, 100, 40),
            fg_rgb(90, 130, 55),
            fg_rgb(110, 160, 70),
            fg_rgb(130, 190, 90),
            fg_rgb(160, 215, 115),
            fg_rgb(200, 240, 150),  # Near (bright leaf)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_GREEN,
    },
    "blood": {
        "name": "Blood",
        "description": "Deep crimson intensity",
        "gradient": [
            fg_rgb(15, 0, 0),       # Far (near black)
            fg_rgb(35, 0, 0),
            fg_rgb(60, 5, 5),
            fg_rgb(90, 10, 10),
            fg_rgb(120, 15, 15),
            fg_rgb(155, 25, 25),
            fg_rgb(190, 35, 35),
            fg_rgb(220, 50, 50),
            fg_rgb(245, 70, 70),
            fg_rgb(255, 100, 100),  # Near (bright red)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_RED,
    },
    "gold": {
        "name": "Gold",
        "description": "Luxurious golden tones",
        "gradient": [
            fg_rgb(40, 25, 0),      # Far (dark bronze)
            fg_rgb(70, 45, 0),
            fg_rgb(100, 65, 5),
            fg_rgb(130, 90, 10),
            fg_rgb(160, 115, 20),
            fg_rgb(190, 145, 35),
            fg_rgb(215, 175, 55),
            fg_rgb(235, 200, 80),
            fg_rgb(250, 225, 110),
            fg_rgb(255, 245, 150),  # Near (bright gold)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_YELLOW,
    },
    "isovalues": {
        "name": "Isovalues",
        "description": "Smooth cosine rainbow spectrum",
        "gradient": [
             fg_rgb(255, 0, 0),    # Red
             fg_rgb(255, 150, 0),  # Orange
             fg_rgb(255, 255, 0),  # Yellow
             fg_rgb(0, 255, 0),    # Green
             fg_rgb(0, 255, 150),  # Spring
             fg_rgb(0, 255, 255),  # Cyan
             fg_rgb(0, 150, 255),  # Azure
             fg_rgb(0, 0, 255),    # Blue
             fg_rgb(150, 0, 255),  # Violet
             fg_rgb(255, 0, 255),  # Magenta
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_CYAN,
    },
    # NEW THEMES
    "rainbow": {
        "name": "Rainbow",
        "description": "Full spectrum depth mapping",
        "gradient": [
            fg_rgb(148, 0, 211),    # Far (violet)
            fg_rgb(75, 0, 130),     # indigo
            fg_rgb(0, 0, 255),      # blue
            fg_rgb(0, 127, 255),    # azure
            fg_rgb(0, 255, 0),      # green
            fg_rgb(127, 255, 0),    # chartreuse
            fg_rgb(255, 255, 0),    # yellow
            fg_rgb(255, 165, 0),    # orange
            fg_rgb(255, 69, 0),     # red-orange
            fg_rgb(255, 0, 0),      # Near (red)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_WHITE,
    },
    "plasma": {
        "name": "Plasma",
        "description": "Electric blue to hot pink",
        "gradient": [
            fg_rgb(0, 0, 50),       # Far (dark blue)
            fg_rgb(20, 0, 100),
            fg_rgb(60, 0, 150),
            fg_rgb(100, 0, 180),
            fg_rgb(150, 30, 200),
            fg_rgb(180, 70, 210),
            fg_rgb(210, 100, 220),
            fg_rgb(240, 130, 225),
            fg_rgb(255, 170, 230),
            fg_rgb(255, 220, 255),  # Near (hot pink)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_MAGENTA,
    },
    "toxic": {
        "name": "Toxic",
        "description": "Radioactive green glow",
        "gradient": [
            fg_rgb(0, 20, 0),       # Far (dark)
            fg_rgb(20, 50, 0),
            fg_rgb(50, 90, 0),
            fg_rgb(80, 130, 0),
            fg_rgb(120, 170, 0),
            fg_rgb(160, 200, 20),
            fg_rgb(200, 230, 50),
            fg_rgb(220, 250, 80),
            fg_rgb(240, 255, 120),
            fg_rgb(255, 255, 180),  # Near (toxic glow)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_GREEN,
    },
    "copper": {
        "name": "Copper",
        "description": "Warm metallic copper tones",
        "gradient": [
            fg_rgb(30, 15, 10),     # Far (dark copper)
            fg_rgb(60, 30, 20),
            fg_rgb(90, 50, 30),
            fg_rgb(125, 70, 40),
            fg_rgb(160, 95, 55),
            fg_rgb(185, 120, 75),
            fg_rgb(210, 150, 100),
            fg_rgb(230, 180, 130),
            fg_rgb(245, 210, 165),
            fg_rgb(255, 235, 200),  # Near (bright copper)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_YELLOW,
    },
    "lavender": {
        "name": "Lavender",
        "description": "Soft purple pastels",
        "gradient": [
            fg_rgb(40, 20, 60),     # Far (deep purple)
            fg_rgb(65, 40, 90),
            fg_rgb(90, 60, 120),
            fg_rgb(115, 85, 150),
            fg_rgb(145, 110, 175),
            fg_rgb(170, 140, 200),
            fg_rgb(195, 170, 220),
            fg_rgb(215, 195, 235),
            fg_rgb(235, 220, 248),
            fg_rgb(250, 245, 255),  # Near (pale lavender)
        ],
        "background": BG_BLACK,
        "accent": BRIGHT_MAGENTA,
    },
}

# Theme list for cycling
THEME_LIST = list(THEMES.keys())


class ThemeManager:
    """Manages color themes and provides depth-based coloring."""
    
    def __init__(self, theme_name="matrix"):
        self.set_theme(theme_name)
    
    def set_theme(self, theme_name):
        """Set the active theme by name."""
        theme_name = theme_name.lower()
        if theme_name not in THEMES:
            theme_name = "matrix"
        self.current_theme = theme_name
        self.theme = THEMES[theme_name]
        self.gradient = self.theme["gradient"]
    
    def next_theme(self):
        """Cycle to the next theme."""
        current_idx = THEME_LIST.index(self.current_theme)
        next_idx = (current_idx + 1) % len(THEME_LIST)
        self.set_theme(THEME_LIST[next_idx])
        return self.theme["name"]
    
    def prev_theme(self):
        """Cycle to the previous theme."""
        current_idx = THEME_LIST.index(self.current_theme)
        prev_idx = (current_idx - 1) % len(THEME_LIST)
        self.set_theme(THEME_LIST[prev_idx])
        return self.theme["name"]
    
    def get_color_for_depth(self, z, z_min, z_max):
        """
        Get the appropriate color code based on depth (z value).
        Objects closer to camera (lower z) are brighter.
        Uses smooth interpolation across 10 gradient stops.
        """
        if z_max == z_min:
            normalized = 0.5
        else:
            # Invert: lower z = closer = brighter (higher index)
            normalized = 1.0 - (z - z_min) / (z_max - z_min)
        
        # Clamp to valid range
        normalized = max(0.0, min(1.0, normalized))
        
        # Map to gradient index with fine granularity
        index = int(normalized * (len(self.gradient) - 1))
        return self.gradient[index]
    
    def get_char_for_depth(self, z, z_min, z_max, char_set=None):
        """
        Get both the character and color for a given depth.
        Returns (char, color_code).
        """
        if char_set is None:
            char_set = LUMINANCE_CHARS
        
        if z_max == z_min:
            normalized = 0.5
        else:
            normalized = 1.0 - (z - z_min) / (z_max - z_min)
        
        normalized = max(0.0, min(1.0, normalized))
        
        char_index = int(normalized * (len(char_set) - 1))
        color = self.get_color_for_depth(z, z_min, z_max)
        
        return char_set[char_index], color
    
    def colorize(self, text, depth_normalized=1.0):
        """Apply theme color to text based on normalized depth (0=far, 1=near)."""
        depth_normalized = max(0.0, min(1.0, depth_normalized))
        index = int(depth_normalized * (len(self.gradient) - 1))
        return f"{self.gradient[index]}{text}{RESET}"
    
    def get_accent(self):
        """Get the accent color for UI elements."""
        return self.theme["accent"]
    
    def get_background(self):
        """Get the background color."""
        return self.theme["background"]


def clear_screen():
    """Clear the terminal screen."""
    print("\033[2J\033[H", end="")


def hide_cursor():
    """Hide the terminal cursor."""
    print("\033[?25l", end="")


def show_cursor():
    """Show the terminal cursor."""
    print("\033[?25h", end="")


def move_cursor(row, col):
    """Move cursor to specified position (1-indexed)."""
    print(f"\033[{row};{col}H", end="")


def set_title(title):
    """Set terminal window title."""
    print(f"\033]0;{title}\007", end="")
