# Planned Changes

Use this file to layout upcoming changes, ideas, and architecture adjustments before implementation.

## Phase 1 Analysis: Upload and Extract PDF Invoice

### Documentation Status (`docs/IMPLEMENTATION_STATUS.md`)

- **Status:** Functional (95% complete for Gemini, 85% for API/UI).
- **Flow:** Upload -> Extract -> Validate.
- **Key Components:**
  - `gemini_client.py`: Gemini 2.0 Flash integration, Retry logic, Cost tracking.
  - `pdf_processor.py`: "pdf2image integration".
  - `endpoints.py`: Async background processing.

### Codebase Reality

- **Status:** Implemented and Functional.
- **Flow:** `POST /api/invoices/upload` -> Save file -> default DB entry -> `POST /process` -> Background Task.
- **Key Components:**
  - `gemini_client.py`: **Matches docs**. Uses `gemini-2.0-flash-exp`, includes exponential backoff, JSON schema validation, and hardcoded 0.0 cost (as expected for preview).
  - `pdf_processor.py`: **Discrepancy**. Code uses `PyMuPDF (fitz)` instead of `pdf2image`. This is an improvement (faster, no poppler dependency), but docs are stale.
  - `endpoints.py`: **Matches docs**. Orchestrates the pipeline correctly. Logic to map JSON response to DB columns is direct and assumes schema compliance.

### Summary

The "Upload and Extract" feature is technically solid and implemented. The main discrepancy is the underlying PDF library (PyMuPDF vs pdf2image), where the code is actually using a more robust solution than documented. The flow is ready for testing with real API keys.

## Detailed Workflow Analysis: Phase 1 (Upload & Extract)

The "Upload and Extract" phase is the foundation of the MAAS system. It handles the ingestion of PDF documents, their conversion to machine-readable format, data extraction via AI, and initial validation.

Here is the step-by-step logical flow as implemented in the codebase:

### 1. Ingestion (Trigger: User Upload)

- **User Action:** User drags and drops a PDF file onto the UI or selects it via the file picker.

- **API Endpoint:** `POST /api/invoices/upload` (`app/api/endpoints.py`) receives the file.
- **Process:**
    1. **Validation:** Checks if the file extension is `.pdf`.
    2. **Storage:** Generates a unique UUID for the invoice and saves the file to `data/uploads/{uuid}_{filename}`.
    3. **Database Record:** Inserts a new row into the `invoices` table with status `PENDING` and minimal metadata (filename, path).
    4. **Response:** Returns the `invoice_id` and initial data to the frontend.

### 2. Processing Trigger

- **User Action:** User clicks "Process" (or potentially auto-triggered by UI settings).

- **API Endpoint:** `POST /api/invoices/{id}/process` (`app/api/endpoints.py`).
- **Process:**
    1. **Verification:** Checks if invoice ID exists in DB.
    2. **Task Queue:** Adds a `background_extraction` task to FastAPI's `BackgroundTasks` queue.
    3. **Response:** Returns immediate "Processing started" message to keep UI responsive.

### 3. Background Extraction Pipeline

This runs asynchronously so the UI doesn't freeze.

- **Function:** `background_extraction(invoice_id, pdf_path)` in `app/api/endpoints.py`.
- **Step A: PDF Conversion** (`app/services/pdf_processor.py`)
  - Uses `PyMuPDF (fitz)` to open the PDF.
  - Renders each page as a high-resolution PNG image (Zoom factor 2.0x for better OCR clarity).
  - Returns a list of `PIL.Image` objects (in-memory).
- **Step B: AI Extraction** (`app/services/gemini_client.py`)
  - Constructs a prompt specifically for Vietnamese invoices (handling common tax rates, date formats).
  - Calls Google's **Gemini 2.0 Flash Experimental** API.
  - **Retry Logic:** If the API fails (timeout/network), it retries up to 3 times with exponential backoff.
  - **Structure Enforcement:** Uses JSON Schema to force Gemini to return data in the exact format we need (Vendor, Invoice Number, Date, Items array, etc.).
  - **Cost Tracking:** Metadata about processing time and token usage is captured (currently $0.00 for preview model).
- **Step C: Data Persistence**
  - The backend receives the raw JSON from Gemini.
  - **Idempotency:** Deletes any existing line items for this invoice ID (clearing previous runs).
  - **Updates:** atomic updates to the `invoices` table with extracted header data (Total, Tax, Vendor).
  - **Insertions:** Inserts detailed line items into `invoice_items` table.
  - **Status Update:** Sets invoice status to `extracted`.

