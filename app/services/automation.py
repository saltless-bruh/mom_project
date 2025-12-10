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
        """Emergency stop signal."""
        logger.warning("Emergency Abort Triggered!")
        self._stop_requested = True

    def _check_abort(self):
        if self._stop_requested:
            raise InterruptedError("Automation stopped by user (Kill Switch).")

    def fill_invoice(self, data: Dict[str, Any]):
        """
        Main logic to fill invoice. 
        Note: Control identifiers are currently placeholders.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would fill invoice {data.get('invoice_number')}")
            return True

        self._check_abort()
        
        try:
            # Focus Window
            self.main_window.set_focus()
            
            # Example Placeholder Logic (Needs `inspect_ui.py` results to be real)
            # 1. Navigate to 'Invoice Entry' (Hypothetical shortcut or menu)
            # self.main_window.menu_select("Data Entry -> Invoices")
            
            # 2. Header
            # self.main_window.child_window(auto_id="txtInvoiceNum").type_keys(data['invoice_number'])
            # self.main_window.child_window(auto_id="txtDate").type_keys(data['invoice_date'])
            
            # 3. Items
            # for item in data['items']:
            #     self.main_window.child_window(auto_id="gridItems").type_keys(...)
            
            logger.info("Invoice filled (Placeholder logic).")
            return True
            
        except Exception as e:
            logger.error(f"Automation failed: {e}")
            raise

# Global Instance
from app.services.config_client import load_config
try:
    _config = load_config()
except:
    _config = {} # fallback
    
automation_service = ACSoftAutomation(_config)
