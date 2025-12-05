# Technical Specifications

## Mom's Accounting Automation System

**Version:** 1.0  
**Last Updated:** December 5, 2025  
**Project Code:** MAAS (Mom's Accounting Automation System)

---

## 1. System Architecture

### 1.1 High-Level Architecture

```bash
┌─────────────────┐
│   Web UI        │ ← Mom's interface (upload, review, approve)
│  (Vue.js/HTML)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  FastAPI        │ ← Orchestration layer
│  Backend        │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬───────────┐
    ↓          ↓          ↓           ↓
┌─────────┐ ┌──────┐ ┌──────────┐ ┌─────────┐
│ Gemini  │ │SQLite│ │PyWinAuto │ │ Logging │
│   API   │ │  DB  │ │ ACSoft   │ │ System  │
└─────────┘ └──────┘ └──────────┘ └─────────┘
```

### 1.2 Component Layers

| Layer | Components | Responsibility |
|-------|-----------|----------------|
| **Presentation** | Vue.js UI, HTML forms | Upload PDFs, display extracted data, approve entries |
| **Application** | FastAPI REST API | Orchestrate workflow, business logic, validation |
| **Integration** | Gemini API client, PyWinAuto scripts | External system communication |
| **Data** | SQLite database, File storage | Persist invoices, audit logs, extracted data |
| **Automation** | PyWinAuto, PyAutoGUI | ACSoft GUI automation |

---

## 2. Detailed Component Specifications

### 2.1 PDF Processing Service

**Module:** `pdf_processor.py`

**Responsibilities:**

- Convert PDF to images (one per page)
- Send images to Gemini API with extraction prompt
- Parse JSON response
- Handle multi-page invoices

**Input:**

```python
{
    "pdf_path": "/path/to/invoice.pdf",
    "extraction_type": "purchase_invoice"  # or "sales_invoice", "receipt"
}
```

**Output:**

```python
{
    "status": "success",
    "confidence": 0.95,
    "data": {
        "vendor_name": "ABC Supplier Co., Ltd",
        "vendor_tax_id": "0123456789",
        "invoice_number": "INV-2025-001",
        "invoice_date": "2025-12-05",
        "currency": "VND",
        "items": [
            {
                "line_number": 1,
                "description": "Sản phẩm A",
                "quantity": 10,
                "unit": "thùng",
                "unit_price": 50000,
                "discount_percent": 5,
                "discount_amount": 25000,
                "tax_percent": 10,
                "tax_amount": 47500,
                "subtotal": 500000,
                "total": 522500
            }
        ],
        "subtotal": 500000,
        "discount_total": 25000,
        "tax_total": 47500,
        "total_amount": 522500,
        "notes": "Thanh toán trong 30 ngày",
        "payment_terms": "NET30"
    },
    "metadata": {
        "pages_processed": 2,
        "processing_time_ms": 1234,
        "gemini_model": "gemini-2.0-flash",
        "api_cost_usd": 0.032
    }
}
```

**API Configuration:**

```python
GEMINI_CONFIG = {
    "model": "gemini-2.0-flash",
    "temperature": 0.1,  # Low for consistency
    "top_p": 0.95,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json"
}
```

**Extraction Prompt Template:**

```bash
Extract all data from this Vietnamese purchase invoice and return as JSON with this structure:
{
  "vendor_name": string,
  "vendor_tax_id": string,
  "vendor_address": string,
  "invoice_number": string,
  "invoice_date": "YYYY-MM-DD",
  "currency": string (VND/USD),
  "items": [
    {
      "line_number": integer,
      "description": string,
      "quantity": number,
      "unit": string,
      "unit_price": number,
      "discount_percent": number,
      "discount_amount": number,
      "tax_percent": number,
      "tax_amount": number,
      "subtotal": number,
      "total": number
    }
  ],
  "subtotal": number,
  "discount_total": number,
  "tax_total": number,
  "total_amount": number,
  "notes": string,
  "payment_terms": string
}

Rules:
- All monetary amounts as numbers (no currency symbols)
- Dates in YYYY-MM-DD format
- Empty fields as null
- Calculate totals if not explicitly shown
- Preserve Vietnamese text exactly as shown
```

**Error Handling:**

```python
class PDFProcessingError(Exception):
    """Base exception for PDF processing"""
    pass

class GeminiAPIError(PDFProcessingError):
    """Gemini API call failed"""
    pass

class InvalidInvoiceError(PDFProcessingError):
    """Invoice structure invalid or incomplete"""
    pass

class LowConfidenceError(PDFProcessingError):
    """Extracted data confidence below threshold"""
    pass
```

---

### 2.2 Data Validation Service

**Module:** `validator.py`

**Responsibilities:**

- Validate extracted data completeness
- Normalize formats (dates, currency, decimals)
- Cross-check calculations (subtotals, taxes, totals)
- Flag anomalies for review

**Validation Rules:**

```python
VALIDATION_RULES = {
    "required_fields": [
        "vendor_name",
        "invoice_number", 
        "invoice_date",
        "items",
        "total_amount"
    ],
    "date_format": "%Y-%m-%d",
    "currency_allowed": ["VND", "USD"],
    "tax_rates_allowed": [0, 5, 8, 10],  # Vietnam tax rates
    "discount_max_percent": 50,
    "amount_precision": 0,  # VND has no decimals
    "calculation_tolerance": 1  # Allow 1 VND rounding error
}
```

**Validation Output:**

```python
{
    "is_valid": true,
    "confidence": 0.95,
    "warnings": [
        {
            "field": "items[0].discount_percent",
            "message": "Unusual discount: 45%",
            "severity": "warning"
        }
    ],
    "errors": [],
    "normalized_data": {
        # Same structure as input, with normalized values
    },
    "calculation_check": {
        "subtotal_match": true,
        "tax_match": true,
        "total_match": true,
        "differences": {}
    }
}
```

**Calculation Verification:**

```python
def verify_calculations(data: dict) -> dict:
    """
    Verify all arithmetic in invoice:
    - Item subtotal = quantity × unit_price
    - Item discount = subtotal × discount_percent
    - Item tax = (subtotal - discount) × tax_percent
    - Item total = subtotal - discount + tax
    - Invoice subtotal = sum(item subtotals)
    - Invoice tax_total = sum(item taxes)
    - Invoice total = subtotal - discount_total + tax_total
    """
    pass
```

---

### 2.3 ACSoft Automation Service

**Module:** `acsoft_automation.py`

**Responsibilities:**

- Connect to ACSoft application
- Navigate to data entry screens
- Fill form fields with validated data
- Take screenshots for audit trail
- Handle errors gracefully

**ACSoft UI Element Map:**

```python
ACSOFT_ELEMENTS = {
    "main_window": {"title_re": ".*ACSoft.*"},
    "menu": {
        "purchasing": {"name": "Mua hàng"},
        "new_invoice": {"name": "Nhập hóa đơn mới"}
    },
    "invoice_form": {
        "vendor_name": {"auto_id": "txtVendorName"},
        "invoice_number": {"auto_id": "txtInvoiceNumber"},
        "invoice_date": {"auto_id": "dtpInvoiceDate"},
        "item_grid": {"auto_id": "dgvItems"},
        "save_button": {"name": "Lưu"},
        "cancel_button": {"name": "Hủy"}
    },
    "item_row": {
        "description": {"column": 0},
        "quantity": {"column": 1},
        "unit": {"column": 2},
        "unit_price": {"column": 3},
        "discount_percent": {"column": 4},
        "tax_percent": {"column": 5},
        "total": {"column": 6}
    }
}
```

**Automation Workflow:**

```python
class ACSoftAutomation:
    def connect(self) -> bool:
        """Connect to running ACSoft instance"""
        
    def navigate_to_invoice_entry(self) -> bool:
        """Navigate to new invoice entry screen"""
        
    def fill_header(self, invoice_data: dict) -> bool:
        """Fill invoice header fields"""
        
    def fill_items(self, items: list) -> bool:
        """Fill line items in grid"""
        
    def take_screenshot(self, step: str) -> str:
        """Take screenshot and return path"""
        
    def verify_form_state(self) -> dict:
        """Read back form values to verify"""
        
    def wait_for_user_confirmation(self) -> bool:
        """Pause and wait for mom to review and save"""
```

**Safety Features:**

```python
SAFETY_CONFIG = {
    "screenshot_before_action": True,
    "verify_after_input": True,
    "auto_save_enabled": False,  # NEVER auto-save
    "pause_on_error": True,
    "max_retry_attempts": 3,
    "action_delay_ms": 500,  # Delay between actions
    "ui_timeout_seconds": 30
}
```

---

### 2.4 FastAPI Backend

**Module:** `main.py`

**API Endpoints:**

```python
# Upload invoice PDF
POST /api/invoices/upload
Content-Type: multipart/form-data
Body: {file: binary}
Response: {invoice_id: str, status: str}

# Get extraction results
GET /api/invoices/{invoice_id}/extraction
Response: {data: dict, validation: dict}

# Update extracted data (manual corrections)
PUT /api/invoices/{invoice_id}/data
Body: {corrected_data: dict}
Response: {status: str}

# Trigger ACSoft automation
POST /api/invoices/{invoice_id}/automate
Response: {status: str, automation_id: str}

# Get automation status
GET /api/automation/{automation_id}/status
Response: {status: str, progress: dict, screenshots: list}

# Mark invoice as completed
POST /api/invoices/{invoice_id}/complete
Body: {notes: str}
Response: {status: str}

# List all invoices
GET /api/invoices?status=pending&limit=50&offset=0
Response: {invoices: list, total: int}

# Get audit log
GET /api/audit?invoice_id={id}&from={date}&to={date}
Response: {logs: list}
```

**Data Models:**

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class InvoiceItem(BaseModel):
    line_number: int
    description: str
    quantity: float
    unit: str
    unit_price: float
    discount_percent: float = 0
    discount_amount: float = 0
    tax_percent: float = 10
    tax_amount: float
    subtotal: float
    total: float

class Invoice(BaseModel):
    id: Optional[str]
    vendor_name: str
    vendor_tax_id: Optional[str]
    invoice_number: str
    invoice_date: datetime
    currency: str = "VND"
    items: List[InvoiceItem]
    subtotal: float
    discount_total: float = 0
    tax_total: float
    total_amount: float
    notes: Optional[str]
    payment_terms: Optional[str]
    
    # Metadata
    uploaded_at: Optional[datetime]
    processed_at: Optional[datetime]
    status: str = "pending"  # pending, extracted, validated, automated, completed
    confidence: Optional[float]
    pdf_path: Optional[str]

class AutomationResult(BaseModel):
    automation_id: str
    invoice_id: str
    status: str  # running, paused, completed, failed
    started_at: datetime
    completed_at: Optional[datetime]
    screenshots: List[str]
    errors: List[str]
    notes: Optional[str]
```

---

### 2.5 Database Schema

**SQLite Database:** `maas.db`

```sql
-- Vendors table
CREATE TABLE vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    tax_id TEXT UNIQUE,
    address TEXT,
    phone TEXT,
    email TEXT,
    payment_terms TEXT DEFAULT 'NET30',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table
CREATE TABLE invoices (
    id TEXT PRIMARY KEY,  -- UUID
    vendor_id INTEGER,
    vendor_name TEXT NOT NULL,
    vendor_tax_id TEXT,
    invoice_number TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    currency TEXT DEFAULT 'VND',
    subtotal REAL NOT NULL,
    discount_total REAL DEFAULT 0,
    tax_total REAL NOT NULL,
    total_amount REAL NOT NULL,
    notes TEXT,
    payment_terms TEXT,
    
    -- File tracking
    pdf_path TEXT NOT NULL,
    pdf_hash TEXT,  -- SHA256 for duplicate detection
    
    -- Processing metadata
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    extracted_at TIMESTAMP,
    validated_at TIMESTAMP,
    automated_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Status tracking
    status TEXT DEFAULT 'pending',  
    -- pending, extracting, extracted, validated, automating, completed, failed
    
    -- Quality metrics
    extraction_confidence REAL,
    validation_errors INTEGER DEFAULT 0,
    manual_corrections INTEGER DEFAULT 0,
    
    -- Gemini API tracking
    gemini_cost_usd REAL,
    processing_time_ms INTEGER,
    
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    UNIQUE(vendor_id, invoice_number, invoice_date)
);

-- Invoice items table
CREATE TABLE invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    description TEXT NOT NULL,
    quantity REAL NOT NULL,
    unit TEXT NOT NULL,
    unit_price REAL NOT NULL,
    discount_percent REAL DEFAULT 0,
    discount_amount REAL DEFAULT 0,
    tax_percent REAL DEFAULT 10,
    tax_amount REAL NOT NULL,
    subtotal REAL NOT NULL,
    total REAL NOT NULL,
    
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
    UNIQUE(invoice_id, line_number)
);