### 4. Validation & auto-correction

- **Function:** `run_validation(invoice_id)` (called immediately after extraction).

- **Logic (`app/services/validator.py`):**
  - **Required Fields:** Checks for missing Vendor Name, Date, or Total.
  - **Date Normalization:** specific logic to handle Vietnamese date formats (DD/MM/YYYY) and convert to ISO (YYYY-MM-DD).
  - **Math Check:** Verification loop:
    - `Quantity * Unit Price == Line Total`? (Reflags mismatches).
    - `Sum(Line Totals) == Subtotal`?
    - `Subtotal + Tax == Grand Total`?
  - **Tax Logic:** Checks if tax rate lines up with standard VN rates (0%, 5%, 8%, 10%).
- **Outcome:**
  - If no errors: Status -> `validated`.
  - If errors found: Status -> `needs_review`.
  - Warnings are stored but don't block the "valid" status (e.g., "Tax calculated vs scanned differs by 1 dong").

### 5. UI Application

- The Frontend polls `GET /api/invoices` or receives updates via WebSocket (if implemented) to show the new status.

- User sees the extracted data side-by-side with the PDF for final manual review.

## Q&A: Addressing Phase 1 Capabilities

### 1. Upload Limits & Batch Processing

- **Question:** How many uploads can Mom make? Can she upload mixed types (selling/buying)?
- **Answer:**
  - **Limits:** The current API accepts one file at a time (`POST /invoices/upload`). The Web UI, however, allows Drag & Drop of one file. *Currently, there is no batch upload endpoint implemented.*
  - **Mixed Types:** Yes, Gemini is context-aware. The prompt `"Extract all data from this Vietnamese invoice"` is generic enough to handle both "Hóa đơn giá trị gia tăng" (VAT Invoice - usually buying) and "Hóa đơn bán hàng" (Sales Invoice).
  - **Sorting:** The system does *not* currently categorize them as "Selling" vs "Buying" explicitly in the database. It just extracts `vendor_name`. If the vendor is Mom's company, it's a selling invoice; otherwise, it's a buying invoice. *We should add a logic rule or AI prompt update to explicitly tag this.*

### 2. Validation of Multiple Invoices

- **Question:** If Mom uploads >1 invoice, how does she validate?
- **Current Flow:**
  - Validation is per-invoice.
  - Mom uploads Invoice A -> System extracts -> Mom reviews A.
  - Mom uploads Invoice B -> System extracts -> Mom reviews B.
  - **Gap:** There is no "Bulk Validate" button. She must click into each invoice from the Dashboard list to review errors.

### 3. Duplicate Handling

- **Question:** What if Mom uploads the same invoice twice?
- **Answer:** The system handles this robustly!
  - **Mechanism:** `app/models/schema.sql` defines a `unique` constraint on `(vendor_id, invoice_number, invoice_date)`.
  - **File Hash:** There is also a `pdf_hash` column.
  - **Behavior:** If she uploads the *exact same PDF*, the backend might accept it initally but extraction would fail on DB insert due to the Unique Constraint, OR we need to verify if the upload endpoint checks strict duplicates before saving.
  - *Correction verify:* The `upload_invoice` endpoint currently does NOT check `pdf_hash` before safe. It blindly inserts. This is a potential improvement area.

### 4. PDF to Image Conversion

- **Question:** Does the tool convert PDF to image for Gemini?
- **Answer:** **Yes.** `app/api/endpoints.py` calls `pdf_processor.convert_to_images(pdf_path)`. This uses `PyMuPDF` to render high-res PNGs of each page. These images are then sent to Gemini Vision API. This avoids parsing raw PDF text, which is often messy in Vietnamese invoices (font issues).

## Proposed Improvements for Change Plan

1. **Add "Invoice Type" field:** Update DB schema and Gemini prompt to detect "Buying" (Mua vào) vs "Selling" (Bán ra).
2. **Batch Upload:** Add UI/API support for uploading multiple files at once.
3. **Duplicate Check on Upload:** Compute SHA256 of PDF on upload and reject immediate duplicates before even saving to disk.

## Cross-Platform Development Strategy (Linux Dev -> Windows Target)

Since development occurs on Linux but deployment is on Windows, we must strictly decouple OS-dependent logic.

### 1. File Paths

