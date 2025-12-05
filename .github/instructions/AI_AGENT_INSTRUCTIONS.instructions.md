# AI Agent Development Instructions
## Mom's Accounting Automation System (MAAS)

**Project Repository:** mom-accounting-automation  
**Target User:** Mom (non-technical accountant)  
**Primary Goal:** Automate invoice data entry into ACSoft software

---

## 🎯 Project Context

You are developing an automation system to help a Vietnamese accountant who manually enters 50-100 invoices per day into ACSoft accounting software. This currently takes 4-6 hours daily. The system should:

1. Extract data from Vietnamese PDF invoices using Gemini 2.0 Flash API
2. Validate and normalize the extracted data
3. Automate ACSoft GUI to fill in the form fields
4. Allow human review before final save (safety feature)
5. Maintain audit trail of all operations

**Critical Success Factor:** The system must save mom 3-5 hours per day while maintaining 95%+ accuracy and safety.

---

## 📋 Development Workflow

### Phase 1: MVP (Weeks 1-2)
**Objective:** Prove concept with one supplier's invoice format

#### Task Checklist:
- [ ] Set up project structure (see TECHNICAL_SPECS.md Appendix B)
- [ ] Implement Gemini API integration for PDF extraction
- [ ] Create data validation service with calculation verification
- [ ] Build SQLite database with schema from specs
- [ ] Develop FastAPI backend with core endpoints
- [ ] Create simple HTML upload interface
- [ ] Implement PyWinAuto script for ACSoft (manual testing)
- [ ] Add comprehensive error handling
- [ ] Write unit tests for all services
- [ ] Test end-to-end with 5-10 sample invoices from primary supplier
- [ ] Document any issues or edge cases discovered

**Success Criteria:**
- Successfully extract data from primary supplier's invoices with 90%+ accuracy
- Validate and normalize extracted data correctly
- Store invoice data in database
- Manual PyWinAuto script can fill ACSoft form (even if not fully integrated)

### Phase 2: Enhancement (Week 3)
**Objective:** Support multiple invoice formats and improve robustness

#### Task Checklist:
- [ ] Collect sample invoices from all regular suppliers (at least 5 different formats)
- [ ] Enhance Gemini prompts to handle diverse invoice layouts
- [ ] Implement vendor-specific extraction rules (if needed)
- [ ] Build comprehensive validation rules for Vietnamese invoices
- [ ] Integrate PyWinAuto automation with FastAPI backend
- [ ] Add screenshot capture for audit trail
- [ ] Implement error recovery mechanisms
- [ ] Create monitoring dashboard (simple UI showing processing status)
- [ ] Add logging system with rotation
- [ ] Conduct integration testing with 20-30 invoices

**Success Criteria:**
- Handle 5+ different invoice formats accurately
- End-to-end automation (upload → extract → validate → automate → review)
- Error rate < 5%
- Processing time < 2 minutes per invoice

### Phase 3: Polish & Production (Week 4)
**Objective:** Production-ready system with documentation

#### Task Checklist:
- [ ] Optimize Gemini API calls (caching, batching if applicable)
- [ ] Fine-tune validation rules based on testing
- [ ] Create user manual for mom (with screenshots)
- [ ] Document troubleshooting procedures
- [ ] Set up automated daily database backups
- [ ] Create configuration management system
- [ ] Build admin interface for updating vendor mappings
- [ ] Performance testing with high-volume scenarios
- [ ] Security review (local data protection)
- [ ] User acceptance testing with mom (10-20 real invoices)
- [ ] Create deployment script and Task Scheduler setup

**Success Criteria:**
- Mom can operate system independently
- System handles daily workload (50-100 invoices)
- Comprehensive documentation exists
- Automated backups working
- No critical bugs remaining

---

## 🛠️ Technical Guidelines

### Code Style & Standards

