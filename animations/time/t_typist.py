"""
T-06: Typist Terminal
Animated typing effect displaying the current time.
"""

import math
from datetime import datetime


class TypistState:
    """Persistent state for typist animation."""
    def __init__(self):
        self.current_text = ""
        self.target_text = ""
        self.cursor_pos = 0
        self.mode = "typing"  # typing, waiting, backspacing
        self.last_update = 0
        self.wait_until = 0
        self.blink_state = True
        self.lines = []
        self.max_lines = 8


_state = TypistState()


def render(buffer, width, height, t, theme_manager):
    """
    Render a retro terminal with typing animation.
    """
    global _state
    
    # Get current time
    now = datetime.now()
    new_target = now.strftime("[SYSTEM] Time: %H:%M:%S")
    
    # Update target if time changed
    if new_target != _state.target_text and _state.mode == "waiting":
        # Need to update - start backspacing the seconds
        _state.mode = "backspacing"
        _state.cursor_pos = len(_state.current_text)
    
    _state.target_text = new_target
    
    # Typing speed (characters per second)
    type_speed = 15
    frame_interval = 1.0 / type_speed
    
    # Update animation state
    if t - _state.last_update > frame_interval:
        _state.last_update = t
        _state.blink_state = not _state.blink_state
        
        if _state.mode == "typing":
            if _state.cursor_pos < len(_state.target_text):
                _state.current_text = _state.target_text[:_state.cursor_pos + 1]
                _state.cursor_pos += 1
            else:
                _state.mode = "waiting"
                _state.wait_until = t + 0.5
                
        elif _state.mode == "backspacing":
            # Only backspace the seconds (last 2 characters)
            if len(_state.current_text) > len(_state.target_text) - 2:
                _state.current_text = _state.current_text[:-1]
                _state.cursor_pos = len(_state.current_text)
            else:
                _state.mode = "typing"
                
        elif _state.mode == "waiting":
            if t > _state.wait_until:
                # Check if we need to update
                current_time_str = now.strftime("%H:%M:%S")
                if current_time_str not in _state.current_text:
                    _state.mode = "backspacing"
    
    # Draw terminal frame
    z_min, z_max = -5, 5
    
    frame_left = 2
    frame_top = 2
    frame_width = min(width - 4, 60)
    frame_height = min(height - 4, 15)
    
    # Draw border
    border_color = theme_manager.get_color_for_depth(-3, z_min, z_max)
    
    # Top border
    buffer.set_pixel(frame_left, frame_top, '╔', z=-3, color=border_color)
    for x in range(frame_left + 1, frame_left + frame_width - 1):
        buffer.set_pixel(x, frame_top, '═', z=-3, color=border_color)
    buffer.set_pixel(frame_left + frame_width - 1, frame_top, '╗', z=-3, color=border_color)
    
    # Bottom border
    buffer.set_pixel(frame_left, frame_top + frame_height - 1, '╚', z=-3, color=border_color)
    for x in range(frame_left + 1, frame_left + frame_width - 1):
        buffer.set_pixel(x, frame_top + frame_height - 1, '═', z=-3, color=border_color)
    buffer.set_pixel(frame_left + frame_width - 1, frame_top + frame_height - 1, '╝', z=-3, color=border_color)
    
    # Side borders
    for y in range(frame_top + 1, frame_top + frame_height - 1):
        buffer.set_pixel(frame_left, y, '║', z=-3, color=border_color)
        buffer.set_pixel(frame_left + frame_width - 1, y, '║', z=-3, color=border_color)
    
    # Title
    title = " TERMINAL v1.0 "
    title_x = frame_left + (frame_width - len(title)) // 2
    for i, char in enumerate(title):
        buffer.set_pixel(title_x + i, frame_top, char, z=-4, color=theme_manager.get_accent())
    
    # Content area
    content_x = frame_left + 2
    content_y = frame_top + 2
    content_width = frame_width - 4
    
    # Static header lines
    header_lines = [
        f"$ date",
        f"  {now.strftime('%a %b %d %Y')}",
        "",
        "$ clock --live",
    ]
    
    # Draw header
    text_color = theme_manager.get_color_for_depth(0, z_min, z_max)
    for line_idx, line in enumerate(header_lines):
        y = content_y + line_idx
        if y >= frame_top + frame_height - 2:
            break
        for i, char in enumerate(line[:content_width]):
            buffer.set_pixel(content_x + i, y, char, z=0, color=text_color)
    
    # Draw current typing line
    typing_y = content_y + len(header_lines)
    typing_prefix = "  "
    full_line = typing_prefix + _state.current_text
    
    accent_color = theme_manager.get_accent()
    
    for i, char in enumerate(full_line[:content_width]):
        buffer.set_pixel(content_x + i, typing_y, char, z=-1, color=accent_color)
    
    # Blinking cursor
    cursor_x = content_x + len(full_line)
    if cursor_x < content_x + content_width and _state.blink_state:
        buffer.set_pixel(cursor_x, typing_y, '█', z=-2, color=accent_color)
    
    # Decorative scan line effect
    scan_y = int((t * 10) % height)
    if scan_y < height:
        scan_color = theme_manager.get_color_for_depth(-4, z_min, z_max)
        for x in range(frame_left, frame_left + frame_width):
            if frame_top < scan_y < frame_top + frame_height - 1:
                buffer.set_pixel(x, scan_y, '░', z=5, color=scan_color)
    
    return (z_min, z_max)