-- Automation runs table
CREATE TABLE automation_runs (
    id TEXT PRIMARY KEY,  -- UUID
    invoice_id TEXT NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT DEFAULT 'running',  -- running, paused, completed, failed
    error_message TEXT,
    screenshots_path TEXT,  -- JSON array of screenshot paths
    actions_log TEXT,  -- JSON log of all actions taken
    
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);

-- Audit log table
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user TEXT DEFAULT 'system',
    action TEXT NOT NULL,  -- upload, extract, validate, correct, automate, complete
    entity_type TEXT NOT NULL,  -- invoice, item, automation
    entity_id TEXT NOT NULL,
    details TEXT,  -- JSON details of the action
    status TEXT,  -- success, warning, error
    ip_address TEXT,
    user_agent TEXT
);

-- Configuration table
CREATE TABLE config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_date ON invoices(invoice_date DESC);
CREATE INDEX idx_invoices_vendor ON invoices(vendor_id);
CREATE INDEX idx_invoices_pdf_hash ON invoices(pdf_hash);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);
```

---

## 3. Configuration Management

**Configuration File:** `config.yaml`

```yaml
# Application settings
app:
  name: "Mom's Accounting Automation System"
  version: "1.0.0"
  environment: "production"  # development, staging, production
  debug: false
  log_level: "INFO"

