import aiosqlite
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

logger = logging.getLogger("maas.database")

# Default path, should come from config
DB_PATH = Path("data/maas.db")

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    @asynccontextmanager
    async def get_db_connection(self) -> AsyncGenerator[aiosqlite.Connection, None]:
        """Async context manager for database connection."""
        async with aiosqlite.connect(self.db_path) as db:
            # Enable foreign keys support
            await db.execute("PRAGMA foreign_keys = ON;")
            # Return connection with row factory for dict-like access
            db.row_factory = aiosqlite.Row
            yield db

    async def execute_query(self, query: str, params: tuple = ()) -> None:
        """Execute a single query (INSERT, UPDATE, DELETE)."""
        async with self.get_db_connection() as db:
            await db.execute(query, params)
            await db.commit()
    
    async def fetch_one(self, query: str, params: tuple = ()) -> dict:
        """Fetch a single row."""
        async with self.get_db_connection() as db:
            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        """Fetch all rows."""
        async with self.get_db_connection() as db:
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

# Global instance
db_manager = DatabaseManager()
