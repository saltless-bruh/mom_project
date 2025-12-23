# System Design Document

## Mom's Accounting Automation System (MAAS)

**Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Initial Design

---

## 1. Architecture Overview

### 1.1 High-Level Architecture

```bash
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │  Web UI     │  │  Upload     │  │   Review     │         │
│  │  (Vue.js)   │  │  Interface  │  │   Interface  │         │
│  └─────────────┘  └─────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────┐
│                    Application Layer                        │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐         │
│  │  FastAPI    │  │  Business   │  │  Workflow    │         │
│  │  Router     │  │  Logic      │  │  Orchestrator│         │
│  └─────────────┘  └─────────────┘  └──────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼──────────────────┐
        │                   │                  │
┌───────▼──────┐  ┌─────────▼────────┐  ┌──────▼────────┐
│ Integration  │  │   Data Layer     │  │  Automation   │
│   Layer      │  │                  │  │    Layer      │
│              │  │                  │  │               │
│ ┌──────────┐ │  │ ┌──────────────┐ │  │ ┌───────────┐ │
│ │ Gemini   │ │  │ │   SQLite     │ │  │ │ PyWinAuto │ │
│ │   API    │ │  │ │   Database   │ │  │ │  Engine   │ │
│ └──────────┘ │  │ └──────────────┘ │  │ └───────────┘ │
│              │  │                  │  │               │
│ ┌──────────┐ │  │ ┌──────────────┐ │  │ ┌───────────┐ │
│ │  PDF     │ │  │ │ File Storage │ │  │ │ PyAutoGUI │ │
│ │Processor │ │  │ │              │ │  │ │  Fallback │ │
│ └──────────┘ │  │ └──────────────┘ │  │ └───────────┘ │
└──────────────┘  └──────────────────┘  └───────────────┘
```

### 1.2 Component Interaction Flow

```bash
1. User uploads PDF → Web UI
2. Web UI → FastAPI → PDF Processor
3. PDF Processor → Gemini API (extract data)
4. Gemini API → Validator Service
5. Validator → Database (store results)
6. Database → Web UI (display for review)
7. User approves → Automation Service
8. Automation Service → ACSoft (fill forms)
9. User reviews in ACSoft → Manual save
10. Automation Service → Database (log completion)
```

---

## 2. Component Design

### 2.1 PDF Processing Service

**Purpose:** Extract structured data from Vietnamese invoice PDFs

**Design Pattern:** Service Layer Pattern

**Key Components:**

- `PDFConverter`: Converts PDF pages to images
- `GeminiClient`: Interfaces with Gemini API
- `ResponseParser`: Parses JSON responses
- `ConfidenceScorer`: Evaluates extraction quality

**Data Flow with Human Review:**

```bash
Step 1: Upload & Preview (NO AI YET)
PDF File → PDFConverter → Images/Text Preview → 
Display to Mom → Mom Reviews PDF Quality

Step 2: Mom Initiates Extraction (AI STARTS HERE)
Mom clicks "Extract Data" → GeminiClient API Call → 
Raw JSON → ResponseParser → Structured Data

Step 3: Human Review & Correction
Structured Data → Display in Editable Form → 
Mom Reviews/Edits Data → Mom Clicks "Submit"

Step 4: Validation & Storage
Submitted Data → Validator → ConfidenceScorer → 
Database Storage → Ready for Automation
```

**Key Design Decision: AI Triggered by User Action**

**Why AI starts AFTER mom clicks "Extract Data" (not on upload):**

1. ✅ **Cost Control**: Gemini API costs $$ per call - only call when user confirms
2. ✅ **Quality Check**: Mom can verify PDF quality before wasting API call
3. ✅ **User Control**: Mom decides when to process (not automatic)
4. ✅ **Error Prevention**: Bad scans detected before API call
5. ✅ **Audit Trail**: Clear user intent logged

**Workflow Timeline:**

```bash
0:00 - Mom uploads PDF → Preview shown instantly (NO API call)
0:05 - Mom reviews PDF → "Looks good, extract this"
0:06 - Mom clicks "Extract Data" → Gemini API called NOW
0:08 - Extraction results shown → Mom reviews/edits
0:10 - Mom clicks "Submit" → Data validated and stored
0:11 - Ready for automation
```