# Server settings
server:
  host: "127.0.0.1"  # Local only
  port: 8000
  workers: 1
  reload: false

# Gemini API settings
gemini:
  api_key_env: "GEMINI_API_KEY"  # Read from environment variable
  model: "gemini-2.0-flash"
  temperature: 0.1
  max_tokens: 8192
  timeout_seconds: 30
  retry_attempts: 3
  cost_tracking: true

# Database settings
database:
  path: "./data/maas.db"
  backup_path: "./data/backups/"
  backup_frequency_hours: 24
  
# File storage settings
storage:
  upload_path: "./data/uploads/"
  processed_path: "./data/processed/"
  screenshots_path: "./data/screenshots/"
  max_file_size_mb: 50
  allowed_extensions: [".pdf"]

# ACSoft automation settings
acsoft:
  executable_path: "C:\\Program Files\\ACSoft\\ACSoft.exe"
  window_title: "ACSoft"
  auto_launch: false
  connection_timeout_seconds: 30
  action_delay_ms: 500
  screenshot_before_action: true
  auto_save: false  # MUST be false

# Validation settings
validation:
  min_confidence: 0.85
  required_fields: ["vendor_name", "invoice_number", "invoice_date", "total_amount"]
  calculation_tolerance: 1
  tax_rates: [0, 5, 8, 10]
  max_discount_percent: 50

