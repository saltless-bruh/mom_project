# Requirements Document

## Mom's Accounting Automation System (MAAS)

**Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Approved

---

## 1. Business Requirements

### 1.1 Project Overview

**Project Name:** Mom's Accounting Automation System (MAAS)

**Business Problem:**
Mom spends 4-6 hours daily manually entering invoice data into ACSoft accounting software. This repetitive task is physically tiring, error-prone, and reduces time available for family and higher-value accounting work.

**Business Objective:**
Reduce manual data entry time by 80-90% (from 4-6 hours to 0.5-1 hour per day) while maintaining 95%+ accuracy and ensuring data safety.

**Success Metrics:**

- Time savings: 3-5 hours per day
- Accuracy: 95%+ extraction accuracy
- Safety: 0 incidents of unauthorized data saves
- User satisfaction: Mom finds system easy to use
- ROI: Break-even on first day of deployment

### 1.2 Stakeholders

| Stakeholder | Role | Primary Concerns |
|-------------|------|------------------|
| Mom | Primary User | Ease of use, reliability, safety |
| Family | Sponsors | Cost, time savings, mom's wellbeing |
| Vendors | Data Providers | Invoice accuracy |
| Tax Authorities | Regulators | Audit trail, compliance |

### 1.3 Scope

**In Scope:**

- ✅ PDF invoice data extraction
- ✅ Data validation and normalization
- ✅ ACSoft GUI automation
- ✅ Human review workflow
- ✅ Audit logging
- ✅ Local deployment

**Out of Scope:**

- ❌ Cloud deployment
- ❌ Multi-user support
- ❌ Mobile application
- ❌ Email integration (Phase 1-3)
- ❌ Financial reporting (Phase 1-3)
- ❌ Integration with other accounting software

---

## 2. Functional Requirements

### 2.1 Invoice Upload & Extraction

**REQ-F001: PDF Upload**

- **Description:** User shall be able to upload PDF invoice files
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Support PDF files up to 50MB
  - Support multi-page PDFs
  - Validate file type before processing
  - Show upload progress
  - Handle upload errors gracefully

**REQ-F002: Data Extraction**

- **Description:** System shall extract structured data from Vietnamese invoices
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Extract vendor name, tax ID, address
  - Extract invoice number, date, payment terms
  - Extract line items (description, quantity, unit, price, discount, tax)
  - Calculate subtotals, tax totals, grand total
  - Support Vietnamese text (UTF-8)
  - Process multi-page invoices
  - Return confidence score for extraction

**REQ-F003: Extraction Quality**

- **Description:** System shall meet extraction accuracy targets
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Overall accuracy: 95%+
  - Confidence score: 0.85+ for automatic processing
  - Process time: < 5 seconds per page
  - Handle poor scan quality gracefully

### 2.2 Data Validation

**REQ-F004: Required Field Validation**

- **Description:** System shall validate presence of required fields
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Vendor name is required
  - Invoice number is required
  - Invoice date is required
  - At least one line item is required
  - Total amount is required
  - Clear error messages for missing fields

**REQ-F005: Format Validation**

- **Description:** System shall validate data formats
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Dates in YYYY-MM-DD format
  - Currency amounts as numbers (VND)
  - Tax rates: 0%, 5%, 8%, or 10%
  - Quantities and prices as positive numbers
  - Invoice numbers as strings

**REQ-F006: Business Rule Validation**

- **Description:** System shall enforce business rules
- **Priority:** P1 (High)
- **Acceptance Criteria:**
  - Maximum discount: 50%
  - Valid tax rates only
  - Positive quantities and prices
  - Future dates flagged as warnings
  - Duplicate invoice detection

**REQ-F007: Calculation Verification**

- **Description:** System shall verify arithmetic accuracy
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Line subtotal = quantity × unit_price
  - Line discount = subtotal × discount_percent
  - Line tax = (subtotal - discount) × tax_percent
  - Line total = subtotal - discount + tax
  - Invoice totals match sum of line items
  - Tolerance: ±1 VND for rounding