**Error Handling:**

- Retry with exponential backoff for API failures
- Fallback to page-by-page processing for large files
- Capture and log all API errors
- Return partial results with warnings
- Allow mom to retry or manual entry if extraction fails

### 2.2 Data Validation Service

**Purpose:** Ensure data integrity and business rule compliance

**Design Pattern:** Chain of Responsibility Pattern

**Validation Chain:**

1. **Structure Validator**: Required fields present
2. **Format Validator**: Date, currency, number formats
3. **Business Rule Validator**: Tax rates, discount limits
4. **Calculation Validator**: Arithmetic accuracy
5. **Duplicate Detector**: Check for existing invoices

**Output:**

- `is_valid`: Boolean
- `confidence`: Float (0-1)
- `errors`: List of critical issues
- `warnings`: List of non-blocking issues
- `normalized_data`: Cleaned and formatted data

### 2.3 ACSoft Automation Service

**Purpose:** Automate data entry into ACSoft GUI via Excel Import

**Design Pattern:** Strategy Pattern (Pivot from direct GUI manipulation)

**Workflow:**

1. **Generate Bridge File:** Convert validated invoice data into ACSoft-compatible Excel format (`.xls` or `.xlsx`).
2. **Launch Import:** Use `pywinauto` to navigate ACSoft menus: `Data Entry` -> `Import Assistant`.
3. **Select File:** Automate file selection dialog to pick the generated bridge file.
4. **Confirm:** Handle confirmation popups.

**Advantages:**

- **Atomic Operation:** Data is imported all-at-once, reducing risk of partial entry.
- **Reviewable Artifact:** The generated Excel file serves as a final check and backup.
- **Robustness:** Unaffected by UI lag or minor layout changes (as long as menu structure persists).

**Safety Mechanisms:**

- **Global Kill Switch (F12):** Immediately terminates automation thread.
- **Visual Delay:** Brief pause before clicking "Import" to allow user intervention.
- **Pre-flight Check:** Verify ACSoft is ready and no other modal is open.

### 2.4 PDF Preview & Human Review Interface

**Purpose:** Allow mom to verify PDF quality and review extracted data before processing

**Design Pattern:** Two-Phase Preview Pattern

#### Phase 1: PDF Quality Preview (Before AI Extraction)

**Component: PDF Preview Service**

```python
class PDFPreviewService:
    """Generate preview of uploaded PDF for quality check"""
    
    def generate_preview(self, pdf_path: str) -> PDFPreview:
        """
        Convert PDF to images and extract basic text for preview.
        NO AI/Gemini call at this stage - just basic PDF rendering.
        
        Returns:
            PDFPreview with images and raw text for display
        """
        pages = []
        for page_num in range(pdf.page_count):
            # Convert to image (thumbnail for preview)
            image = pdf_page_to_image(page_num, dpi=150)
            
            # Extract basic text (PyMuPDF/pdfplumber - local, fast, free)
            raw_text = extract_text_from_page(page_num)
            
            pages.append({
                "page_number": page_num + 1,
                "thumbnail": image_to_base64(image),
                "raw_text": raw_text,
                "size": (image.width, image.height)
            })
        
        return PDFPreview(
            filename=pdf_path,
            page_count=len(pages),
            pages=pages,
            file_size=get_file_size(pdf_path)
        )
```

**UI Flow:**

```bash
┌─────────────────────────────────────────────────────────────┐
│ MAAS - Invoice Upload                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Drag PDF here or Click to Upload]                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘

After Upload (NO AI YET):

┌──────────────────────────────────────────────────────────────┐
│ MAAS - PDF Preview                      [X Close]            │
├──────────────────────────────────────────────────────────────┤
│ ┌──────────────────┐  ┌───────────────────────────────────┐  │
│ │  PDF Thumbnail   │  │ Raw Text Preview (Basic OCR)      │  │
│ │                  │  │                                   │  │
│ │  [Page 1 image]  │  │ Công ty TNHH ABC                  │  │
│ │                  │  │ Địa chỉ: ...                      │  │
│ │                  │  │ Mã số thuế: ...                   │  │
│ │                  │  │                                   │  │
│ │  Page 1 of 2     │  │ HÓA ĐƠN BÁN HÀNG                  │  │
│ │  [< Prev] [Next>]│  │ Số: INV-001                       │  │
│ │                  │  │ ...                               │  │
│ └──────────────────┘  └───────────────────────────────────┘  │
│                                                              │
│ Quality Check:                                               │
│ ✅ Text is readable                                          │
│ ✅ Image is clear                                            │
│ ✅ All pages present                                         │
│                                                              │
│ [❌ Cancel]  [✅ Extract Data with AI] ← AI starts HERE     │
└──────────────────────────────────────────────────────────────┘
```

