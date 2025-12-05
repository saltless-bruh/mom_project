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
        ┌───────────────────┼───────────────────┐
        │                   │                   │
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

**Data Flow:**

```bash
PDF File → PDFConverter → Images → GeminiClient → 
Raw JSON → ResponseParser → Structured Data → 
ConfidenceScorer → Validated Output
```

**Error Handling:**

- Retry with exponential backoff for API failures
- Fallback to page-by-page processing for large files
- Capture and log all API errors
- Return partial results with warnings

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

**Purpose:** Automate data entry into ACSoft GUI

**Design Pattern:** Command Pattern

**Commands:**

- `ConnectCommand`: Establish connection to ACSoft
- `NavigateCommand`: Navigate to data entry screen
- `FillHeaderCommand`: Fill invoice header fields
- `FillItemsCommand`: Fill line item grid
- `ScreenshotCommand`: Capture audit screenshots
- `VerifyCommand`: Read back and verify entries

**Safety Mechanisms:**

- Screenshot before every action
- Element existence verification
- Action confirmation checks
- Automatic pause on errors
- **No auto-save capability**

### 2.4 FastAPI Backend

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

## 4. Error Handling Design

### 4.1 Error Categories

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