### 2.3 Data Review & Correction

**REQ-F008: Review Interface**

- **Description:** User shall review extracted data before automation
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Display all extracted fields
  - Highlight low-confidence fields
  - Show validation errors and warnings
  - Display original PDF side-by-side
  - Enable field editing

**REQ-F009: Manual Correction**

- **Description:** User shall be able to correct extracted data
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Edit any field
  - Add/remove line items
  - Re-validate after edits
  - Track manual corrections
  - Save corrections

### 2.4 ACSoft Automation

**REQ-F010: ACSoft Connection**

- **Description:** System shall connect to running ACSoft instance
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Detect ACSoft window
  - Verify correct version/screen
  - Handle connection failures
  - Timeout after 30 seconds

**REQ-F011: Form Field Population**

- **Description:** System shall populate ACSoft form fields
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Fill vendor information
  - Fill invoice header
  - Fill all line items
  - Apply discounts and taxes
  - Verify each entry
  - Take screenshots for audit

**REQ-F012: Safety Mechanisms**

- **Description:** System shall prevent accidental data saves
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - **NEVER auto-save in ACSoft**
  - Pause after filling form
  - Prompt user to review
  - User must manually save in ACSoft
  - Log completion only after user confirmation

**REQ-F013: Error Recovery**

- **Description:** System shall handle automation errors gracefully
- **Priority:** P1 (High)
- **Acceptance Criteria:**
  - Detect element not found errors
  - Pause on unexpected UI changes
  - Capture screenshot at failure point
  - Log error details
  - Allow user to retry or cancel

### 2.5 Audit & Logging

**REQ-F014: Audit Trail**

- **Description:** System shall maintain complete audit trail
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Log all invoice operations
  - Log all user actions
  - Log all system errors
  - Include timestamps
  - Store for 1 year minimum

**REQ-F015: Screenshot Capture**

- **Description:** System shall capture automation screenshots
- **Priority:** P1 (High)
- **Acceptance Criteria:**
  - Screenshot before each action
  - Screenshot at completion
  - Screenshot at errors
  - Store with invoice record
  - Retain for 30 days

### 2.6 Data Management

**REQ-F016: Invoice Storage**

- **Description:** System shall store invoice data persistently
- **Priority:** P0 (Critical)
- **Acceptance Criteria:**
  - Store original PDF
  - Store extracted data
  - Store validation results
  - Store automation logs
  - Enable search and retrieval

**REQ-F017: Duplicate Detection**

- **Description:** System shall detect duplicate invoices
- **Priority:** P1 (High)
- **Acceptance Criteria:**
  - Check vendor + invoice number + date
  - Check PDF file hash
  - Warn user of potential duplicates
  - Allow override with confirmation

**REQ-F018: Data Backup**

- **Description:** System shall backup data automatically
- **Priority:** P1 (High)
- **Acceptance Criteria:**
  - Daily automated backup
  - Backup database and PDFs
  - Retain backups for 30 days
  - Verify backup integrity
  - Enable restore functionality

---

## 3. Non-Functional Requirements

### 3.1 Performance Requirements

**REQ-NFR001: Processing Speed**

- **Description:** System shall process invoices efficiently
- **Requirement:**
  - PDF extraction: < 5 seconds per page
  - Data validation: < 1 second
  - ACSoft automation: < 30 seconds
  - End-to-end: < 2 minutes per invoice
- **Priority:** P1 (High)

**REQ-NFR002: API Response Time**

- **Description:** API shall respond quickly
- **Requirement:**
  - GET requests: < 500ms
  - POST requests (except extraction): < 1 second
  - Extraction requests: < 30 seconds
- **Priority:** P2 (Medium)

**REQ-NFR003: Database Query Performance**

- **Description:** Database queries shall be fast
- **Requirement:**
  - Simple queries: < 100ms
  - Complex queries: < 500ms
  - Bulk operations: < 5 seconds
- **Priority:** P2 (Medium)