**Key Points:**

- ✅ **Instant preview** - Uses free local PDF libraries (PyMuPDF/pdfplumber)
- ✅ **No cost** - No Gemini API call yet
- ✅ **Quality check** - Mom can see if scan is readable
- ✅ **Cancel if bad** - Mom can reject and rescan without wasting API call

#### Phase 2: Structured Data Review (After AI Extraction)

**Component: Markdown Comparison View**

```python
class ExtractionReviewService:
    """Present extracted data in editable markdown format"""
    
    def format_extraction_as_markdown(self, invoice_data: dict) -> str:
        """
        Convert extracted JSON data to readable markdown format
        that mom can edit before submission.
        """
        md = f"""
# Invoice Data Review

## 📄 Header Information
- **Vendor Name**: {invoice_data['vendor_name']}
- **Vendor Address**: {invoice_data.get('vendor_address', 'N/A')}
- **Tax ID**: {invoice_data.get('tax_id', 'N/A')}
- **Invoice Number**: {invoice_data['invoice_number']}
- **Invoice Date**: {invoice_data['invoice_date']}
- **Due Date**: {invoice_data.get('due_date', 'N/A')}

## 🛒 Line Items
| # | Description | Quantity | Unit Price | Amount |
|---|-------------|----------|------------|--------|
"""
        for idx, item in enumerate(invoice_data.get('items', []), 1):
            md += f"| {idx} | {item['description']} | {item['quantity']} | {item['unit_price']:,} | {item['total']:,} |\n"
        
        md += f"""
## 💰 Totals
- **Subtotal**: {invoice_data.get('subtotal', 0):,} VND
- **Tax (10%)**: {invoice_data.get('tax_amount', 0):,} VND
- **Discount**: {invoice_data.get('discount', 0):,} VND
- **Total Amount**: {invoice_data['total_amount']:,} VND

## ⚠️ Validation Warnings
"""
        for warning in invoice_data.get('validation_warnings', []):
            md += f"- ⚠️ {warning}\n"
        
        md += f"""
---
**Confidence Score**: {invoice_data.get('confidence', 0):.1%}
"""
        return md
```

**UI Flow:**

```bash
After Mom clicks "Extract Data with AI":

┌──────────────────────────────────────────────────────────────┐
│ MAAS - Review Extracted Data           [X Close]             │
├──────────────────────────────────────────────────────────────┤
│ Split View: PDF ↔️ Extracted Data                            │
├──────────────────────────────────────────────────────────────┤
│ ┌─────────────────┐ │ ┌───────────────────────────────────┐  │
│ │  Original PDF   │ │ │ # Invoice Data Review  [📝 Edit]  │  │
│ │                 │ │ │                                   │  │
│ │  [Invoice Image]│ │ │ ## 📄 Header Information          │  │
│ │                 │ │ │ - **Vendor**: Công ty ABC         │  │
│ │                 │ │ │ - **Tax ID**: 0123456789 ⚠️       │  │
│ │                 │ │ │ - **Invoice #**: INV-001           │ │
│ │                 │ │ │ - **Date**: 2025-12-05            ││
│ │  [Zoom] [Rotate]│ │ │                                   ││
│ │                 │ │ │ ## 🛒 Line Items                  ││
│ │                 │ │ │ | # | Item | Qty | Price | Total ││
│ │                 │ │ │ | 1 | ... | 10 | 100k | 1.0M |   ││
│ │                 │ │ │                                   ││
│ │                 │ │ │ ## 💰 Totals                      ││
│ │                 │ │ │ - **Total**: 1,000,000 VND        ││
│ │                 │ │ │                                   ││
│ │                 │ │ │ ⚠️ Tax ID format unusual           ││
│ │                 │ │ │ ✅ All calculations correct        ││
│ └─────────────────┘ │ └───────────────────────────────────┘│
│                     │                                      │
│ [⬅️ Back]  [📝 Edit Data]  [✅ Looks Good, Submit] ← Next  │
└─────────────────────────────────────────────────────────────┘
```

