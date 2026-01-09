"""
Big Text Renderer for ASCII Animations
Provides block-style font rendering for large digits and symbols.
"""

# 5-row x 3-column block font for digits and common symbols
FONT_5x3 = {
    '0': ["███", "█ █", "█ █", "█ █", "███"],
    '1': [" █ ", "██ ", " █ ", " █ ", "███"],
    '2': ["███", "  █", "███", "█  ", "███"],
    '3': ["███", "  █", "███", "  █", "███"],
    '4': ["█ █", "█ █", "███", "  █", "  █"],
    '5': ["███", "█  ", "███", "  █", "███"],
    '6': ["███", "█  ", "███", "█ █", "███"],
    '7': ["███", "  █", "  █", "  █", "  █"],
    '8': ["███", "█ █", "███", "█ █", "███"],
    '9': ["███", "█ █", "███", "  █", "███"],
    ':': ["   ", " █ ", "   ", " █ ", "   "],
    '-': ["   ", "   ", "███", "   ", "   "],
    '/': ["  █", " █ ", " █ ", " █ ", "█  "],
    ' ': ["   ", "   ", "   ", "   ", "   "],
    '.': ["   ", "   ", "   ", "   ", " █ "],
    'A': ["███", "█ █", "███", "█ █", "█ █"],
    'P': ["███", "█ █", "███", "█  ", "█  "],
    'M': ["█ █", "███", "█ █", "█ █", "█ █"],
}

# Huge 5x5 font for better readability
FONT_HUGE = {
    '0': ["█████", "█   █", "█   █", "█   █", "█████"],
    '1': ["  █  ", " ██  ", "  █  ", "  █  ", "█████"],
    '2': ["█████", "    █", "█████", "█    ", "█████"],
    '3': ["█████", "    █", "  ███", "    █", "█████"],
    '4': ["█   █", "█   █", "█████", "    █", "    █"],
    '5': ["█████", "█    ", "█████", "    █", "█████"],
    '6': ["█████", "█    ", "█████", "█   █", "█████"],
    '7': ["█████", "    █", "   █ ", "  █  ", "  █  "],
    '8': ["█████", "█   █", "█████", "█   █", "█████"],
    '9': ["█████", "█   █", "█████", "    █", "█████"],
    ':': ["     ", "  █  ", "     ", "  █  ", "     "],
    '-': ["     ", "     ", "█████", "     ", "     "],
    ' ': ["     ", "     ", "     ", "     ", "     "],
}

# Alternate thin font (3 rows x 3 cols) for smaller displays
FONT_3x3 = {
    '0': ["█▀█", "█ █", "▀▀▀"],
    '1': [" █ ", " █ ", " ▀ "],
    '2': ["▀▀█", "█▀▀", "▀▀▀"],
    '3': ["▀▀█", " ▀█", "▀▀▀"],
    '4': ["█ █", "▀▀█", "  ▀"],
    '5': ["█▀▀", "▀▀█", "▀▀▀"],
    '6': ["█▀▀", "█▀█", "▀▀▀"],
    '7': ["▀▀█", "  █", "  ▀"],
    '8': ["█▀█", "█▀█", "▀▀▀"],
    '9': ["█▀█", "▀▀█", "▀▀▀"],
    ':': [" ● ", "   ", " ● "],
    ' ': ["   ", "   ", "   "],
}


def get_text_width(text, font=None):
    """
    Calculate the total width of a string in block characters.
    
    Args:
        text: String to measure
        font: Font dictionary to use (default: FONT_5x3)
    
    Returns:
        Width in terminal columns
    """
    if font is None:
        font = FONT_5x3
    
    width = 0
    for char in str(text):
        if char in font:
            # Width of character + 1 space
            width += len(font[char][0]) + 1
        else:
            width += 2  # Unknown char = small space
    
    return max(0, width - 1)  # Remove trailing space


def get_text_height(font=None):
    """Get height of font in rows."""
    if font is None:
        font = FONT_5x3
    # All chars should be same height, get from '0'
    return len(font.get('0', [''] * 5))


def draw_big_text(buffer, x, y, text, color=None, z=-10, font=None, char='█'):
    """
    Draw a string of big block text into the screen buffer.
    
    Args:
        buffer: ScreenBuffer instance to draw into
        x: Starting X position (left edge)
        y: Starting Y position (top edge)
        text: String to render (digits, :, -, /, space supported)
        color: ANSI color code (optional)
        z: Z-depth for layering (default: -10, meaning foreground)
        font: Font dictionary to use (default: FONT_5x3)
        char: Character to use for filled pixels (default: █)
    
    Returns:
        (end_x, height) tuple for positioning
    """
    if font is None:
        font = FONT_5x3
    
    cursor_x = int(x)
    y = int(y)
    
    for character in str(text):
        if character in font:
            grid = font[character]
            char_width = len(grid[0]) if grid else 0
            
            for row_idx, row_str in enumerate(grid):
                for col_idx, pixel in enumerate(row_str):
                    if pixel != ' ':
                        # Use the pixel character from font, or override
                        display_char = char if pixel in ('█', '#', '*') else pixel
                        buffer.set_pixel(
                            cursor_x + col_idx, 
                            y + row_idx, 
                            display_char, 
                            z=z, 
                            color=color
                        )
            
            cursor_x += char_width + 1  # Width + spacing
        else:
            # Unknown character - skip with small space
            cursor_x += 2
    
    height = len(font.get('0', [''] * 5))
    return (cursor_x, height)


def draw_big_text_centered(buffer, width, height, text, y_offset=0, color=None, z=-10, font=None):
    """
    Draw big text centered horizontally on screen.
    
    Args:
        buffer: ScreenBuffer instance
        width: Terminal width
        height: Terminal height (unused, for API consistency)
        text: String to render
        y_offset: Vertical offset from center (negative = up)
        color: ANSI color code
        z: Z-depth
        font: Font dictionary
    
    Returns:
        (start_x, start_y, text_width, text_height)
    """
    if font is None:
        font = FONT_5x3
    
    text_width = get_text_width(text, font)
    text_height = get_text_height(font)
    
    start_x = (width - text_width) // 2
    start_y = (height - text_height) // 2 + y_offset
    
    draw_big_text(buffer, start_x, start_y, text, color, z, font)
    
    return (start_x, start_y, text_width, text_height)


def get_text_mask(text, font=None):
    """
    Generate a 2D boolean mask for text (used for Matrix Clock effect).
    
    Args:
        text: String to convert to mask
        font: Font dictionary
    
    Returns:
        List of lists (rows x cols) where True = filled pixel
    """
    if font is None:
        font = FONT_5x3
    
    text_width = get_text_width(text, font)
    text_height = get_text_height(font)
    
    # Initialize empty mask
    mask = [[False] * text_width for _ in range(text_height)]
    
    cursor_x = 0
    for character in str(text):
        if character in font:
            grid = font[character]
            char_width = len(grid[0]) if grid else 0
            
            for row_idx, row_str in enumerate(grid):
                for col_idx, pixel in enumerate(row_str):
                    if pixel != ' ' and cursor_x + col_idx < text_width:
                        mask[row_idx][cursor_x + col_idx] = True
            
            cursor_x += char_width + 1
        else:
            cursor_x += 2
    
    return mask
