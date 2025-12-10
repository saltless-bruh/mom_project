import pytest
import aiosqlite
import os
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# Use a test database path
TEST_DB_PATH = ROOT_DIR / "data" / "test_maas.db"
os.environ["DATABASE_PATH"] = str(TEST_DB_PATH)

from app.models.database import db_manager, DatabaseManager
# Override global db path for tests
db_manager.db_path = TEST_DB_PATH
DatabaseManager.db_path = TEST_DB_PATH # if needed in class default

@pytest.fixture(autouse=True)
async def setup_db():
    # Setup: Create test DB with schema
    schema_path = ROOT_DIR / "app" / "models" / "schema.sql"
    async with aiosqlite.connect(TEST_DB_PATH) as db:
        with open(schema_path, "r") as f:
            await db.executescript(f.read())
        await db.commit()
    
    yield

    # Teardown: Remove test DB
    if TEST_DB_PATH.exists():
        try:
             # Ensure connection is closed before cleanup 
             # (handled by context managers in tests usually)
             pass
        except:
             pass
    # Actual cleanup might need to wait for file unlock on Windows
    # We'll try, but ignore errors for now (pytest handles temp dirs better usually)
    # TEST_DB_PATH.unlink(missing_ok=True) 

@pytest.mark.asyncio
async def test_vendor_crud():
    """Test Create Read Update Delete for Vendor"""
    # Create
    await db_manager.execute_query(
        "INSERT INTO vendors (name, tax_id) VALUES (?, ?)",
        ("Test Vendor", "123456")
    )
    
    # Read
    vendor = await db_manager.fetch_one("SELECT * FROM vendors WHERE tax_id = ?", ("123456",))
    assert vendor is not None
    assert vendor["name"] == "Test Vendor"
    
    # Update
    await db_manager.execute_query(
        "UPDATE vendors SET name = ? WHERE id = ?",
        ("Updated Vendor", vendor["id"])
    )
    updated = await db_manager.fetch_one("SELECT * FROM vendors WHERE id = ?", (vendor["id"],))
    assert updated["name"] == "Updated Vendor"
    
    # Delete
    await db_manager.execute_query("DELETE FROM vendors WHERE id = ?", (vendor["id"],))
    deleted = await db_manager.fetch_one("SELECT * FROM vendors WHERE id = ?", (vendor["id"],))
    assert deleted is None

@pytest.mark.asyncio
async def test_backup_service():
    """Test manual backup trigger"""
    from app.services.backup_service import BackupService
    
    backup_dir = ROOT_DIR / "data" / "test_backups"
    service = BackupService(db_path=str(TEST_DB_PATH), backup_dir=str(backup_dir))
    
    # Trigger backup
    service.perform_backup()
    
    # Check if file exists
    backups = list(backup_dir.glob("maas_backup_*.db"))
    assert len(backups) == 1
    
    # Cleanup
    import shutil
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