**Python Code:**
```python
# Use type hints
def extract_invoice_data(pdf_path: str) -> dict:
    """Extract structured data from invoice PDF.
    
    Args:
        pdf_path: Absolute path to PDF file
        
    Returns:
        Dictionary containing extracted invoice data
        
    Raises:
        PDFProcessingError: If PDF cannot be processed
        GeminiAPIError: If API call fails
    """
    pass

# Use dataclasses/Pydantic for data structures
from pydantic import BaseModel

class InvoiceItem(BaseModel):
    line_number: int
    description: str
    quantity: float
    # ... etc

# Proper error handling
try:
    result = gemini_client.extract(pdf_path)
except GeminiAPIError as e:
    logger.error(f"Gemini API failed: {e}")
    raise
```

**Naming Conventions:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Database tables: `snake_case`

**Documentation:**
- Every module has docstring explaining purpose
- Every public function has docstring with Args/Returns/Raises
- Complex logic has inline comments
- README.md for user-facing documentation
- TECHNICAL_SPECS.md for developer reference

### Git Workflow

**Branch Strategy:**
```
main (production-ready code)
├── develop (integration branch)
├── feature/gemini-extraction
├── feature/acsoft-automation
├── feature/validation-service
└── bugfix/issue-123
```

**Commit Messages:**
```
feat: Add Gemini API integration for invoice extraction
fix: Correct tax calculation validation logic
docs: Update user manual with troubleshooting section
test: Add unit tests for PDF processor
refactor: Simplify validation error handling
```

**Before Committing:**
1. Run tests: `pytest tests/`
2. Check linting: `flake8 app/`
3. Format code: `black app/`
4. Update CHANGELOG.md if user-facing change

### Testing Strategy

**Unit Tests (pytest):**
```python
# tests/test_validator.py
import pytest
from app.services.validator import validate_invoice_data

def test_validate_complete_invoice():
    """Test validation of complete invoice data"""
    data = {
        "vendor_name": "ABC Supplier",
        "invoice_number": "INV-001",
        "invoice_date": "2025-12-05",
        "items": [{"description": "Item 1", "total": 100000}],
        "total_amount": 100000
    }
    result = validate_invoice_data(data)
    assert result["is_valid"] is True
    assert len(result["errors"]) == 0

def test_validate_missing_required_field():
    """Test validation catches missing required fields"""
    data = {"vendor_name": "ABC Supplier"}  # Missing invoice_number
    result = validate_invoice_data(data)
    assert result["is_valid"] is False
    assert any("invoice_number" in err["field"] for err in result["errors"])
```

**Integration Tests:**
```python
# tests/test_integration.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_and_extract_invoice():
    """Test full upload and extraction workflow"""
    with open("tests/fixtures/sample_invoice.pdf", "rb") as f:
        response = client.post(
            "/api/invoices/upload",
            files={"file": ("invoice.pdf", f, "application/pdf")}
        )
    assert response.status_code == 200
    invoice_id = response.json()["invoice_id"]
    
    # Check extraction results
    response = client.get(f"/api/invoices/{invoice_id}/extraction")
    assert response.status_code == 200
    assert "vendor_name" in response.json()["data"]
```

**Test Data:**
- Store sample invoices in `tests/fixtures/`
- Include diverse formats (different vendors, layouts, edge cases)
- Anonymize sensitive data (vendor names, amounts)
- Document each test file's characteristics

### Logging Standards

```python
import logging
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Log levels:
logger.debug("Detailed diagnostic information")  # Development only
logger.info("Normal operation events")           # General flow
logger.warning("Unexpected but handled situation")  # Potential issues
logger.error("Error that prevented operation")   # Failures
logger.critical("System-level failure")          # Requires immediate attention

# Include context in logs:
logger.info(f"Processing invoice {invoice_id} for vendor {vendor_name}")
logger.error(f"Gemini API failed for {pdf_path}: {error_message}", exc_info=True)
```

**Log Format:**
```
2025-12-05 10:30:15,123 | INFO | pdf_processor | Processing invoice.pdf
2025-12-05 10:30:18,456 | WARNING | validator | Low confidence (0.82) for INV-001
2025-12-05 10:30:20,789 | ERROR | acsoft_automation | Element not found: txtVendorName
```

### Configuration Management

