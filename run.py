import os
import sys
import uvicorn
import yaml
import threading
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from dotenv import load_dotenv

# Load env immediately
load_dotenv()

# Add project root to path
ROOT_DIR = Path(__file__).parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import automation service for Kill Switch
from app.services.automation import automation_service
from app.services.config_client import load_config
import keyboard

config = load_config()

# --- Global Kill Switch ---
def setup_kill_switch():
    kill_key = config.get("app", {}).get("global_kill_switch", "F12")
    
    def on_kill():
        print(f"\n[KILL SWITCH] {kill_key} pressed! Stopping automation...")
        automation_service.abort()
        # Optionally exit app entirely? 
        # os._exit(1) # Very hard kill
        
    keyboard.add_hotkey(kill_key, on_kill)
    print(f"Global Kill Switch Active: Press {kill_key} to stop automation.")

setup_kill_switch()

def create_image():
    # Generate a simple icon image
    width = 64
    height = 64
    color1 = "blue"
    color2 = "white"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle((width // 2, 0, width, height // 2), fill=color2)
    dc.rectangle((0, height // 2, width // 2, height), fill=color2)
    return image

def run_server(host, port, app):
    uvicorn.run(app, host=host, port=port, log_level="error")

def on_quit(icon, item):
    icon.stop()
    # Remove PID file
    pid_file = ROOT_DIR / "maas.pid"
    if pid_file.exists():
        pid_file.unlink()
    os._exit(0)

if __name__ == "__main__":
    # Create PID file for shutdown script
    pid_file = ROOT_DIR / "maas.pid"
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
        
    try:
        config = load_config()
        host = config["server"]["host"]
        port = config["server"]["port"]
        
        # Create dummy app if needed
        try:
            from app.main import app
        except ImportError:
            from fastapi import FastAPI
            app = FastAPI()
            @app.get("/")
            def root():
                return {"message": "MAAS Backend Running"}
            @app.get("/health")
            def health():
                return {"status": "ok"}
        
        # Start Server in Thread
        server_thread = threading.Thread(target=run_server, args=(host, port, app))
        server_thread.daemon = True
        server_thread.start()
        
        # Start System Tray
        image = create_image()
        menu = pystray.Menu(
            pystray.MenuItem("Open", lambda: os.system(f"start http://{host}:{port}")),
            pystray.MenuItem("Exit", on_quit)
        )
        icon = pystray.Icon("MAAS", image, "Mom's Accounting System", menu)
        icon.run()
            
    finally:
        pass