### 3.2 Reliability Requirements

**REQ-NFR004: System Uptime**

- **Description:** System shall be available when needed
- **Requirement:**
  - 99%+ availability during work hours
  - Graceful degradation on errors
  - Automatic recovery from transient failures
- **Priority:** P1 (High)

**REQ-NFR005: Data Integrity**

- **Description:** System shall maintain data integrity
- **Requirement:**
  - No data loss
  - ACID database transactions
  - Data validation at all layers
  - Audit trail for all changes
- **Priority:** P0 (Critical)

**REQ-NFR006: Error Handling**

- **Description:** System shall handle errors gracefully
- **Requirement:**
  - No unhandled exceptions
  - Clear error messages
  - Retry logic for transient failures
  - User-friendly error reporting
- **Priority:** P1 (High)

### 3.3 Usability Requirements

**REQ-NFR007: Ease of Use (DEPLOYMENT & UX)**

- **Description:** System shall be operable by non-technical user without ANY command-line or technical knowledge
- **Priority:** P0 (CRITICAL) - System unusable otherwise
- **Category:** Usability & Deployment

**CRITICAL REQUIREMENT:** Mom cannot use terminal/command line.

**Mandatory User Experience:**

1. One-click launch - Desktop icon double-click only
2. No terminal exposure - User never sees command prompt
3. No manual server starting - Backend auto-starts invisibly
4. No URL typing - User never types "localhost"
5. Visual feedback - All operations have clear status
6. Graceful errors - No stack traces, only user-friendly messages
7. System tray indicator - Shows running status

**Acceptance Criteria - Phase 1 (PWA with Auto-Start):**

- [ ] Double-click desktop shortcut launches system
- [ ] Backend starts automatically in hidden window
- [ ] Browser opens to application automatically
- [ ] Application opens in fullscreen/app mode (no URL bar visible)
- [ ] System tray icon shows running status (optional for Phase 1)
- [ ] One-click shutdown from tray icon or window close
- [ ] Auto-start on Windows login (optional user setting)
- [ ] **Critical Test:** Non-technical user can operate without any help

**Acceptance Criteria - Phase 2-3 (Electron Desktop App):**

- [ ] Single .exe installer with setup wizard
- [ ] Desktop shortcut created automatically during installation
- [ ] App indistinguishable from native Windows application
- [ ] No browser chrome or URL bar visible
- [ ] System tray integration with status menu
- [ ] Auto-update capability built-in
- [ ] Standard Windows uninstaller in Add/Remove Programs
- [ ] **Critical Test:** Mom can update app without help

**PROHIBITED Behaviors (System MUST NEVER):**

- ❌ Show terminal or command prompt to user
- ❌ Require user to type "python run.py" or similar commands
- ❌ Show "localhost:8000" or any URL in browser
- ❌ Require manual starting/stopping of services
- ❌ Require editing configuration files manually
- ❌ Show Python tracebacks or technical error messages

**Success Test:**

- Mom's sister (also non-technical) can use system after 5-minute visual demo
- No phone calls for help during first week of use
- Mom uses system daily without technical issues

**REQ-NFR008: User Feedback**

- **Description:** System shall provide clear feedback
- **Requirement:**
  - Progress indicators
  - Success/error notifications
  - Confidence scores displayed
  - Validation results clearly shown
- **Priority:** P1 (High)

### 3.4 Security Requirements

**REQ-NFR009: Data Privacy**

- **Description:** System shall protect sensitive data
- **Requirement:**
  - All data stored locally only
  - No cloud storage (except Gemini processing)
  - API keys in environment variables
  - No sensitive data in logs
- **Priority:** P0 (Critical)

**REQ-NFR010: Access Control**

- **Description:** System shall control access appropriately
- **Requirement:**
  - Web UI accessible only from localhost
  - No external network access
  - Database file permissions: 600
  - No authentication needed (single user)
- **Priority:** P1 (High)

**REQ-NFR011: Audit Security**