**Edit Mode (When Mom Clicks "Edit Data"):**

```bash
┌─────────────────────────────────────────────────────────────┐
│ MAAS - Edit Invoice Data               [X Close]           │
├─────────────────────────────────────────────────────────────┤
│ Editable Form View                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Vendor Name: [Công ty ABC                    ]             │
│ Tax ID:      [0123456789    ] ⚠️ Check format              │
│ Invoice #:   [INV-001       ]                              │
│ Date:        [2025-12-05    ] 📅                           │
│                                                             │
│ Line Items:                                [+ Add Row]      │
│ ┌──┬──────────────┬─────┬──────────┬──────────────┬───┐    │
│ │1 │ Description  │ 10  │ 100,000  │ 1,000,000    │ X │    │
│ │2 │ Description  │ 5   │ 200,000  │ 1,000,000    │ X │    │
│ └──┴──────────────┴─────┴──────────┴──────────────┴───┘    │
│                                                             │
│ Subtotal:  [2,000,000] (auto-calculated)                   │
│ Tax (10%): [  200,000] (auto-calculated)                   │
│ Discount:  [        0]                                     │
│ Total:     [2,200,000] VND                                 │
│                                                             │
│ [❌ Cancel]  [👁️ Preview Changes]  [✅ Submit]              │
└─────────────────────────────────────────────────────────────┘
```

**Key Features:**

- ✅ **Side-by-side comparison** - Original PDF vs Extracted data
- ✅ **Markdown format** - Clean, readable, editable
- ✅ **Inline editing** - Click "Edit" to modify any field
- ✅ **Validation warnings** - Highlights potential errors
- ✅ **Auto-calculation** - Recalculates totals as mom edits
- ✅ **Diff highlighting** - Shows what mom changed

#### Data Flow Implementation

```python
# Backend API endpoints
@router.post("/api/invoices/upload")
async def upload_invoice(file: UploadFile):
    """
    Step 1: Upload PDF and generate preview (NO AI)
    Returns preview data immediately
    """
    pdf_path = save_uploaded_file(file)
    preview = PDFPreviewService().generate_preview(pdf_path)
    
    # Store in temporary storage
    temp_invoice = {
        "id": generate_temp_id(),
        "pdf_path": pdf_path,
        "preview": preview,
        "status": "UPLOADED",
        "extracted_data": None  # No extraction yet
    }
    
    return {
        "invoice_id": temp_invoice["id"],
        "preview": preview,
        "next_action": "REVIEW_QUALITY"  # Mom reviews, then clicks "Extract"
    }

@router.post("/api/invoices/{invoice_id}/extract")
async def extract_invoice_data(invoice_id: str):
    """
    Step 2: Extract data using Gemini API (AI STARTS HERE)
    Called when mom clicks "Extract Data with AI"
    """
    invoice = get_temp_invoice(invoice_id)
    
    # Log API call for cost tracking
    logger.info(f"Gemini API call initiated for invoice {invoice_id}")
    
    # Call Gemini API
    extracted_data = await GeminiClient().extract_invoice(invoice.pdf_path)
    
    # Format as markdown for review
    markdown_view = ExtractionReviewService().format_extraction_as_markdown(extracted_data)
    
    # Update temporary storage
    invoice.extracted_data = extracted_data
    invoice.markdown_view = markdown_view
    invoice.status = "EXTRACTED"
    
    return {
        "invoice_id": invoice_id,
        "extracted_data": extracted_data,
        "markdown_view": markdown_view,
        "confidence": extracted_data.get("confidence", 0),
        "validation_warnings": extracted_data.get("validation_warnings", []),
        "next_action": "REVIEW_AND_EDIT"  # Mom reviews/edits, then submits
    }

@router.put("/api/invoices/{invoice_id}/data")
async def update_invoice_data(invoice_id: str, data: dict):
    """
    Step 3: Update data after mom's edits
    Called when mom edits fields
    """
    invoice = get_temp_invoice(invoice_id)
    
    # Track what changed
    changes = detect_changes(invoice.extracted_data, data)
    
    # Log corrections for ML improvement
    log_human_corrections(invoice_id, changes)
    
    # Re-validate
    validation = validate_invoice_data(data)
    
    return {
        "invoice_id": invoice_id,
        "changes": changes,
        "validation": validation,
        "ready_to_submit": validation["is_valid"]
    }

@router.post("/api/invoices/{invoice_id}/submit")
async def submit_invoice(invoice_id: str):
    """
    Step 4: Final submission - Save to database
    Called when mom clicks "Looks Good, Submit"
    """
    invoice = get_temp_invoice(invoice_id)
    
    # Save to database
    db_invoice = save_invoice_to_database(invoice.extracted_data)
    
    # Clean up temporary storage
    delete_temp_invoice(invoice_id)
    
    return {
        "invoice_id": db_invoice.id,
        "status": "READY_FOR_AUTOMATION",
        "next_action": "AUTOMATE_ACSOFT"
    }
```