# Security settings
security:
  allowed_ips: ["127.0.0.1", "::1"]  # Local only
  api_key_required: false  # For local use
  cors_enabled: true
  cors_origins: ["http://localhost:3000", "http://127.0.0.1:8000"]

# Monitoring settings
monitoring:
  audit_log_enabled: true
  performance_tracking: true
  error_reporting: true
  metrics_retention_days: 90
```

**Environment Variables:**

```bash
# .env file
GEMINI_API_KEY=your_api_key_here
ACSOFT_DB_PATH=C:\ACSoft\Data\acsoft.db  # If needed
LOG_LEVEL=INFO
ENVIRONMENT=production
```

---

## 4. Error Handling Strategy

### 4.1 Error Categories

```python
class ErrorCategory(Enum):
    VALIDATION = "validation"
    EXTRACTION = "extraction"
    AUTOMATION = "automation"
    SYSTEM = "system"
    USER = "user"

class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
```

### 4.2 Error Response Format

```python
{
    "error": {
        "code": "GEMINI_API_ERROR",
        "message": "Failed to extract invoice data",
        "category": "extraction",
        "severity": "error",
        "details": {
            "api_status": 503,
            "retry_after": 60
        },
        "timestamp": "2025-12-05T10:30:00Z",
        "request_id": "req_abc123"
    },
    "recovery_suggestions": [
        "Wait 60 seconds and try again",
        "Check internet connection",
        "Verify Gemini API key is valid"
    ]
}
```

### 4.3 Retry Logic

```python
RETRY_CONFIG = {
    "gemini_api": {
        "max_attempts": 3,
        "backoff_multiplier": 2,
        "initial_delay_seconds": 1
    },
    "acsoft_connection": {
        "max_attempts": 5,
        "backoff_multiplier": 1.5,
        "initial_delay_seconds": 2
    },
    "database_operations": {
        "max_attempts": 3,
        "backoff_multiplier": 1,
        "initial_delay_seconds": 0.5
    }
}
```

---

## 5. Performance Requirements

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| PDF extraction time | < 5 seconds per page | Timer around Gemini API call |
| Data validation time | < 1 second | Timer around validation function |
| ACSoft automation time | < 30 seconds per invoice | Timer around automation workflow |
| End-to-end processing | < 2 minutes per invoice | Upload to automation complete |
| API response time | < 500ms (except extraction) | FastAPI middleware timing |
| Database query time | < 100ms | SQLite EXPLAIN QUERY PLAN |
| Concurrent invoices | 1 (sequential processing) | Single worker configuration |

---

## 6. Security Requirements

### 6.1 Data Security

- All data stored locally on mom's computer
- SQLite database with file-system permissions (chmod 600)
- No cloud storage of invoice PDFs
- Gemini API calls over HTTPS only
- API keys stored in environment variables (not in code)

### 6.2 Access Control

- Web UI accessible only from localhost
- No external network access required (except Gemini API)
- No user authentication needed (single-user system)
- Audit log of all operations

### 6.3 Data Privacy

- Invoice PDFs never leave local machine (except Gemini processing)
- Gemini API calls comply with Google Cloud privacy terms
- No telemetry or analytics sent externally
- Vendor data anonymized in error logs

---

## 7. Testing Requirements

### 7.1 Unit Tests

- PDF processing functions
- Validation logic
- Calculation verification
- Database operations
- API endpoints

**Test Coverage Target:** 80%+

### 7.2 Integration Tests

- End-to-end invoice processing
- Gemini API integration
- ACSoft automation workflow
- Error handling scenarios

### 7.3 Test Data

- Collect 20-30 sample invoices from different vendors
- Include edge cases:
  - Multi-page invoices
  - Missing optional fields
  - Unusual discounts
  - Multiple tax rates
  - Handwritten notes
  - Poor scan quality

### 7.4 User Acceptance Testing

- Mom processes 10-20 real invoices with system
- Measure time savings
- Collect feedback on UI/UX
- Identify edge cases not covered
- Verify accuracy of extracted data

---

## 8. Deployment Specifications

### 8.1 System Requirements

**Hardware:**

- Windows 10/11 (64-bit)
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Stable internet connection (for Gemini API)

**Software:**

- Python 3.9 or higher
- ACSoft (pre-installed)
- Modern web browser (Chrome, Firefox, Edge)

### 8.2 Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/yourusername/mom-accounting-automation.git
cd mom-accounting-automation

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up configuration
cp .env.example .env
# Edit .env and add GEMINI_API_KEY

# 5. Initialize database
python scripts/init_db.py

# 6. Run tests
pytest tests/

# 7. Start application
python run.py
```

