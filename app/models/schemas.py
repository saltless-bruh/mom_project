from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import date, datetime

# --- Shared Models ---

class InvoiceItemBase(BaseModel):
    line_number: Optional[int] = None
    description: str
    quantity: float = 0.0
    unit: Optional[str] = None
    unit_price: float = 0.0
    total: float = 0.0
    tax_percent: Optional[float] = None
    tax_amount: float = 0.0

class InvoiceBase(BaseModel):
    vendor_name: str
    vendor_tax_id: Optional[str] = None
    invoice_number: str
    invoice_date: Optional[str] = None # String to allow "YYYY-MM-DD" parsing
    currency: str = "VND"
    subtotal: float = 0.0
    tax_total: float = 0.0
    total_amount: float = 0.0
    items: List[InvoiceItemBase] = []

# --- Request Models ---

class InvoiceUpdateRequest(InvoiceBase):
    pass

# --- Response Models ---

class InvoiceItemResponse(InvoiceItemBase):
    id: int

class InvoiceResponse(InvoiceBase):
    id: str
    status: str
    pdf_path: str
    uploaded_at: datetime
    # Metadata
    validation_errors: Optional[int] = 0
    manual_corrections: Optional[int] = 0
    
    class Config:
        from_attributes = True

class InvoiceListResponse(BaseModel):
    invoices: List[InvoiceResponse]
    total: int
    page: int
    size: int
    
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    normalized_data: dict

class ProcessResponse(BaseModel):
    message: str
    invoice_id: str
    status: str

class AutomationStatusResponse(BaseModel):
    is_running: bool
    emergency_stop_triggered: bool
    current_action_description: Optional[str] = None