**Environment Variables (.env):**
```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Optional (have defaults)
DATABASE_PATH=./data/maas.db
LOG_LEVEL=INFO
ENVIRONMENT=production
ACSOFT_PATH=C:\Program Files\ACSoft\ACSoft.exe
```

**Configuration File (config.yaml):**
- See TECHNICAL_SPECS.md Section 3 for full schema
- Load with `pyyaml`
- Validate on startup
- Allow override with environment variables

**Secrets Management:**
- NEVER commit `.env` file to git
- Provide `.env.example` template
- API keys only in environment variables
- Log sanitization (mask sensitive data)

---

## 🔍 Code Review Checklist

Before submitting code for review or merging:

### Functionality
- [ ] Code works as intended and meets requirements
- [ ] All edge cases handled (empty fields, malformed data, API failures)
- [ ] Error messages are clear and actionable
- [ ] No hardcoded values (use config instead)

### Code Quality
- [ ] Functions are single-purpose and small (< 50 lines)
- [ ] Type hints used for all function signatures
- [ ] Docstrings for all public functions/classes
- [ ] No duplicate code (DRY principle)
- [ ] Proper separation of concerns (see file structure)

### Testing
- [ ] Unit tests written for new functions
- [ ] Tests cover happy path and error cases
- [ ] Integration tests for API endpoints
- [ ] Test coverage > 80% for new code
- [ ] All tests pass (`pytest tests/`)

### Security
- [ ] No sensitive data in logs
- [ ] Input validation for all user inputs
- [ ] SQL injection prevention (use parameterized queries)
- [ ] File upload validation (type, size, content)
- [ ] No secrets in code (use environment variables)

### Documentation
- [ ] README.md updated if user-facing changes
- [ ] TECHNICAL_SPECS.md updated if architecture changes
- [ ] CHANGELOG.md entry added
- [ ] Inline comments for complex logic
- [ ] API endpoint documented (FastAPI auto-docs)

### Performance
- [ ] No N+1 query problems
- [ ] Efficient algorithms (no unnecessary loops)
- [ ] Database indexes used appropriately
- [ ] Files closed properly (use context managers)
- [ ] API calls minimized (caching where appropriate)

---

## 🚨 Common Pitfalls to Avoid

### 1. Gemini API Issues
**Problem:** API rate limits or timeouts  
**Solution:** 
- Implement exponential backoff retry logic
- Cache extraction results in database
- Monitor API costs daily
- Handle 503 errors gracefully

### 2. ACSoft Automation Brittleness
**Problem:** UI elements change or aren't found  
**Solution:**
- Use multiple locators (auto_id, name, class)
- Implement fallback to PyAutoGUI with image recognition
- Take screenshots before each action (debugging)
- Add detailed error messages with element context

### 3. Data Validation Edge Cases
**Problem:** Unusual invoice formats break validation  
**Solution:**
- Collect diverse sample invoices upfront
- Make validation rules configurable
- Log all validation warnings for review
- Allow manual override with confirmation

### 4. Vietnamese Text Encoding
**Problem:** Garbled Vietnamese characters  
**Solution:**
- Use UTF-8 everywhere (`# -*- coding: utf-8 -*-`)
- Ensure database uses UTF-8 collation
- Test with invoices containing Vietnamese text
- Normalize Unicode characters (NFC)

### 5. File System Issues
**Problem:** Path separators differ on Windows  
**Solution:**
- Use `pathlib.Path` instead of string concatenation
- Use `os.path.join()` for cross-platform compatibility
- Always use absolute paths
- Handle Windows long path issues (> 260 chars)

### 6. Database Locking
**Problem:** SQLite locks when accessed concurrently  
**Solution:**
- Use single worker (no concurrency for MVP)
- Enable WAL mode: `PRAGMA journal_mode=WAL`
- Proper transaction management
- Short-lived connections

### 7. Memory Leaks
**Problem:** Large PDFs consume too much memory  
**Solution:**
- Process PDFs page by page
- Close file handles properly (`with` statements)
- Clear image buffers after processing
- Monitor memory usage in logs