- **Description:** System shall maintain tamper-proof audit logs
- **Requirement:**
  - Append-only audit logs
  - Timestamp all events
  - Log all access attempts
  - Retain logs for compliance
- **Priority:** P1 (High)

### 3.5 Maintainability Requirements

**REQ-NFR012: Code Quality**

- **Description:** Code shall be maintainable
- **Requirement:**
  - Follow PEP 8 style guide
  - Type hints on all functions
  - Docstrings on all public functions
  - Test coverage > 80%
- **Priority:** P1 (High)

**REQ-NFR013: Documentation**

- **Description:** System shall be well-documented
- **Requirement:**
  - User manual
  - Technical specifications
  - API documentation
  - Troubleshooting guide
- **Priority:** P1 (High)

**REQ-NFR014: Logging**

- **Description:** System shall log operations comprehensively
- **Requirement:**
  - Structured logging
  - Multiple log levels
  - Log rotation
  - Searchable logs
- **Priority:** P2 (Medium)

### 3.6 Scalability Requirements

**REQ-NFR015: Current Scale**

- **Description:** System shall handle current workload
- **Requirement:**
  - 50-100 invoices per day
  - Single concurrent user
  - Sequential processing
  - Local deployment only
- **Priority:** P0 (Critical)

**REQ-NFR016: Future Scalability**

- **Description:** System shall be designed for future growth
- **Requirement:**
  - Modular architecture
  - Stateless API design
  - Dependency injection
  - Abstract database layer
- **Priority:** P2 (Medium)

### 3.7 Compatibility Requirements

**REQ-NFR017: Platform Compatibility**

- **Description:** System shall run on target platform
- **Requirement:**
  - Windows 10/11 (64-bit)
  - Python 3.9+
  - ACSoft (current version)
  - Modern web browser
- **Priority:** P0 (Critical)

**REQ-NFR018: Data Format Compatibility**

- **Description:** System shall support common formats
- **Requirement:**
  - PDF 1.4+ format
  - UTF-8 text encoding
  - Vietnamese language
  - JSON for API responses
- **Priority:** P0 (Critical)

**REQ-NFR019: Installation & Deployment**

- **Description:** System installation and deployment must be simple enough for family member to perform without technical knowledge
- **Priority:** P0 (CRITICAL)
- **Category:** Usability & Deployment

**Installation Requirements:**

1. **Single installer file**
   - Phase 1: `MAAS-Install.bat` (batch file with embedded Python)
   - Phase 2-3: `MAAS-Setup.exe` (full installer wizard)

2. **One-click installation process**
   - Double-click installer → Follow simple wizard
   - Desktop shortcut created automatically
   - No manual configuration required

3. **Automatic dependency installation**
   - Python runtime embedded (no separate install)
   - All libraries included
   - No pip commands needed

4. **Clear success confirmation**
   - "Installation Complete!" message
   - Instructions: "Double-click MAAS icon to start"
   - Option to launch immediately

**Uninstallation Requirements:**

- Standard Windows "Add/Remove Programs" entry
- Complete file cleanup
- Data preservation option

**Acceptance Criteria:**

- [ ] Family member can install without help
- [ ] Installation completes in < 5 minutes
- [ ] Works immediately after installation
- [ ] **Critical Test:** Non-technical relative installs successfully

---

## 4. User Requirements

### 4.1 User Stories

**US-001: Upload Invoice**

- **As** Mom
- **I want** to upload invoice PDFs easily
- **So that** I can start the automation process quickly

**US-002: Review Extracted Data**

- **As** Mom
- **I want** to review extracted invoice data
- **So that** I can verify accuracy before automation

**US-003: Correct Errors**

- **As** Mom
- **I want** to correct extraction errors
- **So that** accurate data is entered into ACSoft

**US-004: Automate Entry**

- **As** Mom
- **I want** the system to fill ACSoft forms automatically
- **So that** I don't have to type manually

**US-005: Final Review**

- **As** Mom
- **I want** to review data in ACSoft before saving
- **So that** I can ensure everything is correct