**Summary:**

1. **Upload PDF** → Preview shown instantly (free, local)
2. **Mom reviews preview** → Decides if quality is good
3. **Mom clicks "Extract Data"** → Gemini API called (costs $$)
4. **Extracted data shown** → Side-by-side with PDF in markdown format
5. **Mom edits if needed** → Changes tracked and validated
6. **Mom clicks "Submit"** → Data saved to database
7. **Ready for automation** → Next step is ACSoft automation

### 2.5 FastAPI Backend

**Purpose:** Orchestrate workflow and expose REST API

**Design Pattern:** MVC + Repository Pattern

**Key Routes:**

- `/api/invoices` - Invoice CRUD operations
- `/api/automation` - Automation control
- `/api/audit` - Audit log queries
- `/api/health` - System health checks

**Middleware:**

- Request logging
- Error handling
- Performance timing
- CORS (local only)

### 2.5 Database Design

**Purpose:** Persist all application data

**Design Pattern:** Repository Pattern

**Key Entities:**

- `Invoice`: Main invoice record
- `InvoiceItem`: Line items
- `Vendor`: Vendor information
- `AutomationRun`: Automation history
- `AuditLog`: System audit trail

**Relationships:**

- Invoice 1:N InvoiceItems
- Invoice N:1 Vendor
- Invoice 1:N AutomationRuns
- All entities → AuditLog

---

## 3. Security Design

### 3.1 Data Security

**At Rest:**

- SQLite database with file permissions (600)
- Encrypted backups
- No sensitive data in logs

**In Transit:**

- HTTPS for Gemini API calls
- Local-only HTTP for web UI (no external access)

**API Keys:**

- Stored in environment variables
- Never in code or logs
- Masked in error messages

### 3.2 Access Control

**Web UI:**

- Accessible only from localhost (127.0.0.1)
- No authentication required (single-user system)

**Database:**

- File-level permissions
- No network access
- Automatic backups with retention policy

---

## 4. Deployment Architecture

### 4.1 Deployment Strategy Overview

**Critical Requirement:** Mom cannot use terminal commands or run Python scripts manually.

**Two-Phase Approach:**

**Phase 1 (MVP - Weeks 1-2):** Progressive Web App (PWA) with VBScript launcher

- ✅ Faster to implement (2-3 days)
- ✅ Proves concept with minimal overhead
- ✅ One-click desktop icon launch
- ❌ Still uses browser (Chrome required)

**Phase 2-3 (Enhancement - Weeks 3-4):** Electron desktop application

- ✅ Native desktop application
- ✅ Professional UX (no browser chrome)
- ✅ Auto-update support
- ✅ System tray integration

### 4.2 Phase 1: PWA Architecture

**Component Flow:**

```bash
Desktop Icon → start_maas.vbs → Python Backend (hidden) → Chrome --app mode
                                      ↓
                                localhost:8765
                                      ↓
                                Vue.js Frontend
```

