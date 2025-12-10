import shutil
import logging
from pathlib import Path
from datetime import datetime
import yaml

logger = logging.getLogger("maas.archiver")

class ArchiverService:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.config = self._load_config()
        self.archive_base = self.root_dir / self.config["storage"]["archive_path"]
        self.upload_dir = self.root_dir / self.config["storage"]["upload_path"]

    def _load_config(self):
        config_path = self.root_dir / "config.yaml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def archive_invoice(self, pdf_path: str, invoice_date: str = None) -> str:
        """
        Move PDF from uploads to archive/YYYY/MM/.
        Args:
            pdf_path: Absolute path to the current PDF.
            invoice_date: 'YYYY-MM-DD' string to determine folder structure. 
                          If None, uses current date.
        Returns:
            New absolute path of the archived file.
        """
        source = Path(pdf_path)
        if not source.exists():
            logger.error(f"Cannot archive missing file: {source}")
            return str(source)

        try:
            # Determine Year/Month
            if invoice_date:
                try:
                    dt = datetime.strptime(invoice_date, "%Y-%m-%d")
                    year = dt.strftime("%Y")
                    month = dt.strftime("%m")
                except ValueError:
                    # Fallback to current
                    now = datetime.now()
                    year = now.strftime("%Y")
                    month = now.strftime("%m")
            else:
                now = datetime.now()
                year = now.strftime("%Y")
                month = now.strftime("%m")

            # Create destination folder
            dest_dir = self.archive_base / year / month
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Move File (handle duplicates)
            dest_file = dest_dir / source.name
            if dest_file.exists():
                # Append timestamp to name
                timestamp = datetime.now().strftime("%H%M%S")
                dest_file = dest_dir / f"{source.stem}_{timestamp}{source.suffix}"

            shutil.move(str(source), str(dest_file))
            logger.info(f"Archived {source.name} to {dest_file}")
            return str(dest_file)

        except Exception as e:
            logger.error(f"Archival failed for {source}: {e}")
            return str(source) # Return original path if fail

# Global Instance? Needs ROOT_DIR. 
# We'll instantiate in main or via dependency injection pattern if simple.