**US-006: Track History**

- **As** Mom
- **I want** to see history of processed invoices
- **So that** I can verify what's been done

### 4.2 User Workflows

**Workflow 1: Standard Invoice Processing**

```bash
1. Mom uploads PDF invoice
2. System extracts data (3-5 seconds)
3. Mom reviews extraction results
4. Mom corrects any errors (if needed)
5. Mom approves for automation
6. System fills ACSoft form (20-30 seconds)
7. Mom reviews in ACSoft
8. Mom manually saves in ACSoft
9. System logs completion
```

**Workflow 2: Low Confidence Invoice**

```bash
1. Mom uploads PDF invoice
2. System extracts data with low confidence
3. System highlights uncertain fields
4. Mom manually corrects uncertain fields
5. System re-validates
6. Proceed with standard workflow
```

**Workflow 3: Duplicate Detection**

```bash
1. Mom uploads PDF invoice
2. System detects potential duplicate
3. System shows existing invoice
4. Mom confirms: new or duplicate
5a. If duplicate: Skip processing
5b. If new: Proceed with standard workflow
```

---

## 5. Interface Requirements

### 5.1 User Interface Requirements

**REQ-UI001: Upload Interface**

- Drag-and-drop support
- File browser button
- Upload progress bar
- File type validation

**REQ-UI002: Review Interface**

- Split view: PDF on left, data on right
- Editable fields
- Highlight errors and warnings
- Show confidence scores
- Approve/reject buttons

**REQ-UI003: Status Dashboard**

- List of recent invoices
- Processing status for each
- Filter by status (pending, completed, failed)
- Search by invoice number or vendor

**REQ-UI004: Automation Progress**

- Real-time progress updates
- Screenshot preview
- Pause/cancel buttons
- Error notifications

### 5.2 API Interface Requirements

**REQ-API001: REST API**

- JSON request/response format
- HTTP status codes
- Error response format
- API documentation (Swagger/OpenAPI)

**REQ-API002: Endpoints**

- Invoice upload: `POST /api/invoices/upload`
- Get extraction: `GET /api/invoices/{id}/extraction`
- Update data: `PUT /api/invoices/{id}/data`
- Trigger automation: `POST /api/invoices/{id}/automate`
- Get status: `GET /api/automation/{id}/status`
- List invoices: `GET /api/invoices`

### 5.3 External Interface Requirements

**REQ-EXT001: Gemini API**

- HTTPS connection
- JSON request/response
- API key authentication
- Error handling for rate limits

**REQ-EXT002: ACSoft Integration**

- Windows UI Automation
- PyWinAuto library
- Screen coordinate fallback (PyAutoGUI)
- Screenshot capture

---

## 6. Data Requirements

### 6.1 Data Entities

**Invoice Data:**

- Vendor information (name, tax ID, address)
- Invoice metadata (number, date, payment terms)
- Line items (description, quantity, unit, price, discount, tax)
- Totals (subtotal, discount total, tax total, grand total)
- Processing metadata (confidence, errors, timestamps)

**Audit Data:**

- User actions
- System events
- Error logs
- Performance metrics

**Configuration Data:**

- Gemini API settings
- Validation rules
- ACSoft element locators
- System preferences

### 6.2 Data Retention

| Data Type | Retention Period | Reason |
|-----------|------------------|--------|
| Invoice PDFs | 7 years | Tax compliance |
| Extracted data | 7 years | Business records |
| Audit logs | 1 year | Troubleshooting |
| Screenshots | 30 days | Audit trail |
| Backups | 30 days | Recovery |

---

## 7. Constraints & Assumptions

### 7.1 Constraints

**Technical Constraints:**

- Must run on Windows 10/11
- Must work with current ACSoft version
- Must be installed locally (no cloud)
- Limited to Python ecosystem

**Business Constraints:**

- Budget: Gemini API costs only (~$3-5/month)
- Timeline: 4 weeks for MVP
- Resources: Single developer