**Key Components:**

1. **`start_maas.vbs`** - VBScript launcher (double-click to start)
   - Starts Python backend invisibly (no console window)
   - Polls `/health` endpoint until backend ready
   - Opens Chrome in --app mode (fullscreen, no URL bar)
   - Handles "already running" case gracefully

2. **`run.py`** - Modified to hide console window
   - Uses `ctypes` on Windows to hide console
   - Starts FastAPI server on localhost:8765
   - Logs to file only (no stdout to console)

3. **`stop_maas.vbs`** - Clean shutdown script
   - Terminates Python backend process
   - Closes Chrome windows
   - Clean exit

4. **Embedded Python Runtime**
   - Self-contained Python 3.9 installation
   - No system Python required
   - All dependencies pre-installed

**File Structure:**

```bash
C:\MAAS\
├── python\                 # Embedded Python runtime
│   ├── python.exe
│   ├── python39.dll
│   └── Lib\site-packages\
├── app\                    # Application code
├── frontend\               # Vue.js frontend
├── data\                   # User data
├── logs\                   # Application logs
├── start_maas.vbs          # Launcher (double-click this)
├── stop_maas.vbs           # Shutdown script
└── README.txt              # User instructions
```

**Example: start_maas.vbs (simplified)**

```vbscript
' Start backend invisibly
Set objShell = CreateObject("WScript.Shell")
pythonExe = "C:\MAAS\python\python.exe"
backendScript = "C:\MAAS\run.py"
objShell.Run """" & pythonExe & """ """ & backendScript & """", 0, False

' Wait for backend ready (health check polling)
maxRetries = 30
Do While retryCount < maxRetries
    WScript.Sleep 1000
    ' Check http://localhost:8765/health
    ' If status 200, break
Loop

' Open browser in app mode
chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"
objShell.Run """" & chromeExe & """ --app=http://localhost:8765", 1, False
```

**Example: run.py (console hiding)**

```python
import sys

# Hide console window on Windows
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.WinDLL("kernel32")
    hwnd = kernel32.GetConsoleWindow()
    if hwnd:
        user32 = ctypes.WinDLL("user32")
        user32.ShowWindow(hwnd, 0)  # SW_HIDE

# Start FastAPI server
import uvicorn
from app.main import app

uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
```

**Installation Process:**

1. Extract package to C:\MAAS\
2. Run `install.bat` (creates desktop shortcut, optionally adds to startup)
3. Double-click "MAAS" desktop icon to launch

### 4.3 Phase 2-3: Electron Architecture

**Component Flow:**

```bash
MAAS.exe → Electron Main Process → Python Backend (embedded)
                ↓
          Electron Renderer → Vue.js Frontend
```

**Architecture:**

**Main Process (Node.js):**

- Spawns Python backend as child process
- Waits for health check before opening window
- Manages application lifecycle
- Handles system tray integration
- Manages auto-updates

**Renderer Process:**

- Loads Vue.js frontend from localhost:8765
- IPC communication with main process (if needed)
- Native window controls

**Embedded Backend:**

- Python runtime bundled with Electron
- Starts automatically when app launches
- Terminates when app quits

**Example: Electron main.js (simplified)**

```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const axios = require('axios');

let mainWindow;
let backendProcess;

async function startBackend() {
  // Path to embedded Python
  const pythonPath = path.join(process.resourcesPath, 'python', 'python.exe');
  const scriptPath = path.join(process.resourcesPath, 'app', 'run.py');
  
  // Spawn Python backend
  backendProcess = spawn(pythonPath, [scriptPath], {
    windowsHide: true,
    detached: false
  });
  
  // Wait for backend ready
  const maxRetries = 30;
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await axios.get('http://localhost:8765/health');
      if (response.status === 200) {
        return true;
      }
    } catch (error) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  return false;
}

async function createWindow() {
  // Start backend first
  const backendReady = await startBackend();
  if (!backendReady) {
    // Show error dialog
    return;
  }
  
  // Create browser window
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });
  
  // Load frontend
  mainWindow.loadURL('http://localhost:8765');
}

app.whenReady().then(createWindow);

app.on('quit', () => {
  // Kill backend process
  if (backendProcess) {
    backendProcess.kill();
  }
});
```

