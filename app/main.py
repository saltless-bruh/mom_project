import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

# Imports
from app.api import endpoints
from app.services.backup_service import backup_service
from scripts.init_db import init_db 

# Logger Setup
logging.basicConfig(
    filename='logs/maas.log', 
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("maas.main")

# App Lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up...")
    
    # 1. Initialize DB (safe to run multiple times)
    try:
        # We invoke the init_db logic if DB missing
        if not Path("data/maas.db").exists():
            init_db()
    except Exception as e:
        logger.error(f"DB Init failed: {e}")

    # 2. Start Scheduler
    backup_service.start()
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")
    backup_service.scheduler.shutdown()

app = FastAPI(title="Mom's Accounting Automation System", lifespan=lifespan)

# CORS checks (Allow localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For local app, * is fine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router
app.include_router(endpoints.router, prefix="/api")

# Static Files (Frontend)
# Serve "frontend" directory at root "/"
# Check if frontend exists
frontend_dir = Path("frontend")
frontend_dir.mkdir(exist_ok=True)
if not (frontend_dir / "index.html").exists():
    with open(frontend_dir / "index.html", "w") as f:
        f.write("<h1>MAAS Frontend Placeholder</h1>")

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Use config port
    uvicorn.run(app, host="0.0.0.0", port=8765)