**Operational Constraints:**

- Single user (Mom) only
- Sequential processing (no concurrency needed)
- Work hours: 8 AM - 6 PM daily

### 7.2 Assumptions

**Technical Assumptions:**

- Gemini API remains available and affordable
- ACSoft UI remains relatively stable
- Windows UI Automation continues to work
- Internet connection available for API calls

**Business Assumptions:**

- Invoice volume stays at 50-100 per day
- Invoice formats remain relatively consistent
- Mom has basic computer literacy
- ACSoft remains the primary accounting software

### 7.3 Dependencies

**External Dependencies:**

- Google Gemini API availability
- ACSoft software availability
- Python 3.9+ availability
- Internet connectivity

**Internal Dependencies:**

- Phase 1 completion before Phase 2
- Database initialization before first use
- API key configuration before operations

---

## 8. Acceptance Criteria

### 8.1 Phase 1 (MVP) Acceptance

- [ ] Upload PDF and extract data from 1 vendor format
- [ ] Validation catches missing/invalid fields
- [ ] Database stores invoice records
- [ ] FastAPI endpoints functional
- [ ] Simple web UI allows upload and review
- [ ] PyWinAuto script successfully fills ACSoft form
- [ ] Unit tests pass with 80%+ coverage
- [ ] System processes 10 test invoices successfully

### 8.2 Phase 2 (Enhancement) Acceptance

- [ ] Extract data from 5+ different vendor formats
- [ ] Handle errors gracefully with recovery
- [ ] Monitoring dashboard shows processing status
- [ ] Screenshot audit trail working
- [ ] Integration tests pass
- [ ] System processes 30 test invoices successfully
- [ ] Processing time < 2 minutes per invoice

### 8.3 Phase 3 (Production) Acceptance

- [ ] User manual complete and reviewed by Mom
- [ ] Automated backups working
- [ ] Performance meets targets
- [ ] Mom successfully processes 20 real invoices
- [ ] No critical bugs remaining
- [ ] All documentation complete
- [ ] Deployment script works correctly
- [ ] Mom approves system for daily use

---

## 9. Regulatory & Compliance

### 9.1 Data Protection

**Requirements:**

- All data stored locally (GDPR not applicable for personal use)
- Vendor data protected with file permissions
- API keys secured in environment variables
- No data sharing with third parties

### 9.2 Accounting Compliance

**Requirements:**

- Maintain audit trail for 1+ year
- Invoice records retained for 7+ years (tax law)
- Accurate data entry (95%+ accuracy)
- Human verification before final save

---

## Appendix A: Requirement Traceability Matrix

| Requirement ID | Phase | Priority | Status |
|----------------|-------|----------|--------|
| REQ-F001 | 1 | P0 | Not Started |
| REQ-F002 | 1 | P0 | Not Started |
| REQ-F003 | 1 | P0 | Not Started |
| REQ-F004 | 1 | P0 | Not Started |
| REQ-F005 | 1 | P0 | Not Started |
| REQ-F006 | 1 | P1 | Not Started |
| REQ-F007 | 1 | P0 | Not Started |
| REQ-F008 | 1 | P0 | Not Started |
| REQ-F009 | 1 | P0 | Not Started |
| REQ-F010 | 1 | P0 | Not Started |
| REQ-F011 | 1 | P0 | Not Started |
| REQ-F012 | 1 | P0 | Not Started |
| REQ-F013 | 2 | P1 | Not Started |
| REQ-F014 | 1 | P0 | Not Started |
| REQ-F015 | 2 | P1 | Not Started |
| REQ-F016 | 1 | P0 | Not Started |
| REQ-F017 | 2 | P1 | Not Started |
| REQ-F018 | 3 | P1 | Not Started |

---

**Document Status:** Approved  
**Approval Date:** December 5, 2025  
**Next Review:** After Phase 1 completion

**Approved By:**

- Mom (Primary User) - [Signature]
- Project Sponsor - [Signature]
- Technical Lead - [Signature]
