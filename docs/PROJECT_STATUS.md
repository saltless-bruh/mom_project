# Mom's Accounting Automation System (MAAS) - Project Documentation

**Version:** 1.0.0 (MVP Foundation)
**Date:** December 10, 2025

## 1. Project Overview

**Mom's Accounting Automation System (MAAS)** is a specialized, local desktop application designed to assist accountants in automating the tedious process of entering Vietnamese PDF invoices into the **ACSoft** accounting software.

The system acts as an intelligent bridge, converting unstructured PDF documents into structured data, verifying the accuracy of that data, and then "typing" it into the accounting software automatically.

### Core Philosophy

* **"Panic Button" Safety**: The user is always in control. The system validates data but allows the user to make the final decision.
* **Offline First**: All data (PDFs, Database) is stored locally on the user's machine for privacy and speed.
* **Zero-Config Deployment**: Runs from a single folder without requiring complex installation (Python is embedded).

---

## 2. Key Features

### 📄 Intelligent Data Extraction

* **Engine**: Powered by **Google Gemini 2.0 Flash (Experimental)**, a multimodal AI capable of "reading" Vietnamese invoices with high accuracy.
* **Process**: Converts PDF pages to high-resolution images and extracts key fields: `Invoice Number`, `Date`, `Vendor Name`, `Tax ID`, and all `Line Items`.
* **Logic**: Handles various patterns of Vietnamese dates (DD/MM/YYYY) and currency formats (VND 100.000 vs 100,000).

### 🛡️ Smart Data Validation

Before data enters the accounting software, it passes through a rigorous validation engine:

* **Math Check**: Verifies that `Quantity × Unit Price` equals the `Line Total` for every item.
* **Tax Audit**: Checks that `Subtotal + Tax Amount` equals the `Grand Total` (within a 5 VND tolerance).
* **Completeness**: Flags missing required fields like Invoice Date or Number.
* **User Feedback**: Warnings are displayed clearly in the UI, allowing "Mom" to spot errors instantly.

### 🖥️ Modern User Interface

* **Dashboard**: A clean, single-page view showing the status of all invoices (`Uploaded`, `Processing`, `Validated`, `Completed`).
* **Split-Screen Review**: Allows the user to view the original PDF on the left and the extracted data on the right simultaneously.
* **No-Build Architecture**: Built with standard HTML/JS (Vue 3) for maximum stability and ease of modification.

### 🤖 Robotic Process Automation (RPA)

* **ACSoft Integration**: Uses **PyWinAuto** to directly control the ACSoft desktop application.
* **Global Kill Switch**: Pressing **`F12`** at any time immediately stops the automation script, preventing rogue data entry.
* **Simulation Mode**: Currently runs in "Dry Run" mode to test logic without affecting live data.

---

## 3. Technical Architecture

### Component Diagram

```
[ User ] <--> [ Web UI (Vue.js) ] <--> [ FastAPI Server ] <--> [ SQLite DB ]
                                            |
                                            +--> [ Gemini AI Client ]
                                            |
                                            +--> [ Automation Service ] --> [ ACSoft.exe ]
```

### Technology Stack

* **Backend**: Python 3.11 (Embedded), FastAPI, Uvicorn.
* **Frontend**: Vue.js 3, TailwindCSS, Phosphor Icons (HTML/JS).
* **Database**: SQLite (WAL Enabled) with `aiosqlite` for async access.
* **AI**: Google Generative AI SDK (`google-generativeai`).
* **Automation**: `pywinauto` for Windows GUI control, `keyboard` for hotkeys.
* **Packaging**: Custom VBS launcher + Batch installer.

### Data Security

* **Local Storage**: PDFs are saved to `data/uploads/`.
* **Archival**: Processed invoices are automatically moved to `data/archive/{Year}/{Month}/`.
* **Backups**: Automated daily backups of the database to `data/backups/`.

---

## 4. Operational Workflow

1. **Launch**: User clicks the "MAAS" desktop shortcut. The system starts invisibly in the tray.
2. **Upload**: User drags & drops a batch of PDF invoices into the Web Dashboard.
3. **Processing**: The system automatically sends PDFs to Gemini for extraction.
4. **Review**:
    * User sees invoices marked as "Needs Review" (orange) or "Validated" (green).
    * User clicks an invoice to verify details against the PDF view.
5. **Automate**:
    * User clicks "Send to ACSoft".
    * The system takes control of the mouse/keyboard and enters the data into the open ACSoft window.
6. **Completion**: The invoice status is updated to "Completed".

---

## 5. Implementation Status

### ✅ Completed Modules

* **Project Structure**: Full Python project skeleton with embedded runtime.
* **Database**: Operational with Backup Service.
* **Gemini Integration**: Fully functional extraction service.
* **Validation Engine**: Strict math and logic checks implemented.
* **Backend API**: Fast and robust API endpoints serving the frontend.
* **Web UI**: Responsive Dashboard and Detail View.
* **Automation Framework**: "Dry Run" service with Kill Switch.

### 🚧 Pending Configuration (Requires Target Machine)

* **UI Discovery**: We generated a `scripts/inspect_ui.py` tool. This **must** be run on "Mom's" computer to finding the exact "Control IDs" (variable names) used by her specific version of ACSoft.
* **Mapping**: Once IDs are found, `app/services/automation.py` needs to be updated one-time to map our data fields to those IDs.

---

## 6. Next Steps

1. **Deployment**: Copy the project folder to Mom's computer.
2. **Configuration**: Run `inspect_ui.py` with ACSoft open.
3. **Final Polish**: Update the automation script with the real Control IDs and disable "Dry Run".

---
**Maintained By**: Developer Team
**License**: Private / Proprietary
