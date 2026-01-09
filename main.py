"""
Terminal 3D Animation Engine - Main Entry Point
"""

import sys
import os
import random
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine import AnimationEngine, check_key, clear_screen, set_title, show_cursor, move_cursor
from colors import RESET, CYAN, YELLOW, GREEN, MAGENTA, RED, WHITE, BLUE
from animations import ANIMATIONS, ANIMATION_LIST, SCREENSAVERS_REGULAR, SCREENSAVERS_ULTRAWIDE, TIME_APPS


def print_header():
    """Print the animated ASCII header."""
    header = [
        f"{CYAN}╔════════════════════════════════════════════════════════╗{RESET}",
        f"{CYAN}║     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗  ║{RESET}",
        f"{CYAN}║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║  ║{RESET}",
        f"{CYAN}║        ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║  ║{RESET}",
        f"{CYAN}║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║  ║{RESET}",
        f"{CYAN}║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║  ║{RESET}",
        f"{CYAN}║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝  ║{RESET}",
        f"{CYAN}║            █████╗ ███╗   ██╗██╗███╗   ███╗             ║{RESET}",
        f"{CYAN}║           ██╔══██╗████╗  ██║██║████╗ ████║             ║{RESET}",
        f"{CYAN}║           ███████║██╔██╗ ██║██║██╔████╔██║             ║{RESET}",
        f"{CYAN}║           ██╔══██║██║╚██╗██║██║██║╚██╔╝██║             ║{RESET}",
        f"{CYAN}║           ██║  ██║██║ ╚████║██║██║ ╚═╝ ██║             ║{RESET}",
        f"{CYAN}║           ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝╚═╝     ╚═╝             ║{RESET}",
        f"{CYAN}╚════════════════════════════════════════════════════════╝{RESET}",
    ]
    
    for line in header:
        print(line)


def print_category_menu():
    """Print the top-level category menu."""
    clear_screen()
    print_header()
    print()
    print(f"    {YELLOW}═══════════════════ MAIN MENU ════════════════════{RESET}")
    print()
    print(f"    {WHITE}[1]{RESET} Standard 3D Animations")
    print(f"        {CYAN}classic wireframes and math 3d{RESET}")
    print()
    print(f"    {WHITE}[2]{RESET} Screensavers (16:9)")
    print(f"        {CYAN}centralized volumetric fractals{RESET}")
    print()
    print(f"    {WHITE}[3]{RESET} Screensavers (Ultrawide)")
    print(f"        {CYAN}horizontal flows and infinite fields{RESET}")
    print()
    print(f"    {WHITE}[4]{RESET} Time & Utility")
    print(f"        {CYAN}clocks, timers, and stopwatches{RESET}")
    print()
    print(f"    {YELLOW}═══════════════════ OPTIONS ══════════════════════{RESET}")
    print()
    print(f"    {WHITE}[S]{RESET} Settings    {WHITE}[R]{RESET} Random    {WHITE}[Q]{RESET} Quit")
    print()


def print_list_menu(title, items_dict, selected_index=-1):
    """Print a list of animations from a dictionary."""
    clear_screen()
    print_header()
    print()
    print(f"    {YELLOW}══════════ {title} ══════════{RESET}")
    print()
    
    keys = list(items_dict.keys())
    
    # Calculate columns based on terminal width approximately
    # We'll use 2 columns for now
    mid_point = (len(keys) + 1) // 2
    
    for i in range(mid_point):
        # Column 1
        key1 = keys[i]
        name1 = items_dict[key1]["name"]
        item1 = f"[{i+1:2d}] {name1:<22}"
        item1 = f"{WHITE}{item1}{RESET}"
            
        # Column 2
        if i + mid_point < len(keys):
            key2 = keys[i + mid_point]
            name2 = items_dict[key2]["name"]
            item2 = f"[{i + mid_point + 1:2d}] {name2:<22}"
            item2 = f"{WHITE}{item2}{RESET}"
        else:
            item2 = ""
            
        print(f"    {item1}    {item2}")

    print()
    print(f"    {YELLOW}════════════════════════════════════════════════════════{RESET}")
    print()
    print(f"    {WHITE}Enter number to select, or [B] Back{RESET}")