### 8.3 Auto-Start Configuration

**Windows Task Scheduler:**

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>C:\Path\To\mom-accounting-automation\venv\Scripts\python.exe</Command>
      <Arguments>run.py</Arguments>
      <WorkingDirectory>C:\Path\To\mom-accounting-automation</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
```

---

## 9. Monitoring & Maintenance

### 9.1 Health Checks

```python
# Health check endpoint
GET /api/health
Response: {
    "status": "healthy",
    "timestamp": "2025-12-05T10:30:00Z",
    "components": {
        "database": "healthy",
        "gemini_api": "healthy",
        "acsoft_connection": "healthy",
        "disk_space": "healthy"
    },
    "metrics": {
        "invoices_today": 15,
        "processing_time_avg_seconds": 45,
        "error_rate_percent": 2
    }
}
```

### 9.2 Daily Maintenance Tasks

- Database backup (automated)
- Clean up old screenshots (> 30 days)
- Archive processed invoices (> 90 days)
- Review error logs
- Check disk space

### 9.3 Metrics to Track

- Invoices processed per day
- Average processing time
- Extraction accuracy rate
- Automation success rate
- Manual correction frequency
- Gemini API costs
- Error frequency by type

---

## 10. Future Enhancement Specifications

### 10.1 Email Integration

- Connect to mom's email (IMAP)
- Auto-download invoice attachments
- Parse email metadata for context
- Queue invoices for processing

### 10.2 Machine Learning Optimization

- Learn vendor-specific patterns
- Improve field mapping over time
- Predict item categories
- Anomaly detection for fraudulent invoices

### 10.3 Mobile App

- React Native mobile app
- Upload photos of paper invoices
- Review/approve on mobile
- Push notifications for processing status

### 10.4 Multi-User Support

- User authentication
- Role-based access control
- Multi-tenant data isolation
- Collaborative review workflow

---

## Appendix A: Technology Stack Details

```python
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
google-generativeai==0.3.1
pywinauto==0.6.8
pyautogui==0.9.54
pillow==10.1.0
pypdf==3.17.1
python-multipart==0.0.6
python-dotenv==1.0.0
pyyaml==6.0.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

