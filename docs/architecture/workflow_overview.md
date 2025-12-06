---
title: MAAS Complete Workflow Overview
description: End-to-end workflow design from user perspective
last_updated: 2025-12-05
version: 1.0
status: Design Phase - Ready for Implementation
---

# MAAS Complete Workflow Overview

**Document Purpose:** Visual and narrative description of complete system workflow  
**Audience:** Developers, stakeholders, mom (user)  
**Phase:** Design (Pre-Implementation)

---

## Table of Contents

1. [User Journey Overview](#user-journey-overview)
2. [Detailed Workflow Stages](#detailed-workflow-stages)
3. [System Architecture Flow](#system-architecture-flow)
4. [Error Handling Flows](#error-handling-flows)
5. [Alternative Scenarios](#alternative-scenarios)

---

## User Journey Overview

### High-Level User Experience (Mom's Perspective)

```bash
┌─────────────────────────────────────────────────────────────────┐
│                     MOM'S DAILY WORKFLOW                        │
└─────────────────────────────────────────────────────────────────┘

MORNING: Mom arrives at office with 50-100 paper invoices

┌──────────────┐
│ 1. SCAN      │  Mom scans invoices → PDF files saved to folder
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 2. LAUNCH    │  Double-click MAAS desktop icon → App opens
└──────┬───────┘  (No terminal, no commands, just like any Windows app)
       │
       ↓
┌──────────────┐
│ 3. UPLOAD    │  Drag PDF into MAAS window
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 4. PREVIEW   │  See PDF preview instantly (< 1 sec)
└──────┬───────┘  Check if scan is readable
       │
       ↓
┌──────────────┐
│ 5. EXTRACT   │  Click "Extract Data" → AI processes (2-8 sec)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 6. REVIEW    │  See extracted data side-by-side with PDF
└──────┬───────┘  Compare numbers, vendor name, dates
       │
       ↓
┌──────────────┐
│ 7. EDIT      │  Fix any errors (click "Edit" if needed)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 8. SUBMIT    │  Click "Looks Good, Submit"
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 9. AUTOMATE  │  Click "Fill ACSoft Form" → Automation runs
└──────┬───────┘  Watch as system fills form (30-60 sec)
       │
       ↓
┌──────────────┐
│ 10. VERIFY   │  System pauses → Mom reviews filled form in ACSoft
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 11. SAVE     │  Mom manually saves in ACSoft (safety!)
└──────┬───────┘
       │
       ↓
┌──────────────┐
│ 12. NEXT     │  Process next invoice → Repeat steps 3-11
└──────────────┘

RESULT: 50-100 invoices processed in 1-2 hours (vs 4-6 hours manually)
```

---

## Detailed Workflow Stages

### Stage 1: Application Launch

**User Action:** Double-click MAAS desktop icon

**What Happens Behind the Scenes:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: LAUNCH (PHASE 1 - PWA APPROACH)                       │
└─────────────────────────────────────────────────────────────────┘

Desktop Icon (MAAS.lnk)
  ↓ (runs)
start_maas.vbs
  ↓
  ├─→ Check if backend already running (port 8765)
  │   └─→ If yes: Just open browser window → DONE
  │
  ├─→ If no: Start Python backend (hidden window)
  │   └─→ python.exe run.py (NO VISIBLE CONSOLE)
  │
  ├─→ Poll health endpoint: http://localhost:8765/health
  │   └─→ Wait max 30 seconds (retry every 1 second)
  │
  └─→ When backend healthy:
      └─→ Open Chrome in app mode (--app flag)
          └─→ URL: http://localhost:8765
          └─→ Result: Fullscreen browser, no URL bar, looks native

USER SEES: Application window opens in 3-5 seconds
           (Same experience as opening Microsoft Word)
```

**Phase 2-3 Electron Version:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 1: LAUNCH (PHASE 2-3 - ELECTRON APPROACH)                │
└─────────────────────────────────────────────────────────────────┘

MAAS.exe
  ↓
Electron Main Process
  ↓
  ├─→ Spawn Python backend as child process
  │   └─→ Embedded Python (no system Python needed)
  │
  ├─→ Poll health endpoint
  │   └─→ Wait for backend ready
  │
  └─→ Create application window
      └─→ Load Vue.js UI from localhost:8765
      └─→ Native window controls, system tray icon

USER SEES: Native desktop application opens
           (Indistinguishable from Microsoft software)
```

---

### Stage 2: PDF Upload & Preview

**User Action:** Drag PDF file into app window OR click "Upload Invoice"

**System Behavior:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 2: UPLOAD & PREVIEW (NO AI YET - FREE & FAST)            │
└─────────────────────────────────────────────────────────────────┘

Frontend: File selected
  ↓
  POST /api/invoices/upload
  ↓
Backend: Receive PDF file
  ↓
  ├─→ Save to data/invoices/{timestamp}_{filename}.pdf
  │
  ├─→ Generate Preview (NO GEMINI API - Uses local libraries)
  │   └─→ PDFConverter (PyMuPDF or pdfplumber)
  │       ├─→ Convert pages to images (150 DPI thumbnails)
  │       ├─→ Extract basic text (simple OCR, not AI)
  │       └─→ Return preview data
  │
  └─→ Return response to frontend
      └─→ {
            invoice_id: "temp_123",
            preview: {
              pages: [
                {page: 1, thumbnail: "base64...", text: "..."},
                {page: 2, thumbnail: "base64...", text: "..."}
              ],
              page_count: 2,
              file_size: "1.2 MB"
            },
            status: "UPLOADED",
            next_action: "REVIEW_QUALITY"
          }

Frontend: Display preview
  ↓
┌──────────────────────────────────────────────────────────┐
│ MAAS - PDF Preview                                       │
├──────────────────────────────────────────────────────────┤
│ ┌──────────────┐  ┌────────────────────────────────┐     │
│ │ PDF Preview  │  │ Raw Text (Basic OCR)           │     │
│ │              │  │                                │     │
│ │ [Thumbnail]  │  │ Công ty TNHH ABC               │     │
│ │              │  │ Địa chỉ: 123 Main St           │     │
│ │ Page 1 of 2  │  │ Mã số thuế: 0123456789         │     │
│ │              │  │                                │     │
│ │ [< ] [ >]    │  │ HÓA ĐƠN BÁN HÀNG               │     │
│ │              │  │ Số: INV-001                    │     │
│ │              │  │ Ngày: 05/12/2025               │     │
│ └──────────────┘  └────────────────────────────────┘     │
│                                                          │
│ Quality Check:                                           │
│ ✅ Text is readable                                      │
│ ✅ Image is clear                                        │
│ ⚠️  Slightly rotated (still usable)                      │
│                                                          │
│ [❌ Cancel]  [🔄 Re-scan]  [✅ Extract Data with AI]     │
└──────────────────────────────────────────────────────────┘

MOM DECIDES:
  → If quality good: Click "Extract Data with AI" → Stage 3
  → If quality bad: Click "Re-scan" → Rescan paper invoice
  → If wrong file: Click "Cancel" → Start over

KEY INSIGHT: No money spent until mom approves quality!
```

**Timing:** < 1 second for preview to appear  
**Cost:** $0 (uses free local libraries)  
**Purpose:** Prevent wasted API calls on bad scans

---

### Stage 3: AI Extraction

**User Action:** Click "Extract Data with AI" button

**System Behavior:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 3: AI EXTRACTION (GEMINI API CALLED - COSTS $$)           │
└─────────────────────────────────────────────────────────────────┘

Frontend: "Extract Data" button clicked
  ↓
  POST /api/invoices/{invoice_id}/extract
  ↓
Backend: Extraction request received
  ↓
  ├─→ Log API call (for cost tracking)
  │   └─→ "Gemini API call initiated for invoice_123"
  │
  ├─→ Load PDF from data/invoices/
  │
  ├─→ Call GeminiClient.extract_invoice(pdf_path)
  │   ↓
  │   GeminiClient:
  │   ├─→ Convert PDF pages to images (higher DPI for AI)
  │   ├─→ Encode images as base64
  │   ├─→ Build prompt with Vietnamese instructions
  │   │   └─→ "Extract invoice data from Vietnamese PDF..."
  │   │       "Handle multi-page invoices..."
  │   │       "Return structured JSON..."
  │   │
  │   ├─→ Call Gemini API (gemini-2.0-flash-exp)
  │   │   └─→ POST to https://generativelanguage.googleapis.com
  │   │       └─→ Wait for response (2-8 seconds)
  │   │
  │   ├─→ Parse JSON response
  │   │   └─→ Extract: vendor, invoice_number, date, items, totals
  │   │
  │   └─→ Calculate confidence score
  │       └─→ Based on: field completeness, format validity, Gemini confidence
  │
  ├─→ Run Validation Service
  │   ├─→ Structure Validator (required fields present?)
  │   ├─→ Format Validator (dates valid? numbers valid?)
  │   ├─→ Business Rules Validator (tax rate = 10%?)
  │   ├─→ Calculation Validator (subtotal + tax = total?)
  │   └─→ Duplicate Detector (invoice already processed?)
  │
  ├─→ Format as Markdown (for display)
  │   └─→ ExtractionReviewService.format_as_markdown(data)
  │       └─→ Creates clean, readable markdown format
  │
  └─→ Return response
      └─→ {
            invoice_id: "temp_123",
            extracted_data: { vendor: "...", items: [...], ... },
            markdown_view: "# Invoice Data\n## Header\n...",
            confidence: 0.92,
            validation: {
              is_valid: true,
              errors: [],
              warnings: ["Tax ID format unusual"]
            },
            next_action: "REVIEW_AND_EDIT"
          }

Frontend: Display extraction results
  ↓
┌──────────────────────────────────────────────────────────┐
│ MAAS - Review Extracted Data                             │
├──────────────────────────────────────────────────────────┤
│ Split View: Original PDF ↔️ Extracted Data               │
├──────────────────────────────────────────────────────────┤
│ ┌──────────────┐ │ ┌────────────────────────────────┐    │
│ │ Original PDF │ │ │ # Invoice Data Review          │    │
│ │              │ │ │                                │    │
│ │ [Full PDF]   │ │ │ ## 📄 Header Information       │    │
│ │              │ │ │ - **Vendor**: Công ty ABC      │    │
│ │ [Zoom]       │ │ │ - **Tax ID**: 0123456789 ⚠️    │    │
│ │ [Rotate]     │ │ │ - **Invoice #**: INV-001       │    │
│ │              │ │ │ - **Date**: 2025-12-05         │    │
│ │              │ │ │                                │    │
│ │              │ │ │ ## 🛒 Line Items               │    │
│ │              │ │ │ | # | Item | Qty | Price | $  │     │
│ │              │ │ │ |---|------|-----|-------|----│     │
│ │              │ │ │ | 1 | Prod | 10  | 100k  | 1M │     │
│ │              │ │ │ | 2 | Serv | 5   | 200k  | 1M │     │
│ │              │ │ │                                │    │
│ │              │ │ │ ## 💰 Totals                   │    │
│ │              │ │ │ - Subtotal: 2,000,000 VND      │    │
│ │              │ │ │ - Tax (10%): 200,000 VND       │    │
│ │              │ │ │ - Total: 2,200,000 VND ✅      │    │
│ │              │ │ │                                │    │
│ │              │ │ │ ⚠️ Tax ID format unusual       │    │
│ │              │ │ │ ✅ All calculations correct    │    │
│ │              │ │ │                                │    │
│ │              │ │ │ Confidence: 92% 🟢             │    │
│ └──────────────┘ │ └────────────────────────────────┘    │
│                  │                                       │
│ [⬅️ Back]  [📝 Edit Data]  [✅ Looks Good, Submit]       │
└──────────────────────────────────────────────────────────┘

MOM'S OPTIONS:
  → Data looks perfect: Click "Looks Good, Submit" → Stage 5
  → Found errors: Click "Edit Data" → Stage 4
  → Major errors: Click "Back" → Re-scan invoice
```

**Timing:** 2-8 seconds (depends on PDF size)  
**Cost:** ~$0.01-0.05 per invoice (Gemini API)  
**Confidence:** System shows 0-100% confidence score

---

### Stage 4: Human Review & Editing (If Needed)

**User Action:** Click "Edit Data" button (if corrections needed)

**System Behavior:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 4: HUMAN CORRECTION (OPTIONAL)                            │
└─────────────────────────────────────────────────────────────────┘

Frontend: Switch to edit mode
  ↓
┌──────────────────────────────────────────────────────────┐
│ MAAS - Edit Invoice Data                                 │
├──────────────────────────────────────────────────────────┤
│ Editable Form View                                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 📄 Header                                                │
│ Vendor Name: [Công ty ABC                    ] 📋 Copy   │
│ Tax ID:      [0123456789    ] ⚠️ Unusual format          │
│              └─→ Mom clicks, changes to "0123-456-789"  │
│ Invoice #:   [INV-001       ]                            │
│ Date:        [2025-12-05    ] 📅                         │
│ Due Date:    [2025-12-20    ]                            │
│                                                          │
│ 🛒 Line Items                          [+ Add Row]      │
│ ┌──┬──────────────┬─────┬──────────┬──────────┬───┐    │
│ │# │ Description  │ Qty │ Price    │ Amount   │ X │    │
│ ├──┼──────────────┼─────┼──────────┼──────────┼───┤    │
│ │1 │Product A     │ 10  │ 100,000  │1,000,000 │ X │    │
│ │  │              │     │          │          │   │    │
│ │2 │Service B     │ 5   │ 200,000  │1,000,000 │ X │    │
│ │  │ └─→ Mom clicks, changes Qty from 5 to 6    │ │    │
│ │  │     System auto-recalculates amount        │ │    │
│ │  │     1,200,000 (updated!)                   │ │    │
│ └──┴──────────────┴─────┴──────────┴──────────┴───┘    │
│                                                          │
│ 💰 Totals (Auto-calculated)                             │
│ Subtotal:  [2,200,000] VND  (updated!)                  │
│ Tax (10%): [  220,000] VND  (auto-calculated)           │
│ Discount:  [        0] VND                              │
│ Total:     [2,420,000] VND  (updated!)                  │
│                                                          │
│ Changes Made: 2 fields edited ⚠️                         │
│ - Tax ID format corrected                               │
│ - Line item 2 quantity: 5 → 6                           │
│                                                          │
│ [❌ Cancel]  [👁️ Preview Changes]  [✅ Submit]          │
└──────────────────────────────────────────────────────────┘

When mom edits:
  ↓
  PUT /api/invoices/{invoice_id}/data
  ↓
Backend:
  ├─→ Track changes (original vs edited)
  │   └─→ Log for ML improvement: "Human corrected Tax ID format"
  │
  ├─→ Re-run validation on edited data
  │   └─→ Ensure edits didn't break anything
  │
  ├─→ Auto-recalculate totals
  │   └─→ If line items change, update subtotal/tax/total
  │
  └─→ Return updated validation status

Frontend: Show real-time validation
  └─→ ✅ green checkmarks for valid fields
      ⚠️ yellow warnings for suspicious values
      ❌ red X for invalid/required fields

When mom clicks "Submit":
  → Go to Stage 5
```

**Key Features:**

- ✅ **Real-time validation** - As mom types
- ✅ **Auto-calculation** - Totals update automatically
- ✅ **Change tracking** - System logs what was corrected
- ✅ **Copy buttons** - Easy to copy/paste if needed
- ✅ **Undo available** - Can revert changes

---

### Stage 5: Data Submission & Storage

**User Action:** Click "Looks Good, Submit" or "Submit" (after editing)

**System Behavior:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 5: SUBMISSION & STORAGE                                  │
└─────────────────────────────────────────────────────────────────┘

Frontend: "Submit" clicked
  ↓
  POST /api/invoices/{invoice_id}/submit
  ↓
Backend: Final submission
  ↓
  ├─→ Run final validation
  │   └─→ Ensure all required fields present and valid
  │
  ├─→ Save to SQLite database
  │   ├─→ Table: invoices (header data)
  │   ├─→ Table: invoice_items (line items)
  │   ├─→ Table: audit_log (track submission)
  │   └─→ Generate permanent invoice_id: "INV-2025-001"
  │
  ├─→ Update invoice status
  │   └─→ UPLOADED → EXTRACTED → VALIDATED → READY_FOR_AUTOMATION
  │
  ├─→ If mom made corrections:
  │   └─→ Log corrections to audit trail
  │       └─→ "User corrected 2 fields: tax_id, line_item_2_quantity"
  │
  ├─→ Move PDF from temp to permanent storage
  │   └─→ data/invoices/2025/12/INV-2025-001.pdf
  │
  └─→ Return success response
      └─→ {
            invoice_id: "INV-2025-001",
            status: "READY_FOR_AUTOMATION",
            next_action: "AUTOMATE_ACSOFT",
            summary: {
              vendor: "Công ty ABC",
              total: "2,200,000 VND",
              items_count: 2
            }
          }

Frontend: Show success + next step
  ↓
┌──────────────────────────────────────────────────────────┐
│ ✅ Invoice Saved Successfully!                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Invoice #: INV-2025-001                                  │
│ Vendor: Công ty ABC                                      │
│ Total: 2,200,000 VND                                     │
│ Items: 2 line items                                      │
│                                                          │
│ Data is now saved and ready for ACSoft automation.      │
│                                                          │
│ [📥 Process Another Invoice]  [🤖 Automate ACSoft Now] │
└──────────────────────────────────────────────────────────┘

MOM'S OPTIONS:
  → Process more invoices: Click "Process Another" → Back to Stage 2
  → Fill ACSoft now: Click "Automate ACSoft Now" → Stage 6
```

**What's Stored:**

```sql
-- invoices table
INSERT INTO invoices VALUES (
  'INV-2025-001',
  'Công ty ABC',
  '0123-456-789',
  'INV-001',
  '2025-12-05',
  2200000,
  'READY_FOR_AUTOMATION',
  0.92,  -- confidence
  '2025-12-05 10:30:00',
  ...
);

-- invoice_items table (2 rows)
INSERT INTO invoice_items VALUES (...);

-- audit_log table
INSERT INTO audit_log VALUES (
  'Invoice INV-2025-001 created',
  'user_action',
  'mom',
  '2025-12-05 10:30:00'
);
```

---

### Stage 6: ACSoft Automation

**User Action:** Click "Automate ACSoft Now" button

**System Behavior:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 6: ACSOFT AUTOMATION (GUI AUTOMATION)                     │
└─────────────────────────────────────────────────────────────────┘

Frontend: "Automate ACSoft Now" clicked
  ↓
  POST /api/automation/start/{invoice_id}
  ↓
Backend: Automation request
  ↓
  ├─→ Check invoice status
  │   └─→ Must be "READY_FOR_AUTOMATION"
  │
  ├─→ Check ACSoft is running
  │   └─→ Search for ACSoft window (PyWinAuto)
  │   └─→ If not found: Prompt mom to open ACSoft first
  │
  ├─→ Load invoice data from database
  │
  └─→ Start ACSoftAutomationService
      ↓
      ACSoftAutomationService:
      
      STEP 1: Connect to ACSoft
      ├─→ Find ACSoft window by title
      ├─→ Verify window is active
      ├─→ Take screenshot (BEFORE automation)
      │   └─→ Save: data/screenshots/INV-2025-001_before.png
      └─→ Log: "Connected to ACSoft"
      
      STEP 2: Navigate to Data Entry Form
      ├─→ Click menu: Data → New Invoice
      ├─→ Wait for form to appear (max 5 sec)
      ├─→ Verify form loaded (check title bar)
      ├─→ Take screenshot (form ready)
      └─→ Log: "Data entry form opened"
      
      STEP 3: Fill Header Fields
      ├─→ For each field:
      │   ├─→ Find element (by auto_id, name, or class)
      │   ├─→ Verify element is editable
      │   ├─→ Clear existing value
      │   ├─→ Type new value
      │   ├─→ Verify value was entered correctly
      │   ├─→ Take screenshot
      │   └─→ Log: "Filled vendor_name: Công ty ABC"
      │
      └─→ Fields filled:
          - Vendor name: "Công ty ABC"
          - Tax ID: "0123-456-789"
          - Invoice number: "INV-001"
          - Invoice date: "05/12/2025"
          - Due date: "20/12/2025"
      
      STEP 4: Fill Line Items Grid
      ├─→ Find line items table
      ├─→ For each line item:
      │   ├─→ Click "Add Row" button
      │   ├─→ Wait for row to appear
      │   ├─→ Fill cells:
      │   │   - Description: "Product A"
      │   │   - Quantity: 10
      │   │   - Unit Price: 100,000
      │   │   - (Amount auto-calculated by ACSoft)
      │   ├─→ Verify values
      │   ├─→ Take screenshot
      │   └─→ Log: "Filled line item 1"
      │
      └─→ Total 2 line items added
      
      STEP 5: Verify Totals
      ├─→ Read subtotal field from ACSoft
      │   └─→ Expected: 2,200,000 | Actual: 2,200,000 ✅
      ├─→ Read tax field
      │   └─→ Expected: 220,000 | Actual: 220,000 ✅
      ├─→ Read total field
      │   └─→ Expected: 2,420,000 | Actual: 2,420,000 ✅
      └─→ Log: "Totals verified successfully"
      
      STEP 6: Pause for Human Review (CRITICAL!)
      ├─→ Take screenshot (FILLED FORM - BEFORE SAVE)
      │   └─→ Save: data/screenshots/INV-2025-001_filled.png
      ├─→ Update invoice status: "AUTOMATION_PAUSED"
      ├─→ Return control to mom
      └─→ Log: "Automation paused for review"

Frontend: Show automation complete dialog
  ↓
┌──────────────────────────────────────────────────────────┐
│ ✅ ACSoft Form Filled Successfully!                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ 🤖 Automation Status: COMPLETED                          │
│ ⏱️  Time Taken: 45 seconds                               │
│ ✅ All fields filled and verified                        │
│                                                          │
│ ⚠️  IMPORTANT: Please Review Form in ACSoft              │
│                                                          │
│ The form has been filled but NOT saved.                  │
│ Please review the form in ACSoft and:                    │
│                                                          │
│ 1. Check all fields are correct                         │
│ 2. Verify totals match                                   │
│ 3. Manually save in ACSoft (File → Save)                │
│                                                          │
│ ACSoft is now waiting for your manual save.             │
│                                                          │
│ [📸 View Screenshots]  [✅ Mark as Completed]           │
└──────────────────────────────────────────────────────────┘

MOM'S ACTIONS NOW:
  1. Switch to ACSoft window (Alt+Tab)
  2. Review filled form visually
  3. Verify numbers match invoice
  4. Manually click "Save" button in ACSoft
  5. Return to MAAS, click "Mark as Completed"
```

**Critical Safety Feature:**

```bash
🛑 SYSTEM NEVER AUTO-SAVES IN ACSOFT 🛑

Why?
- Financial data requires human verification
- Automation can make mistakes
- Mom needs final control
- Accounting compliance requires human approval

Mom ALWAYS manually saves in ACSoft after reviewing.
```

**Timing:** 30-60 seconds (depends on form complexity)  
**Screenshots:** 4-6 screenshots taken for audit trail  
**Verification:** System verifies each field after filling

---

### Stage 7: Completion & Next Invoice

**User Action:** Click "Mark as Completed" (after manually saving in ACSoft)

**System Behavior:**

```bash
┌─────────────────────────────────────────────────────────────────┐
│ STAGE 7: COMPLETION                                            │
└─────────────────────────────────────────────────────────────────┘

Frontend: "Mark as Completed" clicked
  ↓
  POST /api/invoices/{invoice_id}/complete
  ↓
Backend:
  ├─→ Update invoice status
  │   └─→ AUTOMATION_PAUSED → COMPLETED
  │
  ├─→ Record completion timestamp
  │
  ├─→ Update statistics
  │   ├─→ Total invoices processed: +1
  │   ├─→ Total time saved: +3.5 hours
  │   └─→ Success rate: 98.5%
  │
  ├─→ Log audit event
  │   └─→ "Invoice INV-2025-001 completed by mom at 10:35:00"
  │
  └─→ Return summary
      └─→ {
            status: "COMPLETED",
            next_invoice_ready: false,
            summary: {
              processed_today: 15,
              remaining: 35,
              time_saved: "2.5 hours"
            }
          }

Frontend: Show completion + stats
  ↓
┌──────────────────────────────────────────────────────────┐
│ ✅ Invoice Completed!                                    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Invoice INV-2025-001 has been processed successfully.   │
│                                                          │
│ 📊 Today's Statistics:                                   │
│ ├─ Invoices Processed: 15                               │
│ ├─ Time Saved: 2.5 hours                                │
│ ├─ Success Rate: 98.5%                                  │
│ └─ Remaining: 35 invoices                               │
│                                                          │
│ Great progress! 🎉                                       │
│                                                          │
│ [📥 Process Next Invoice]  [📊 View Dashboard]          │
└──────────────────────────────────────────────────────────┘

MOM'S OPTIONS:
  → Process next invoice: Click "Process Next" → Back to Stage 2
  → Take break: Click "View Dashboard" → See daily stats
  → Finish for today: Close application
```

---

## System Architecture Flow

### Component Interaction Diagram

```bash
┌─────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   MOM        │
│   (User)     │
└──────┬───────┘
       │ Interacts with
       ↓
┌─────────────────────────────────────────────┐
│   PRESENTATION LAYER (Frontend)             │
│   ├─ Vue.js Application                     │
│   ├─ Upload Interface                       │
│   ├─ PDF Preview Component                  │
│   ├─ Markdown Review Component              │
│   ├─ Edit Form Component                    │
│   └─ Automation Status Display              │
└────────────────┬────────────────────────────┘
                 │ HTTP/REST API
                 ↓
┌─────────────────────────────────────────────┐
│   APPLICATION LAYER (Backend - FastAPI)     │
│   ├─ API Routes                             │
│   │   ├─ /api/invoices/upload               │
│   │   ├─ /api/invoices/{id}/extract         │
│   │   ├─ /api/invoices/{id}/data (PUT)      │
│   │   ├─ /api/invoices/{id}/submit          │
│   │   └─ /api/automation/start/{id}         │
│   │                                          │
│   ├─ Workflow Orchestrator                  │
│   │   └─ Manages state transitions          │
│   │                                          │
│   └─ Business Logic Services                │
│       ├─ PDFPreviewService                  │
│       ├─ GeminiExtractionService            │
│       ├─ ValidationService                  │
│       ├─ MarkdownFormatterService           │
│       └─ ACSoftAutomationService            │
└────────────────┬────────────────────────────┘
                 │
     ┌───────────┼───────────────────┐
     │           │                   │
     ↓           ↓                   ↓
┌──────────┐ ┌─────────┐ ┌─────────────────┐
│ EXTERNAL │ │  DATA   │ │   AUTOMATION    │
│ SERVICES │ │  LAYER  │ │     LAYER       │
├──────────┤ ├─────────┤ ├─────────────────┤
│          │ │         │ │                 │
│ Gemini   │ │ SQLite  │ │ PyWinAuto       │
│ API      │ │ Database│ │ (ACSoft)        │
│          │ │         │ │                 │
│ $$       │ │ Local   │ │ PyAutoGUI       │
│ Cost per │ │ Storage │ │ (Fallback)      │
│ call     │ │         │ │                 │
└──────────┘ └─────────┘ └─────────────────┘
```

### Data Flow with State Transitions

```bash
┌─────────────────────────────────────────────────────────────────┐
│                    INVOICE LIFECYCLE                            │
└─────────────────────────────────────────────────────────────────┘

State: NULL
  ↓ (User uploads PDF)
State: UPLOADED
  - PDF saved to disk
  - Preview generated (local)
  - Temp record created
  ↓ (User clicks "Extract Data")
State: EXTRACTING
  - Gemini API called
  - Waiting for response...
  ↓ (Extraction complete)
State: EXTRACTED
  - Data returned from Gemini
  - Markdown view generated
  - Validation run
  ↓ (User reviews/edits)
State: VALIDATED
  - User approved data
  - Ready for submission
  ↓ (User clicks "Submit")
State: READY_FOR_AUTOMATION
  - Saved to database permanently
  - Audit log created
  - Ready for ACSoft
  ↓ (User clicks "Automate ACSoft")
State: AUTOMATING
  - PyWinAuto running
  - Filling ACSoft form
  - Screenshots being taken
  ↓ (Automation complete)
State: AUTOMATION_PAUSED
  - Form filled, waiting review
  - Mom reviews in ACSoft
  - Mom manually saves
  ↓ (User clicks "Mark as Completed")
State: COMPLETED
  - Invoice fully processed
  - Statistics updated
  - Ready for next invoice

ALTERNATIVE PATHS:
- UPLOADED → CANCELLED (User cancels, bad quality)
- EXTRACTING → EXTRACTION_FAILED (API error) → MANUAL_ENTRY
- AUTOMATING → AUTOMATION_FAILED → MANUAL_MODE
```

---

## Error Handling Flows

### Scenario 1: Gemini API Failure

```bash
┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO: GEMINI API FAILS                               │
└─────────────────────────────────────────────────────────────────┘

User clicks "Extract Data"
  ↓
Gemini API call
  ↓
ERROR: API Timeout / Rate Limit / Network Error
  ↓
Backend catches exception
  ↓
  ├─→ Retry logic (3 attempts with exponential backoff)
  │   ├─→ Attempt 1: Wait 2 seconds, retry
  │   ├─→ Attempt 2: Wait 4 seconds, retry
  │   └─→ Attempt 3: Wait 8 seconds, retry
  │
  └─→ If all retries fail:
      ↓
      Frontend shows error dialog
      ↓
┌──────────────────────────────────────────────────────────┐
│ ⚠️ Extraction Failed                                     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Unable to extract data from invoice.                     │
│                                                          │
│ Reason: Gemini API timeout                              │
│                                                          │
│ Options:                                                 │
│ 1. Try again (may work now)                             │
│ 2. Manual entry mode (you type the data)                │
│ 3. Process later (save for retry)                       │
│                                                          │
│ [🔄 Try Again]  [✍️ Manual Entry]  [💾 Save for Later] │
└──────────────────────────────────────────────────────────┘

MOM'S OPTIONS:
  → Try Again: Retry extraction immediately
  → Manual Entry: Show editable form with PDF preview
      └─→ Mom types data manually while looking at PDF
  → Save for Later: Mark invoice for retry, process next
```

---

### Scenario 2: ACSoft Automation Failure

```bash
┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO: ACSOFT AUTOMATION FAILS                        │
└─────────────────────────────────────────────────────────────────┘

Automation running...
  ↓
STEP 3: Fill vendor name field
  ↓
ERROR: Element not found (ACSoft UI changed?)
  ↓
Backend catches exception
  ↓
  ├─→ Take screenshot (debug info)
  ├─→ Log error details
  ├─→ Try fallback locator strategy
  │   └─→ Still fails
  │
  └─→ Switch to Manual Mode
      ↓
      Frontend shows manual mode dialog
      ↓
┌──────────────────────────────────────────────────────────┐
│ ⚠️ Automation Failed - Manual Mode                       │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Unable to automate ACSoft (element not found).          │
│                                                          │
│ Please enter data manually in ACSoft using this guide:  │
│                                                          │
│ ┌────────────────────────────────────────────────┐      │
│ │ FIELD              VALUE            [Copy]     │      │
│ ├────────────────────────────────────────────────┤      │
│ │ Vendor Name        Công ty ABC      [📋]       │      │
│ │ Tax ID             0123-456-789     [📋]       │      │
│ │ Invoice Number     INV-001          [📋]       │      │
│ │ Date               05/12/2025       [📋]       │      │
│ │                                                │      │
│ │ Line 1: Product A, Qty: 10, Price: 100,000    │      │
│ │ Line 2: Service B, Qty: 6, Price: 200,000     │      │
│ │                                                │      │
│ │ Total: 2,420,000 VND                          │      │
│ └────────────────────────────────────────────────┘      │
│                                                          │
│ 1. Click [Copy] button for each field                   │
│ 2. Paste into corresponding field in ACSoft             │
│ 3. When done, mark as completed below                   │
│                                                          │
│ [✅ I've Entered Data Manually]  [📸 View PDF]         │
└──────────────────────────────────────────────────────────┘

KEY INSIGHT: System remains useful even when automation breaks!
            Mom still saves time via extraction + validation.
```

---

### Scenario 3: Low Confidence Extraction

```bash
┌─────────────────────────────────────────────────────────────────┐
│ ERROR SCENARIO: LOW CONFIDENCE EXTRACTION (< 85%)              │
└─────────────────────────────────────────────────────────────────┘

Extraction completes
  ↓
Confidence Score: 72% (below 85% threshold)
  ↓
System flags for mandatory review
  ↓
Frontend shows warning dialog
  ↓
┌──────────────────────────────────────────────────────────┐
│ ⚠️ Low Confidence Extraction                             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ Confidence: 72% 🟠 (Low)                                │
│                                                          │
│ The system is not very confident about this extraction. │
│ Please review carefully!                                 │
│                                                          │
│ Potential Issues:                                        │
│ ❌ Vendor name unclear (blurry text)                     │
│ ⚠️  Tax ID format unusual (9 digits instead of 10)      │
│ ⚠️  Date format ambiguous (DD/MM vs MM/DD?)             │
│ ✅ Line items extracted successfully                     │
│ ⚠️  Total amount: 2 interpretations possible            │
│                                                          │
│ 🚫 AUTOMATION DISABLED (confidence too low)             │
│                                                          │
│ [📝 Review & Edit Data]  [❌ Reject & Re-scan]          │
└──────────────────────────────────────────────────────────┘

MOM MUST:
  → Review data extra carefully
  → Correct errors manually
  → Automation will be DISABLED until mom fixes issues
  → After correction, can manually enter in ACSoft
```

---

## Alternative Scenarios

### Scenario A: Batch Processing Multiple Invoices

```bash
┌─────────────────────────────────────────────────────────────────┐
│ BATCH MODE: Process 10 invoices, then automate all             │
└─────────────────────────────────────────────────────────────────┘

Mom's Workflow:
  1. Upload Invoice 1 → Extract → Review → Submit
  2. Upload Invoice 2 → Extract → Review → Submit
  3. Upload Invoice 3 → Extract → Review → Submit
  ... (repeat 10 times)
  
  10. Click "Batch Automate All"
      ↓
      System queues 10 invoices
      ↓
      For each invoice:
        ├─ Automate ACSoft
        ├─ Pause for review
        ├─ Wait for mom's "Looks good"
        └─ Move to next
      ↓
      All 10 completed in 15 minutes (vs 2 hours manually!)
```

---

### Scenario B: Multi-Page Invoice

```bash
┌─────────────────────────────────────────────────────────────────┐
│ MULTI-PAGE INVOICE (e.g., 3 pages, 50 line items)             │
└─────────────────────────────────────────────────────────────────┘

Upload PDF (3 pages)
  ↓
Preview shows: "3 pages detected"
  ↓
Mom reviews all 3 page thumbnails
  ↓
Click "Extract Data"
  ↓
Gemini processes all 3 pages together (context-aware)
  ↓
Returns consolidated data:
  - Header from page 1
  - Line items 1-20 from page 1
  - Line items 21-40 from page 2
  - Line items 41-50 + totals from page 3
  ↓
Mom reviews consolidated markdown view
  ↓
System validates:
  ✅ Total matches across pages
  ✅ Line item numbering sequential
  ✅ No duplicate items
  ↓
Submit → Automate (fills all 50 line items in ACSoft)
```

---

### Scenario C: Duplicate Invoice Detection

```bash
┌─────────────────────────────────────────────────────────────────┐
│ DUPLICATE INVOICE DETECTED                                     │
└─────────────────────────────────────────────────────────────────┘

Mom uploads invoice
  ↓
Extract data
  ↓
Validation runs
  ↓
Duplicate Detector finds match:
  - Same vendor + invoice number already in database
  - Processed 2 days ago
  ↓
Frontend shows warning dialog
  ↓
┌──────────────────────────────────────────────────────────┐
│ ⚠️ Duplicate Invoice Detected                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ This invoice may have already been processed:           │
│                                                          │
│ Existing Invoice:                                        │
│ - Vendor: Công ty ABC                                    │
│ - Invoice #: INV-001                                     │
│ - Date: 2025-12-03                                       │
│ - Total: 2,200,000 VND                                   │
│ - Processed: 2 days ago                                  │
│                                                          │
│ Current Invoice:                                         │
│ - Vendor: Công ty ABC                                    │
│ - Invoice #: INV-001                                     │
│ - Date: 2025-12-05 (different!)                         │
│ - Total: 2,200,000 VND                                   │
│                                                          │
│ Is this a duplicate or a correction?                     │
│                                                          │
│ [❌ Duplicate - Skip]  [✏️ Correction - Replace]        │
│ [✅ Different Invoice - Continue]                        │
└──────────────────────────────────────────────────────────┘
```

---

## Performance Metrics

### Target Performance (Phase 1-3)

| Operation | Target | Measured By |
|-----------|--------|-------------|
| **App Launch** | < 5 seconds | Time from icon click to UI ready |
| **PDF Preview** | < 1 second | Upload to preview display |
| **AI Extraction** | < 8 seconds | API call to results displayed |
| **Data Validation** | < 1 second | In-memory processing |
| **Database Save** | < 0.5 seconds | Write to SQLite |
| **ACSoft Automation** | < 60 seconds | Full form filling + verification |
| **End-to-End** | < 2 minutes | Upload to completed |

### Success Metrics

| Metric | Target | Current (After Rollout) |
|--------|--------|-------------------------|
| **Time Saved** | 80-90% reduction | (TBD) |
| **Extraction Accuracy** | > 95% | (TBD) |
| **Automation Success** | > 98% | (TBD) |
| **User Satisfaction** | > 8/10 | (TBD) |
| **System Uptime** | > 99% | (TBD) |
| **Manual Corrections** | < 5% of invoices | (TBD) |

---

## Summary: Key Design Principles

### 1. Human-in-the-Loop (Most Important!)

- ✅ User reviews BEFORE AI processes (quality check)
- ✅ User reviews AFTER AI processes (data accuracy)
- ✅ User reviews BEFORE save (final verification)
- ✅ **User ALWAYS manually saves in ACSoft** (safety!)

### 2. Cost Optimization

- ✅ Preview first (free local tools)
- ✅ AI triggered by user action (not automatic)
- ✅ No wasted API calls on bad scans

### 3. User Control & Transparency

- ✅ Clear workflow stages
- ✅ Visible confidence scores
- ✅ Editable at every step
- ✅ Change tracking

### 4. Graceful Degradation

- ✅ Manual mode if AI fails
- ✅ Manual mode if automation fails
- ✅ System remains useful even when broken

### 5. Safety First

- ✅ Comprehensive validation
- ✅ Audit trail (screenshots, logs)
- ✅ No auto-save (human approval required)
- ✅ Duplicate detection

### 6. Non-Technical User Design

- ✅ One-click launch (no terminal)
- ✅ Visual feedback at every step
- ✅ User-friendly error messages
- ✅ Guided workflow (clear next steps)

---

## Next Steps: Implementation

**Phase 1 (Weeks 1-2): MVP**

1. ✅ Desktop application packaging (PWA with launcher)
2. ✅ PDF upload + preview (local, free)
3. ✅ Gemini extraction (API integration)
4. ✅ Markdown comparison view
5. ✅ Basic validation
6. ✅ Database storage
7. ✅ ACSoft automation (single vendor format)
8. ✅ Test with mom (10-20 invoices)

**Phase 2 (Week 3): Enhancement**

- Multi-vendor support
- Advanced validation rules
- Confidence scoring refinement
- Error recovery improvements
- Performance optimization

**Phase 3 (Week 4): Polish**

- Electron desktop app (native UX)
- User documentation
- Monitoring dashboard
- Backup automation
- Production deployment

---

**Document Status:** Complete Design - Ready for Implementation  
**Last Updated:** December 5, 2025  
**Next Action:** Begin Phase 1 implementation (Task-1.5: Desktop packaging)

---

*This workflow document captures the complete system design as of December 5, 2025, incorporating all updates including deployment architecture, PDF preview workflow, and human-in-the-loop design principles.*
