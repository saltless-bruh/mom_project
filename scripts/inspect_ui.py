import sys
import time
from pywinauto import Desktop

def inspect_active_window(delay=3):
    print(f"Switch to the target application now! Scanning in {delay} seconds...")
    time.sleep(delay)
    
    try:
        # Get foreground window
        desktop = Desktop(backend="uia")
        window = desktop.active() # Gets active window
        
        print("\n" + "="*50)
        print(f"Active Window: '{window.window_text()}'")
        print("="*50 + "\n")
        
        # Print Control Identifiers
        # dump_tree() is recursive and prints structure
        window.print_control_identifiers()
        
        print("\n" + "="*50)
        print("Scan Complete.")
        print("="*50)
        
    except Exception as e:
        print(f"Error inspecting window: {e}")

if __name__ == "__main__":
    inspect_active_window(5)