---

## Appendix B: File Structure

```bash
mom-accounting-automation/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Configuration loader
│   ├── models.py               # Pydantic models
│   ├── database.py             # SQLAlchemy setup
│   ├── api/
│   │   ├── __init__.py
│   │   ├── invoices.py         # Invoice endpoints
│   │   ├── automation.py       # Automation endpoints
│   │   └── audit.py            # Audit endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── pdf_processor.py    # PDF extraction
│   │   ├── validator.py        # Data validation
│   │   ├── acsoft_automation.py # ACSoft automation
│   │   └── gemini_client.py    # Gemini API wrapper
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging setup
│       └── helpers.py          # Helper functions
├── frontend/
│   ├── index.html              # Main UI
│   ├── app.js                  # Vue.js app
│   └── style.css               # Styling
├── tests/
│   ├── __init__.py
│   ├── test_pdf_processor.py
│   ├── test_validator.py
│   ├── test_automation.py
│   └── test_api.py
├── scripts/
│   ├── init_db.py              # Database initialization
│   ├── backup.py               # Backup script
│   └── migrate.py              # Data migration
├── data/                        # Created at runtime
│   ├── maas.db                 # SQLite database
│   ├── uploads/                # Uploaded PDFs
│   ├── processed/              # Processed invoices
│   ├── screenshots/            # Automation screenshots
│   └── backups/                # Database backups
├── logs/                        # Application logs
├── config.yaml                  # Configuration file
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── README.md                    # User documentation
├── TECHNICAL_SPECS.md          # This file
└── run.py                       # Application entry point
```

---

**Document Status:** DRAFT - Ready for Implementation  
**Next Review Date:** After Phase 1 MVP completion
