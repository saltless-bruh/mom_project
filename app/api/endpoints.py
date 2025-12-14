import shutil
import uuid
import logging
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from app.models.schemas import InvoiceResponse, InvoiceListResponse, ValidationResult, ProcessResponse, AutomationStatusResponse
from app.models.database import db_manager
from app.services.pdf_processor import pdf_processor
from app.services.gemini_client import gemini_client
from app.services.validator import validator
from app.services.automation import automation_service

# Setup Logger
logger = logging.getLogger("maas.api")

router = APIRouter()

# Config (Should ideally be injected or loaded once)
UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/invoices/upload", response_model=InvoiceResponse)
async def upload_invoice(file: UploadFile = File(...)):
    """Upload a PDF invoice."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    # Generate ID and Path
    invoice_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{invoice_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create DB Record
        query = """
            INSERT INTO invoices (id, invoice_number, invoice_date, vendor_name, total_amount, pdf_path, status, subtotal, tax_total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # Initial dummy data until extraction
        await db_manager.execute_query(query, (
            invoice_id, 
            "PENDING", 
            "1970-01-01", 
            "Unknown", 
            0.0, 
            str(file_path), 
            "uploaded",
            0.0,
            0.0
        ))
        
        # Fetch back
        invoice = await db_manager.fetch_one("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        return InvoiceResponse.from_orm(invoice)
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/invoices", response_model=InvoiceListResponse)
async def get_invoices(
    page: int = 1, 
    size: int = 20, 
    status: Optional[str] = None
):
    """List invoices with pagination."""
    offset = (page - 1) * size
    
    # Count Total
    count_query = "SELECT COUNT(*) as count FROM invoices"
    params = ()
    if status:
        count_query += " WHERE status = ?"
        params = (status,)
    
    total_res = await db_manager.fetch_one(count_query, params)
    total = total_res["count"] if total_res else 0
    
    # Fetch Data
    query = "SELECT * FROM invoices"
    if status:
        query += " WHERE status = ?"
    query += " ORDER BY uploaded_at DESC LIMIT ? OFFSET ?"
    
    full_params = params + (size, offset)
    invoices = await db_manager.fetch_all(query, full_params)
    
    return {
        "invoices": [InvoiceResponse.from_orm(inv) for inv in invoices],
        "total": total,
        "page": page,
        "size": size
    }

async def background_extraction(invoice_id: str, pdf_path: str):
    """Background task to run Gemini extraction."""
    try:
        logger.info(f"Starting extraction for {invoice_id}")
        await db_manager.execute_query("UPDATE invoices SET status = 'extracting' WHERE id = ?", (invoice_id,))
        
        # 1. Convert to Images
        images = pdf_processor.convert_to_images(pdf_path)
        
        # 2. Extract Data
        data = gemini_client.extract_invoice_data(images)
        
        # 3. Update DB
        # Note: We need to map JSON result to DB columns carefully.
        # Ideally, we should validate it first, but let's save the raw extraction result 
        # (For MVP, we overwrite columns directly)
        
        update_query = """
            UPDATE invoices SET 
                vendor_name = ?,
                vendor_tax_id = ?,
                invoice_number = ?,
                invoice_date = ?,
                total_amount = ?,
                tax_total = ?,
                subtotal = ?,
                currency = ?,
                status = 'extracted',
                extracted_at = CURRENT_TIMESTAMP,
                gemini_cost_usd = ?,
                processing_time_ms = ?
            WHERE id = ?
        """
        
        # Calculate derived subtotal if missing
        total = data.get("total_amount", 0)
        items = data.get("items", [])
        subtotal = sum(item.get("total", 0) for item in items)
        tax = data.get("tax_amount", 0)
        
        meta = data.get("_metadata", {})
        
        await db_manager.execute_query(update_query, (
            data.get("vendor_name"),
            data.get("vendor_tax_id"),
            data.get("invoice_number"),
            data.get("invoice_date"),
            total,
            tax,
            subtotal,
            data.get("currency", "VND"),
            meta.get("estimated_cost_usd", 0),
            meta.get("processing_time_ms", 0),
            invoice_id
        ))
        
        # 4. Insert Items
        # Clear old items first (if retry)
        await db_manager.execute_query("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
        
        item_query = """
            INSERT INTO invoice_items (invoice_id, line_number, description, quantity, unit_price, total, unit)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        for i, item in enumerate(items):
            await db_manager.execute_query(item_query, (
                invoice_id,
                item.get("line_number", i+1),
                item.get("description"),
                item.get("quantity", 0),
                item.get("unit_price", 0),
                item.get("total", 0),
                item.get("unit")
            ))
            
        # Trigger Validation automatically?
        # For now, let UI trigger it or do it here. Let's do it here for full automation flow.
        await run_validation(invoice_id)
        
        logger.info(f"Extraction completed for {invoice_id}")
        
    except Exception as e:
        logger.error(f"Extraction failed for {invoice_id}: {e}")
        await db_manager.execute_query("UPDATE invoices SET status = 'failed' WHERE id = ?", (invoice_id,))

async def run_validation(invoice_id: str):
    """Run validation logic on an invoice."""
    # Fetch Data
    inv = await db_manager.fetch_one("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    items = await db_manager.fetch_all("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    
    # Construct Dict for Validator
    data = dict(inv)
    data["items"] = [dict(i) for i in items]
    
    # Validate
    result = validator.validate(data)
    
    # Update DB
    status = "validated" if result["is_valid"] else "needs_review"
    
    # Update Status & Metrics
    await db_manager.execute_query(
        "UPDATE invoices SET status = ?, validation_errors = ?, validated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, len(result["errors"]), invoice_id)
    )
    
    return result

@router.post("/invoices/{id}/process", response_model=ProcessResponse)
async def process_invoice(id: str, background_tasks: BackgroundTasks):
    """Trigger extraction process."""
    invoice = await db_manager.fetch_one("SELECT pdf_path FROM invoices WHERE id = ?", (id,))
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    
    background_tasks.add_task(background_extraction, id, invoice["pdf_path"])
    return {"message": "Processing started", "invoice_id": id, "status": "processing"}

@router.post("/invoices/{id}/validate", response_model=ValidationResult)
async def validate_invoice_endpoint(id: str):
    """Trigger validation manually."""
    invoice = await db_manager.fetch_one("SELECT * FROM invoices WHERE id = ?", (id,))
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    return await run_validation(id)

# --- Automation Endpoints ---

@router.get("/automation/status", response_model=AutomationStatusResponse)
async def get_automation_status():
    """Get current status of the automation service."""
    return automation_service.get_status()

@router.post("/automation/stop")
async def stop_automation():
    """Emergency stop (Kill Switch)."""
    automation_service.abort()
    return {"message": "Automation stop requested"}

@router.post("/automation/resume")
async def resume_automation():
    """Clear emergency stop flag."""
    automation_service.resume_from_error()
    return {"message": "Automation error state cleared"}