def settings_menu(engine):
    """Sub-menu for settings."""
    in_settings = True
    while in_settings:
        clear_screen()
        print_header()
        print()
        print(f"    {YELLOW}═══════════════════ SETTINGS ═════════════════════{RESET}")
        print()
        print(f"    Current Theme: {GREEN}{engine.theme_manager.theme['name']}{RESET}")
        print(f"    Target FPS:    {GREEN}{engine.target_fps}{RESET}")
        print(f"    Speed:         {GREEN}{engine.speed}x{RESET}")
        print()
        print(f"    [T] Change Theme")
        print(f"    [F] Change FPS (20/30/60)")
        print(f"    [S] Change Default Speed")
        print(f"    [B] Back to Main Menu")
        print()
        
        print("    Select option: ", end="", flush=True)
        
        while True:
            key = check_key()
            if key:
                break
            time.sleep(0.05)
            
        key = key.lower()
        if key == 'b' or key == 'q':
            in_settings = False
        elif key == 't':
            engine.theme_manager.next_theme()
        elif key == 'f':
            if engine.target_fps == 20: engine.set_fps(30)
            elif engine.target_fps == 30: engine.set_fps(60)
            else: engine.set_fps(20)
        elif key == 's':
            # Cycle through speed presets
            idx = engine.speed_index
            idx = (idx + 1) % len(engine.speed_presets)
            engine.speed_index = idx
            engine.speed = engine.speed_presets[idx]


def run_animation_from_dict(engine, anim_key, anim_dict):
    """Run a specific animation from a dictionary."""
    if anim_key not in anim_dict:
        return
    
    anim = anim_dict[anim_key]
    
    # Set recommended theme for this animation
    engine.theme_manager.set_theme(anim.get("recommended_theme", "matrix"))
    
    engine.run_animation(anim["render"], anim["name"])


def handle_selection_screen(engine, title, anim_dict):
    """Handles the sub-menu for a specific collection of animations."""
    keys = list(anim_dict.keys())
    
    while True:
        print_list_menu(title, anim_dict)
        
        # User input loop
        input_buffer = ""
        last_input_time = 0
        
        while True:
            key = check_key()
            
            if key:
                key_lower = key.lower()
                
                # Navigation / Commands
                if key_lower == 'b' or key_lower == 'q':
                    return # Go back
                    
                # Digit handling with buffer for 2 digits
                if key.isdigit():
                    current_time = time.time()
                    if current_time - last_input_time > 1.0: # Reset buffer after 1s
                        input_buffer = key
                    else:
                        input_buffer += key
                        
                    last_input_time = current_time
                    
                    # Try to process buffer immediately if it's potentially valid 
                    # OR wait a bit?
                    # Better UX: if length is 2 or if index is valid single digit and we wait...
                    # Let's verify if the input_buffer corresponds to a valid index
                    
                    try:
                        idx = int(input_buffer) - 1
                        # If the number is large > len, maybe they meant single digit?
                        # But for now let's assume valid.
                        
                        if 0 <= idx < len(keys):
                            # Valid index!
                            # But wait, did they want to type 12 (index 11) or 1?
                            # If they typed '1', and there are > 9 items, we must wait.
                            if len(keys) > 9 and len(input_buffer) < 2 and int(input_buffer + "0") <= len(keys) + 9:
                                # Start a sort of 'wait' visual or just wait in loop
                                # Non-blocking wait
                                pass
                            else:
                                run_animation_from_dict(engine, keys[idx], anim_dict)
                                input_buffer = "" # Reset
                                break 
                                
                    except ValueError:
                        input_buffer = ""
                
            # Check timeout for single digit entry if we were waiting
            if input_buffer and (time.time() - last_input_time > 0.5):
                try:
                    idx = int(input_buffer) - 1
                    if 0 <= idx < len(keys):
                        run_animation_from_dict(engine, keys[idx], anim_dict)
                        break
                except:
                    pass
                input_buffer = ""
            
            time.sleep(0.02)


def main():
    """Main entry point."""
    engine = AnimationEngine()
    set_title("Terminal Animation Engine")
    
    try:
        while True:
            print_category_menu()
            
            # Top level input
            key = None
            while key is None:
                key = check_key()
                if key is None:
                    time.sleep(0.05)
            
            key = key.lower()
            
            if key == 'q':
                clear_screen()
                print("Thanks for using Terminal Animation Engine!")
                break
            elif key == 's':
                settings_menu(engine)
            elif key == 'r':
                # Random from all
                all_dicts = [ANIMATIONS, SCREENSAVERS_REGULAR, SCREENSAVERS_ULTRAWIDE, TIME_APPS]
                chosen_dict = random.choice(all_dicts)
                chosen_key = random.choice(list(chosen_dict.keys()))
                run_animation_from_dict(engine, chosen_key, chosen_dict)
            
            elif key == '1':
                handle_selection_screen(engine, "STANDARD ANIMATIONS", ANIMATIONS)
            elif key == '2':
                handle_selection_screen(engine, "SCREENSAVERS (16:9)", SCREENSAVERS_REGULAR)
            elif key == '3':
                handle_selection_screen(engine, "SCREENSAVERS (ULTRAWIDE)", SCREENSAVERS_ULTRAWIDE)
            elif key == '4':
                handle_selection_screen(engine, "TIME & UTILITY", TIME_APPS)

    except KeyboardInterrupt:
        clear_screen()
        print("\nExiting...")
    finally:
        show_cursor()

if __name__ == "__main__":
    main()