- **Rule:** ALWAYS use `pathlib.Path`. Never string concatenation (`/` vs `\`).

- **Handling:** `pathlib` automatically handles the OS separator.

### 2. PyWinAuto Isolation

- `pywinauto` is Windows-only. It will crash or fail to install on Linux.

- **Strategy:**
  - Wrap imports in `try/except ImportError`.
  - Create a **MockAutomationService** that runs on Linux. It logs actions ("Clicked Import") instead of performing them.
  - This allows full end-to-end testing of the *logic* (Upload -> Extract -> Excel Gen) on Linux.

### 3. Excel Generation Compatibility

- **Library:** `pandas` with `openpyxl` (modern .xlsx) or `xlwt` (legacy .xls).

- **Target:** ACSoft likely uses older libraries. We must test if it requires `.xls` (binary Excel 97-2003) or `.xlsx`. *Assumption for now: .xlsx (standard), but ready to switch specific engine if needed.*

### 4. Dependency Management

- Keep `requirements.txt` generic.

- Move `pywinauto` to a `requirements-windows.txt` or handle failure gracefully in code.

---

## Phase 2 Plan: Excel-Based Automation & Comparison

Based on the limitations of Direct GUI Automation and the samples provided, we are pivoting to an "Excel Intermediate" strategy.

### 1. Invoice Type Logic

We will differentiate "Buying" vs "Selling" invoices automatically.

- **Logic:**
  - Target Entity: "CÔNG TY TNHH MỘT THÀNH VIÊN 933" (Mom's 933 Company).
  - **Selling Invoice:** `seller_name` == "933 Company".
  - **Buying Invoice:** `buyer_name` == "933 Company".
- **Action:** Add `invoice_type` column (ENUM: `IN` | `OUT`) to the database.

### 2. The Excel "Bridge" Strategy

Instead of typing into ACSoft, we will generate files ACSoft can import.

- **Step A: Map Vendor Codes**
  - ACSoft requires specific `MaDoiTuong` (Vendor Codes) (e.g., "VUHONGMINH" not "CÔNG TY TNHH VŨ HỒNG MINH").
  - **New Feature:** "Vendor Mapping" in Web UI.
  - When an invoice is validated, if the Vendor Name is new, ask Mom: *"Select existing ACSoft code for this vendor"* (autocomplete list manageable in settings).
- **Step B: Generate Excel**
- - Create two templates based on ACSoft requirements (user must provide sample excel export from ACSoft for us to reverse engineer).

  - `template_sales.xls`
  - `template_purchase.xls`
- **Step C: Automation**
  - PyWinAuto script becomes simple:
-       1. Open ACSoft.

        2. Click `Import Excel` (Purchase or Sales module based on type).
        3. Select the generated file.
        4. Click `Confirm`.

-## 3. Benefits of Pivot

- **Safety:** Mom can inspect the generated Excel file before "Automation" runs.

- **Reliability:** Excel import is atomic (all or nothing) and faster than typing.
- **Maintenance:** Easier to update an Excel template than 50 GUI click coordinates.

## Comparative Analysis: Original Plan vs. New Excel Strategy

### 1. Complexity

- **Original:** **High.** Required mapping dynamic extracted data to ~50 active GUI elements (text boxes, dropdowns, grids) in real-time. Handling UI lag, popups, and focus stealing was a constant risk.

- **New:** **Medium.** Shifts complexity from "Runtime GUI Manipulation" to "Data Transformation." We just need to map our DB schema to ACSoft's Excel schema once. The actual automation is just 3 clicks.

### 2. Robustness

- **Original:** **Fragile.** If ACSoft updates, changes resolution, or if Mom moves the mouse, the script crashes.

- **New:** **Robust.** Excel import is a standard feature. As long as the file format is correct, it works.

### 3. Trust & Safety (Crucial for Mom)

- **Original:** "Ghost in the machine." Mom watches fields fill in magically. If it makes a mistake, she panics. She can't "undo" easily without deleting the invoice in ACSoft manually.

- **New:** "Reviewable Artifact." The system produces a file. Mom can open it, double-check sums, and essentially "approve" the data before it ever touches her accounting software.

### 4. Implementation Speed

- **Original:** Slow. Requires writing PyWinAuto scripts for every single field and testing on the specific target Windows machine.

- **New:** Fast. We can build the Excel generator entirely on Linux/Dev environment. We only need to write a tiny PyWinAuto script to click "Import".

### Verdict

The **Excel Strategy** is superior in every metric that matters for this project: **Stability, Trust, and Ease of Review.** The only new requirement is obtaining the "standard import template" from ACSoft.
