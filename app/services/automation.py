import logging
import time
import os
from pywinauto import Application, Desktop
from pywinauto.findwindows import ElementNotFoundError
from typing import Dict, Any

logger = logging.getLogger("maas.automation")

class ACSoftAutomation:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = None
        self.main_window = None
        self._stop_requested = False
        
        # Configuration
        self.acsoft_path = config.get("acsoft", {}).get("executable_path", r"C:\Program Files\ACSoft\ACSoft.exe")
        self.window_title = config.get("acsoft", {}).get("window_title", "ACSoft")
        self.dry_run = config.get("automation", {}).get("dry_run", True)
        self.visual_delay = config.get("automation", {}).get("visual_delay", 1.0) # Seconds to pause/highlight
        
        # State exposure for UI
        self.is_running = False
        self.current_action_description = None
        self.emergency_stop_triggered = False

    def connect(self):
        """Connect to running ACSoft or launch it."""
        try:
            # Try connecting first
            logger.info("Attempting to connect to running ACSoft instance...")
            self.app = Application(backend="uia").connect(title_re=self.window_title)
            self.main_window = self.app.window(title_re=self.window_title)
            logger.info("Connected successfully.")
        except ElementNotFoundError:
            # Launch if not found
            if not os.path.exists(self.acsoft_path):
                 raise FileNotFoundError(f"ACSoft executable not found at {self.acsoft_path}")
            
            logger.info("Launching ACSoft...")
            self.app = Application(backend="uia").start(self.acsoft_path)
            # Wait for window
            time.sleep(5) 
            self.main_window = self.app.window(title_re=self.window_title)
            self.main_window.wait('visible', timeout=10)

    def abort(self):
        """Emergency stop signal (Kill Switch)."""
        logger.warning("Emergency Abort Triggered!")
        self._stop_requested = True
        self.emergency_stop_triggered = True
        self.is_running = False
        self.current_action_description = "EMERGENCY STOPPED"

    def resume_from_error(self):
        """Clear error flags to allow new jobs."""
        self._stop_requested = False
        self.emergency_stop_triggered = False
        self.current_action_description = None
        logger.info("Automation error state cleared by user.")

    def _check_abort(self):
        if self._stop_requested:
            self.is_running = False
            raise InterruptedError("Automation stopped by user (Kill Switch).")

    def _visual_anticipation(self, description: str, element=None):
        """
        Safety Feature: Move mouse, Draw Box, Wait, Then Act.
        """
        self._check_abort()
        self.current_action_description = description
        logger.info(f"[VISUAL] {description}")
        
        if self.dry_run:
            time.sleep(self.visual_delay)
            return

        # TODO: Implement PyWinAuto draw_outline() here if element is passed
        if element:
            try:
                element.draw_outline(colour='green', thickness=2)
            except:
                pass 
        
        # "Traffic Light" Pause
        time.sleep(self.visual_delay)

    def get_status(self):
        return {
            "is_running": self.is_running,
            "emergency_stop_triggered": self.emergency_stop_triggered,
            "current_action_description": self.current_action_description
        }

    def fill_invoice(self, data: Dict[str, Any]):
        """
        Main logic to fill invoice with Safety Delays.
        """
        self.is_running = True
        self.emergency_stop_triggered = False
        self._stop_requested = False

        try:
            if self.dry_run:
                self._visual_anticipation("DRY RUN: Starting Invoice Entry...")
                self._visual_anticipation(f"Typing Invoice #: {data.get('invoice_number')}")
                self._visual_anticipation(f"Typing Vendor: {data.get('vendor_name')}")
                self._visual_anticipation("Adding Line Items...")
                self._visual_anticipation("Reviewing Totals...")
                self.is_running = False
                self.current_action_description = None
                return True

            self._check_abort()
            
            # Real Logic Skeleton
            self.main_window.set_focus()
            
            # Example with Visual Anticipation
            # self._visual_anticipation("Focusing Invoice Number Field", txtInvoiceNum)
            # txtInvoiceNum.type_keys(data['invoice_number'])
            
            logger.info("Invoice filled (Real logic placeholder).")
            self.is_running = False
            self.current_action_description = None
            return True
            
        except Exception as e:
            self.is_running = False
            logger.error(f"Automation failed: {e}")
            if isinstance(e, InterruptedError):
                self.emergency_stop_triggered = True # Keep the flag up for UI
            raise

# Global Instance
from app.services.config_client import load_config
try:
    _config = load_config()
except:
    _config = {} # fallback
    
automation_service = ACSoftAutomation(_config)

