"""Main entry point for servitor system"""

import sys
import os


def main():
    """Main entry point - detects GUI or CLI mode"""
    # Check if GUI mode is requested or if DISPLAY is available
    gui_mode = False
    
    # Check command line arguments
    if '--gui' in sys.argv or '-g' in sys.argv:
        gui_mode = True
    elif '--cli' in sys.argv or '-c' in sys.argv:
        gui_mode = False
    else:
        # Auto-detect: use GUI if no arguments and DISPLAY is set (Unix/Linux)
        # On macOS/Windows, try GUI by default
        if len(sys.argv) == 1:
            if sys.platform == 'darwin' or sys.platform == 'win32':
                gui_mode = True
            elif 'DISPLAY' in os.environ:
                gui_mode = True
    
    if gui_mode:
        try:
            from .gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI mode not available: {e}")
            print("Falling back to CLI mode...")
            from .cli import main as cli_main
            cli_main()
    else:
        from .cli import main as cli_main
        cli_main()


if __name__ == '__main__':
    main()