**Installation Process:**

1. Download MAAS-Setup.exe
2. Run installer (NSIS or Squirrel)
3. Desktop shortcut and Start Menu entry created automatically
4. Double-click to launch

**Advantages Over PWA:**

- Native application (no browser chrome)
- Professional UX
- System tray integration
- Auto-update support
- Better process management

### 4.4 Health Monitoring

**Health Check Endpoint:**

```python
# app/api/routes/health.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """Backend health check for launcher scripts"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
```

**Health Check Strategy:**

- Launcher scripts poll `/health` endpoint
- 1 second intervals
- 30 second timeout
- HTTP 200 = backend ready
- Any error = retry or fail

### 4.5 Process Management

**Startup Flow:**

1. User double-clicks desktop icon
2. Launcher checks if backend already running (port 8765)
3. If running → just open browser/window
4. If not running → start backend invisibly
5. Poll health endpoint (max 30 seconds)
6. When healthy → open UI
7. If timeout → show error message with log location

**Shutdown Flow:**

1. User closes UI window
2. Backend continues running (allows reopen)
3. To fully stop: Run stop script or kill process
4. Clean termination of all child processes

**Error Handling:**

- Port already in use → detect and notify user
- Backend fails to start → show error with log path
- Backend crashes → system tray notification (Phase 2-3)
- Health check timeout → user-friendly error message

### 4.6 Deployment Package Structure

**Phase 1 (PWA):**

```bash
MAAS_v1.0.zip
├── python/               # Embedded Python runtime (50-100 MB)
├── app/                  # Application code
├── frontend/             # Vue.js build
├── data/                 # Empty directories (created on install)
├── logs/
├── config.yaml
├── run.py
├── start_maas.vbs
├── stop_maas.vbs
├── install.bat           # Windows installer script
└── README.txt            # User instructions
```

**Phase 2-3 (Electron):**

```bash
MAAS-Setup.exe            # NSIS installer (100-150 MB)
└── (Contains all files bundled inside installer)
```

**Installation Script (install.bat):**

```batch
@echo off
REM Copy files to C:\MAAS\
xcopy /E /I python C:\MAAS\python
xcopy /E /I app C:\MAAS\app
REM ... copy other files ...

REM Create desktop shortcut
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MAAS.lnk'); $Shortcut.TargetPath = 'C:\MAAS\start_maas.vbs'; $Shortcut.Save()"

REM Optional: Add to Windows startup
REM Copy shortcut to %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\

echo Installation complete!
pause
```

---

## 5. Error Handling Design

### 5.1 Error Categories

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| **Validation** | Missing fields, invalid formats | User correction required |
| **Extraction** | Gemini API failures, low confidence | Retry or manual entry |
| **Automation** | Element not found, ACSoft crashed | Pause and notify user |
| **System** | Disk full, database locked | Alert and halt operations |

### 4.2 Error Recovery Flow

```bash
Error Occurs → Classify Error → 
Check if Retryable → 
  Yes → Retry with backoff → Log attempt
  No → Log error → Notify user → 
    Provide recovery options → User decides
```

---

## 5. Performance Design

### 5.1 Performance Goals

| Operation | Target | Strategy |
|-----------|--------|----------|
| PDF extraction | < 5s per page | Async processing, image optimization |
| Validation | < 1s | In-memory processing, caching rules |
| Automation | < 30s per invoice | Optimized element locators |
| End-to-end | < 2 min per invoice | Pipeline optimization |

### 5.2 Optimization Strategies

**Database:**

- Indexes on frequently queried fields
- WAL mode for better concurrency
- Regular VACUUM operations

**API Calls:**

- Connection pooling for Gemini API
- Response caching where appropriate
- Batch processing for multiple invoices

**UI:**

- Lazy loading of invoice lists
- Progressive image loading
- Client-side caching

---

## 6. Scalability Design

### 6.1 Current Scope (Phase 1-3)

**Design for:**

- Single user (Mom)
- Sequential processing (1 invoice at a time)
- Local deployment only
- 50-100 invoices per day

