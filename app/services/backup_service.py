import shutil
import logging
from pathlib import Path
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger("maas.backup")

class BackupService:
    def __init__(self, db_path: str = "data/maas.db", backup_dir: str = "data/backups/"):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.scheduler = AsyncIOScheduler()
        
        # Ensure backup dir exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def start(self):
        """Start the backup scheduler."""
        # Schedule daily backup at 2:00 AM
        self.scheduler.add_job(
            self.perform_backup,
            CronTrigger(hour=2, minute=0),
            id="daily_backup",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Backup scheduler started.")

    def perform_backup(self):
        """Execute the backup logic."""
        try:
            if not self.db_path.exists():
                logger.warning(f"Database file {self.db_path} does not exist. Skipping backup.")
                return

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"maas_backup_{timestamp}.db"
            
            # Simple file copy (for SQLite, robust backup might need 'vacuum into' or API, 
            # but copy is sufficient if app traffic is low at 2AM or wal mode is on)
            shutil.copy2(self.db_path, backup_file)
            logger.info(f"Backup created successfully: {backup_file}")
            
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)

    def cleanup_old_backups(self, retention_days: int = 7):
        """Delete backups older than retention period."""
        try:
            # Sort backups by modification time
            backups = sorted(self.backup_dir.glob("maas_backup_*.db"), key=lambda f: f.stat().st_mtime)
            
            # If we have more backups than retention days (assuming 1 per day approx)
            # Better strategy: check file age
            import time
            current_time = time.time()
            cutoff_time = current_time - (retention_days * 86400)
            
            for backup in backups:
                if backup.stat().st_mtime < cutoff_time:
                    backup.unlink()
                    logger.info(f"Deleted old backup: {backup}")
                    
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}", exc_info=True)

# Global instance
backup_service = BackupService()