### 8. Error Recovery
**Problem:** System stuck in inconsistent state after error  
**Solution:**
- Use database transactions (rollback on error)
- Status field in database tracks progress
- Resume functionality for interrupted processing
- Clear error states with manual reset button

---

## 📊 Monitoring & Debugging

### Key Metrics to Track
```python
# In code, log these metrics:
metrics = {
    "invoice_id": str,
    "processing_time_ms": int,
    "extraction_confidence": float,
    "validation_errors": int,
    "manual_corrections": int,
    "automation_success": bool,
    "gemini_api_cost_usd": float
}
```

### Daily Monitoring Checklist
- [ ] Check logs for errors: `tail -f logs/maas.log`
- [ ] Review invoices with low confidence (< 0.85)
- [ ] Check Gemini API costs
- [ ] Verify backups completed successfully
- [ ] Check disk space in `data/` directory
- [ ] Review processing times (should be < 2 min per invoice)

### Debugging Tips
**When extraction fails:**
1. Check PDF is valid: `pdfinfo invoice.pdf`
2. Verify Gemini API key: `echo $GEMINI_API_KEY`
3. Review Gemini response in logs
4. Test with simpler invoice (single page, clear text)

**When validation fails:**
1. Print extracted data: `logger.debug(json.dumps(data, indent=2))`
2. Check validation rules match invoice format
3. Verify calculations manually
4. Look for missing fields in extraction

**When ACSoft automation fails:**
1. Check ACSoft is running: Task Manager
2. Verify element locators: `pywinauto.findwindows.find_elements()`
3. Take screenshot: `automation.take_screenshot("debug")`
4. Test automation step-by-step manually
5. Check Windows UI Automation is enabled

---

## 🤝 Communication & Collaboration

### Issue Reporting Template
```markdown
**Title:** [BUG] Short description

**Description:**
Clear description of the issue

**Steps to Reproduce:**
1. Upload invoice ABC.pdf
2. Click "Process"
3. Error appears

**Expected Behavior:**
Invoice should be extracted successfully

**Actual Behavior:**
Error: "Gemini API timeout"

**Environment:**
- Windows 11
- Python 3.9.7
- MAAS version 1.0.0

**Logs:**
```
2025-12-05 10:30:00 | ERROR | gemini_client | Request timeout after 30s
```

**Screenshots:**
[Attach if relevant]
```

### Feature Request Template
```markdown
**Title:** [FEATURE] Short description

**Use Case:**
Mom needs to [specific need]

**Proposed Solution:**
Add [specific feature] that allows [benefit]

**Alternatives Considered:**
- Option A: [pros/cons]
- Option B: [pros/cons]

**Priority:**
- [ ] Critical (blocks daily work)
- [ ] High (significant time savings)
- [ ] Medium (nice to have)
- [ ] Low (future enhancement)
```

### Pull Request Template
```markdown
**Title:** feat: Add Gemini API integration

**Description:**
Implements PDF invoice extraction using Gemini 2.0 Flash API.

**Changes:**
- Added `gemini_client.py` service
- Implemented retry logic with exponential backoff
- Added unit tests for API client
- Updated requirements.txt with google-generativeai

**Testing:**
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Tested with 10 sample invoices
- [x] API cost tracking verified

**Screenshots/Logs:**
[If UI changes or debugging needed]

**Checklist:**
- [x] Code follows style guidelines
- [x] Documentation updated
- [x] Tests added/updated
- [x] No breaking changes
```

---

## 🎓 Learning Resources