### 6.2 Future Scalability (Post-MVP)

**Potential Enhancements:**

- Multi-user support with authentication
- Queue-based processing (Redis/RabbitMQ)
- Concurrent invoice processing
- Cloud deployment option
- Multi-language support

**Design Decisions for Future:**

- Use dependency injection
- Abstract database layer
- Separate configuration from code
- Stateless API design

---

## 7. Monitoring & Observability Design

### 7.1 Logging Strategy

**Log Levels:**

- `DEBUG`: Development only
- `INFO`: Normal operations
- `WARNING`: Recoverable issues
- `ERROR`: Operation failures
- `CRITICAL`: System failures

**Log Structure:**

```json
{
  "timestamp": "2025-12-05T10:30:00Z",
  "level": "INFO",
  "component": "pdf_processor",
  "action": "extract_invoice",
  "invoice_id": "INV-001",
  "duration_ms": 1234,
  "status": "success"
}
```

### 7.2 Metrics Collection

**Key Metrics:**

- Processing time per invoice
- Extraction confidence scores
- Validation error rates
- Automation success rates
- API costs (Gemini)
- System resource usage

### 7.3 Audit Trail

**Captured Events:**

- All invoice operations (upload, extract, validate, automate, complete)
- User actions (corrections, approvals)
- System errors and recoveries
- Configuration changes

---

## 8. Testing Design

### 8.1 Test Strategy

**Unit Tests:**

- All business logic functions
- Data transformations
- Validation rules
- Error handling

**Integration Tests:**

- API endpoint workflows
- Database operations
- Gemini API integration (mocked)

**End-to-End Tests:**

- Complete invoice processing
- Error recovery scenarios
- ACSoft automation (manual)

**Test Data:**

- Diverse invoice samples
- Edge cases and error scenarios
- Anonymized real data

### 8.2 Test Coverage Goals

- Unit test coverage: 80%+
- Integration test coverage: 70%+
- Critical path coverage: 100%

---

## 9. Deployment Design

### 9.1 Deployment Architecture

**Environment:**

- Mom's Windows 10/11 computer
- Local installation (no cloud)
- Automatic startup on boot

**Components:**

- Python virtual environment
- SQLite database file
- Configuration files
- Log files
- Backup directory

### 9.2 Deployment Process

```bash
1. Install Python 3.9+
2. Clone repository
3. Create virtual environment
4. Install dependencies
5. Configure .env file
6. Initialize database
7. Run tests
8. Start application
9. Set up Task Scheduler
10. Configure daily backups
```

---

## 10. Maintenance Design

### 10.1 Regular Maintenance

**Daily:**

- Automated database backup
- Log rotation
- Disk space check

**Weekly:**

- Review error logs
- Check API costs
- Verify backup integrity

**Monthly:**

- Database optimization (VACUUM)
- Archive old invoices
- Update dependencies

### 10.2 Update Strategy

**Minor Updates:**

- Deploy during off-hours
- Automatic database migration
- Rollback capability

**Major Updates:**

- User notification
- Full backup before update
- Staged rollout
- User acceptance testing

---

## Appendix A: Design Decisions

### A.1 Technology Choices

**FastAPI vs Flask:**

- Chose FastAPI for automatic API docs and type checking

**SQLite vs PostgreSQL:**

- SQLite for zero-maintenance and local deployment

**PyWinAuto vs Selenium:**

- PyWinAuto for native Windows UI automation

**Gemini vs Other OCR:**

- Gemini for superior Vietnamese support and cost

### A.2 Trade-offs

| Decision | Pro | Con | Rationale |
|----------|-----|-----|-----------|
| Local-only deployment | Privacy, no hosting costs | No remote access | Privacy is critical |
| Sequential processing | Simple, reliable | Slower for bulk | Current volume acceptable |
| No authentication | Simple for single user | Not multi-user ready | Single user system |
| Manual save required | Maximum safety | Extra user step | Safety over convenience |

---

**Document Maintenance:**

- Update when architecture changes
- Review before each phase
- Keep synchronized with TECHNICAL_SPECS.md

**Last Updated:** December 5, 2025  
**Next Review:** After Phase 1 completion