### Python Best Practices
- [PEP 8 Style Guide](https://pep8.org/)
- [Real Python Tutorials](https://realpython.com/)
- [Effective Python by Brett Slatkin](https://effectivepython.com/)

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Full Stack FastAPI Template](https://github.com/tiangolo/full-stack-fastapi-postgresql)

### PyWinAuto
- [Getting Started Guide](https://pywinauto.readthedocs.io/en/latest/getting_started.html)
- [UI Automation Examples](https://github.com/pywinauto/pywinauto/tree/master/examples)

### Gemini API
- [API Documentation](https://ai.google.dev/docs)
- [Gemini Vision Examples](https://ai.google.dev/tutorials/python_quickstart)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

---

## 🔐 Security & Privacy Guidelines

### Data Handling Rules
1. **PDFs stay local:** Never upload to third-party services (except Gemini)
2. **Database encryption:** Consider SQLCipher for production
3. **API keys:** Environment variables only, never in code
4. **Logs:** Sanitize sensitive data (amounts, vendor names)
5. **Backups:** Encrypted and stored locally only

### GDPR Considerations (if applicable)
- Vendor data is business data, not personal data
- Retain invoices per tax law requirements (typically 7 years)
- No data shared with third parties
- Mom has full control and ownership

### Audit Trail
- Log all operations with timestamps
- Store screenshots for verification
- Track who made manual corrections (if multi-user in future)
- Retention period: 1 year minimum

---

## 📦 Deployment Checklist

### Pre-Deployment
- [ ] All tests pass (unit + integration + UAT)
- [ ] Performance meets requirements (< 2 min per invoice)
- [ ] User manual completed and reviewed by mom
- [ ] Backup system tested and working
- [ ] Error handling verified with edge cases
- [ ] Gemini API key configured in production

### Deployment Steps
1. Clone repository to mom's computer
2. Install Python 3.9+ and dependencies
3. Configure `.env` file with API keys
4. Initialize database: `python scripts/init_db.py`
5. Run smoke tests: `pytest tests/smoke/`
6. Start application: `python run.py`
7. Set up Task Scheduler for auto-start
8. Configure daily backup cron job
9. Test with 2-3 real invoices with mom present
10. Monitor logs for first week

### Post-Deployment
- [ ] Monitor daily for first week
- [ ] Collect mom's feedback
- [ ] Track metrics (time saved, accuracy, errors)
- [ ] Address any issues immediately
- [ ] Schedule weekly check-ins for first month

---

## 🎯 Success Metrics

### Quantitative
- **Time savings:** 80%+ reduction (from 4-6 hours to < 1 hour per day)
- **Accuracy:** 95%+ extraction accuracy
- **Automation success:** 98%+ forms filled without errors
- **Processing time:** < 2 minutes per invoice
- **Error rate:** < 1% requiring manual correction
- **Uptime:** 99%+ (system operational when needed)

### Qualitative
- Mom finds system easy to use
- Mom trusts automated data extraction
- Reduced physical strain (less typing)
- More time for family responsibilities
- Positive impact on work-life balance

### Business Impact
- Increased capacity (can take on more clients)
- Reduced errors in accounting records
- Better audit trail and compliance
- Lower stress and improved job satisfaction

---

## 📞 Support & Troubleshooting

### Common Issues & Solutions

**Issue:** "Gemini API key invalid"  
**Solution:** Verify API key in `.env`, regenerate if needed

**Issue:** "Cannot connect to ACSoft"  
**Solution:** Ensure ACSoft is running, check window title matches config

**Issue:** "Invoice extraction confidence too low"  
**Solution:** Check PDF quality, may need manual review

**Issue:** "Database locked"  
**Solution:** Close other connections, restart application

**Issue:** "Disk space low"  
**Solution:** Archive old invoices, clean up screenshots > 30 days

### Getting Help
1. Check logs: `logs/maas.log`
2. Review TECHNICAL_SPECS.md for architecture details
3. Search existing GitHub issues
4. Create new issue with full context (see template above)
5. For urgent issues: Direct communication with developer

---

## 🚀 Quick Start for AI Agent

**When starting a new feature:**
1. Read relevant section of TECHNICAL_SPECS.md
2. Check existing code structure and patterns
3. Write tests first (TDD approach)
4. Implement feature incrementally
5. Run tests frequently (`pytest tests/`)
6. Update documentation as you go
7. Create PR with clear description

**When debugging an issue:**
1. Reproduce the issue locally
2. Check logs for error details
3. Add debug logging if needed
4. Write test that captures the bug
5. Fix the code
6. Verify test passes
7. Add regression test

**When reviewing code:**
1. Use checklist above (Code Review Checklist)
2. Run tests locally
3. Check documentation completeness
4. Test edge cases manually
5. Verify follows project conventions

---

## 📚 Documentation Organization

### Documentation Structure

**All documentation MUST be created in the `docs/` folder.**

### Folder Organization

**`docs/api/`** - API Documentation
- API endpoint reference
- Request/response schemas
- Authentication details
- API usage examples

**`docs/user/`** - User Documentation
- Installation guide
- User manual
- Workflow guide
- Troubleshooting guide
- FAQ

**`docs/developer/`** - Developer Documentation
- Code structure
- Setup guide
- Coding standards
- Design patterns
- Database guide
- Contributing guide

**`docs/architecture/`** - Architecture Documentation
- System overview
- Component design
- Data flow diagrams
- Integration points
- Design decisions (ADRs)
- Security architecture

**`docs/deployment/`** - Deployment Documentation
- Deployment guide
- Configuration guide
- Environment setup
- Backup/restore procedures
- Maintenance guide
- Monitoring setup

**`docs/testing/`** - Testing Documentation
- Test plan (`test_plan.md`)
- Coverage requirements (`coverage_requirements.md`)
- Test data documentation (`test_data.md`)
- Subdirectories:
  - `unit/` - Unit test docs
  - `integration/` - Integration test docs
  - `e2e/` - End-to-end test docs
  - `fixtures/` - Test fixture docs
  - `strategies/` - Testing strategies

### When to Create Documentation

**User-facing changes:**
→ Create in `docs/user/`

**API changes:**
→ Create in `docs/api/`

**Code architecture changes:**
→ Create in `docs/architecture/`

**Deployment process changes:**
→ Create in `docs/deployment/`

**Testing changes:**
→ Create in `docs/testing/`

**Developer guides:**
→ Create in `docs/developer/`

### Documentation Standards

1. **Always use Markdown (.md) format**
2. **Use clear, descriptive filenames:** `installation_guide.md` not `install.md`
3. **Include frontmatter (optional):**
   ```markdown
   ---
   title: Installation Guide
   description: Complete installation instructions
   last_updated: 2025-12-05
   ---
   ```
4. **Structure documents consistently:**
   - Title and purpose
   - Table of contents (for long docs)
   - Clear headings and sections
   - Examples and screenshots
   - Troubleshooting section

5. **Link between documents:**
   - Use relative links: `[API Docs](../api/endpoints.md)`
   - Keep links up-to-date

6. **Update `docs/README.md`:**
   - Add new documentation types
   - Update Quick Lookup Guide
   - Keep structure current

### Quick Lookup

See `docs/README.md` for:
- Complete folder structure
- Quick lookup guide ("How do I...?")
- Documentation guidelines
- Current status

---

## 📝 Additional Notes

### Vietnamese Language Support
- All UI text should support Vietnamese
- Use Unicode (UTF-8) throughout
- Test with Vietnamese invoice data
- Gemini 2.0 Flash has excellent Vietnamese OCR

### ACSoft Integration Notes
- ACSoft is Windows-only (no Linux/Mac version)
- UI automation requires Windows UI Automation enabled
- Some ACSoft versions may have different element IDs
- Test with mom's specific ACSoft version

### Scalability Considerations (Future)
- Current design: single user, sequential processing
- Future: Could support multiple users with authentication
- Future: Could add queue-based processing for high volume
- Future: Could add caching layer (Redis) if needed

---

## ✅ Ready to Start?

You now have comprehensive instructions to develop MAAS. Key principles:

1. **User-centric:** Mom's needs come first
2. **Safety:** Human review before final save
3. **Reliability:** Comprehensive error handling and logging
4. **Maintainability:** Clean code, good tests, clear documentation
5. **Privacy:** All data stays local

**Next Steps:**
1. Set up development environment
2. Implement Phase 1 (MVP) tasks
3. Test with real invoices
4. Iterate based on feedback

Good luck! 🎉

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Maintained By:** Development Team
