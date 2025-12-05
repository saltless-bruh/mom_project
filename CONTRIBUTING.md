# Contributing Guidelines

## Mom's Accounting Automation System (MAAS)

Thank you for your interest in contributing to MAAS! This document provides guidelines for contributing to the project.

---

## 🎯 Project Overview

MAAS is an automation system designed to help a Vietnamese accountant reduce manual data entry time by automatically extracting invoice data from PDFs and populating ACSoft accounting software. The primary user is non-technical, so reliability, safety, and ease of use are paramount.

**Key Principles:**

- **User Safety First:** Human review required before final save
- **Data Privacy:** All data remains local
- **Simplicity:** Easy for non-technical users
- **Reliability:** Comprehensive error handling and logging
- **Maintainability:** Clean code, good tests, clear documentation

---

## 🚀 Getting Started

### Prerequisites

**Required:**

- Python 3.9 or higher
- Git
- Windows 10/11 (for ACSoft automation)
- Google Gemini API key

**Recommended:**

- VS Code with Python extension
- PyCharm (alternative IDE)
- Windows Terminal
- Postman (for API testing)

### Development Environment Setup

```bash
# 1. Clone repository
git clone https://github.com/[username]/mom-accounting-automation.git
cd mom-accounting-automation

# 2. Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac (if developing cross-platform components)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Initialize database
python scripts/init_db.py

# 6. Run tests to verify setup
pytest tests/

# 7. Start development server
python run.py
```

### Project Structure

```bash
mom-accounting-automation/
├── app/                    # Application code
│   ├── api/               # FastAPI endpoints
│   ├── services/          # Business logic services
│   ├── models.py          # Pydantic models
│   ├── database.py        # Database configuration
│   └── config.py          # Configuration management
├── frontend/              # Web UI
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Additional documentation
├── .github/               # GitHub templates and workflows
├── data/                  # Runtime data (created automatically)
├── logs/                  # Application logs
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── README.md             # User documentation
```

---

## 📋 How to Contribute

### Types of Contributions

We welcome:

- **Bug fixes** - Fix issues reported in GitHub Issues
- **Feature development** - Implement features from project phases
- **Documentation** - Improve docs, add examples, fix typos
- **Testing** - Add test coverage, improve test quality
- **Code quality** - Refactoring, optimization, cleanup
- **Localization** - Improve Vietnamese language support

### Contribution Workflow

1. **Find or create an issue**
   - Check existing issues for something to work on
   - Create new issue if needed (use templates)
   - Comment on issue to claim it

2. **Fork and branch**
   - Fork the repository (if external contributor)
   - Create feature branch from `develop`
   - Use naming convention: `feature/description` or `bugfix/issue-number-description`

3. **Develop**
   - Write code following style guidelines
   - Add/update tests
   - Update documentation
   - Commit with clear messages

4. **Test**
   - Run full test suite: `pytest tests/`
   - Run linting: `flake8 app/`
   - Format code: `black app/`
   - Check coverage: `pytest --cov=app tests/`

5. **Submit Pull Request**
   - Push branch to your fork
   - Create PR to `develop` branch
   - Fill out PR template completely
   - Link related issues
   - Request review

6. **Address feedback**
   - Respond to review comments
   - Make requested changes
   - Push updates (PR auto-updates)

7. **Celebrate! 🎉**
   - PR gets merged
   - Issue gets closed
   - Your contribution is live!

---

## 💻 Development Guidelines

### Code Style

**Python Style:**

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Maximum line length: 88 characters (Black default)

**Formatting:**

```bash
# Format code
black app/ tests/

# Check linting
flake8 app/ tests/

# Type checking (optional but recommended)
mypy app/
```

**Type Hints:**

```python
# Always use type hints
def process_invoice(pdf_path: str, config: dict) -> Invoice:
    """Process invoice PDF and return Invoice object.
    
    Args:
        pdf_path: Absolute path to PDF file
        config: Configuration dictionary
        
    Returns:
        Invoice object with extracted data
        
    Raises:
        PDFProcessingError: If PDF cannot be processed
    """
    pass
```

**Docstrings:**

```python
# Use Google-style docstrings
def calculate_tax(amount: float, rate: float) -> float:
    """Calculate tax amount.
    
    Args:
        amount: Base amount for tax calculation
        rate: Tax rate as decimal (e.g., 0.10 for 10%)
        
    Returns:
        Calculated tax amount
        
    Example:
        >>> calculate_tax(100000, 0.10)
        10000.0
    """
    return amount * rate
```

**Naming Conventions:**

```python
# Module names: lowercase with underscores
# gemini_client.py, pdf_processor.py

# Class names: PascalCase
class InvoiceProcessor:
    pass

# Function and variable names: snake_case
def extract_invoice_data(pdf_path):
    invoice_date = "2025-12-05"
    
# Constants: UPPER_SNAKE_CASE
API_TIMEOUT_SECONDS = 30
MAX_RETRY_ATTEMPTS = 3

# Private methods: leading underscore
def _internal_helper():
    pass
```

### Testing Guidelines

**Test Structure:**

```python
# tests/test_validator.py
import pytest
from app.services.validator import validate_invoice_data

class TestInvoiceValidation:
    """Test suite for invoice validation."""
    
    def test_valid_invoice_passes(self):
        """Test that valid invoice data passes validation."""
        data = {
            "vendor_name": "ABC Supplier",
            "invoice_number": "INV-001",
            "invoice_date": "2025-12-05",
            "total_amount": 100000
        }
        result = validate_invoice_data(data)
        assert result["is_valid"] is True
        
    def test_missing_required_field_fails(self):
        """Test that missing required field fails validation."""
        data = {"vendor_name": "ABC Supplier"}
        result = validate_invoice_data(data)
        assert result["is_valid"] is False
        assert "invoice_number" in str(result["errors"])
        
    @pytest.mark.parametrize("tax_rate", [0, 5, 8, 10])
    def test_valid_tax_rates(self, tax_rate):
        """Test that valid tax rates are accepted."""
        # Test implementation
        pass
```

**Test Coverage:**

- Aim for 80%+ coverage
- All critical paths must be tested
- Test both success and error cases
- Test edge cases and boundary conditions

**Running Tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_validator.py

# Run specific test
pytest tests/test_validator.py::TestInvoiceValidation::test_valid_invoice_passes

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

### Git Commit Guidelines

**Commit Message Format:**

```bash
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code formatting (no logic change)
- `refactor` - Code refactoring
- `test` - Adding/updating tests
- `chore` - Maintenance tasks

**Examples:**

```bash
# Simple commit
git commit -m "feat(extraction): Add Gemini API integration"

# Detailed commit
git commit -m "fix(validation): Correct tax calculation for multi-rate invoices

Previous logic assumed single tax rate per invoice. Now correctly
handles line items with different tax rates (0%, 5%, 8%, 10%).

- Added per-item tax rate validation
- Updated calculation verification
- Added test cases for mixed tax rates

Fixes #156"
```

### Documentation Standards

**README.md:**

- User-facing documentation
- Installation instructions
- Usage examples
- Troubleshooting guide

**TECHNICAL_SPECS.md:**

- System architecture
- Component specifications
- API documentation
- Database schema

**Inline Comments:**

```python
# Use comments to explain WHY, not WHAT
# Good:
# Convert to VND since Gemini returns amounts with decimals
amount = int(float(amount_str))

# Bad:
# Convert amount to integer
amount = int(float(amount_str))
```

**API Documentation:**

- FastAPI auto-generates docs at `/docs`
- Ensure all endpoints have clear descriptions
- Document request/response schemas
- Provide example payloads

---

## 🧪 Testing Strategy

### Test Types

**Unit Tests:**

- Test individual functions/methods
- Mock external dependencies
- Fast execution
- High coverage

**Integration Tests:**

- Test component interactions
- Test API endpoints
- Test database operations
- Use test database

**End-to-End Tests:**

- Test complete workflows
- Upload PDF → Extract → Validate → Automate
- Use real (anonymized) sample data
- Slower but comprehensive

**Manual Testing:**

- Test with real ACSoft software
- Test with diverse invoice formats
- User acceptance testing with mom
- Exploratory testing

### Test Data

**Sample Invoices:**

- Store in `tests/fixtures/`
- Anonymize sensitive data
- Include diverse formats
- Document characteristics

```python
# tests/fixtures/README.md
# Test Invoice Descriptions

## invoice_standard.pdf
- Single page
- Standard format
- 5 line items
- Single tax rate (10%)
- VND currency

## invoice_multipage.pdf
- 3 pages
- 20 line items
- Mixed tax rates
- Includes discount

## invoice_handwritten.pdf
- Poor scan quality
- Handwritten notes
- Low confidence expected
```

**Test Database:**

```python
# tests/conftest.py
import pytest
from app.database import engine, Base

@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
```

---

## 🔍 Code Review Guidelines

### For Authors

**Before Requesting Review:**

- [ ] All tests pass
- [ ] Code is formatted (black)
- [ ] Linting passes (flake8)
- [ ] Documentation updated
- [ ] Self-review completed
- [ ] PR template filled out

**Responding to Reviews:**

- Be open to feedback
- Ask questions if unclear
- Explain design decisions
- Make requested changes promptly
- Mark conversations as resolved

### For Reviewers

**What to Check:**

- Functionality works as intended
- Code follows style guidelines
- Tests are comprehensive
- Documentation is clear
- No security issues
- Performance is acceptable

**Review Checklist:**

- [ ] Code is readable and maintainable
- [ ] Logic is correct and handles edge cases
- [ ] Error handling is comprehensive
- [ ] No hardcoded values
- [ ] No sensitive data exposed
- [ ] Tests cover new functionality
- [ ] Documentation is updated

**Providing Feedback:**

- Be constructive and specific
- Explain the "why" behind suggestions
- Distinguish between required changes and suggestions
- Acknowledge good work
- Use GitHub's suggestion feature

**Comment Types:**

```markdown
<!-- Required change -->
**Required:** This will cause a bug when invoice_date is None.
Please add null check.

<!-- Suggestion -->
**Suggestion:** Consider extracting this logic into a separate
function for better testability.

<!-- Question -->
**Question:** Why use this approach instead of X?

<!-- Praise -->
**Nice!** Good use of context managers here.
```

---

## 🐛 Bug Reporting

### How to Report Bugs

1. **Check existing issues** - Bug may already be reported
2. **Use bug report template** - Provides necessary structure
3. **Provide reproduction steps** - Clear steps to reproduce
4. **Include environment details** - OS, Python version, etc.
5. **Attach logs/screenshots** - Visual proof helps
6. **Anonymize sensitive data** - Remove vendor names, amounts

### Good Bug Report Example

```markdown
**Title:** [BUG] Gemini API timeout with large multi-page PDFs

**Description:**
When processing invoices with more than 10 pages, the Gemini API
call times out after 30 seconds, causing the extraction to fail.

**Steps to Reproduce:**
1. Upload invoice_large.pdf (15 pages)
2. Click "Process Invoice"
3. Wait 30 seconds
4. Error appears: "Gemini API timeout"

**Expected Behavior:**
Invoice should be processed successfully, even if it takes longer.

**Actual Behavior:**
Error after 30 seconds with no retry attempted.

**Environment:**
- OS: Windows 11
- Python: 3.9.7
- MAAS Version: 1.0.0

**Error Logs:**
```

2025-12-05 10:30:00 | ERROR | gemini_client | Request timeout after 30s

```bash

**Suggested Fix:**
Increase API_TIMEOUT to 60 seconds or add retry logic.
```

---

## ✨ Feature Requests

### How to Request Features

1. **Check existing requests** - May already exist
2. **Use feature request template** - Provides structure
3. **Explain the use case** - Why is this needed?
4. **Describe expected behavior** - What should happen?
5. **Consider alternatives** - Are there other approaches?
6. **Indicate priority** - How important is this?

### Good Feature Request Example

```markdown
**Title:** [FEATURE] Automatic email import of invoices

**Use Case:**
As mom, I want to automatically import invoices from email
attachments so that I don't have to manually download PDFs.

**Problem Statement:**
Currently, mom receives 50+ invoices per day via email. She
manually downloads each PDF before uploading to MAAS. This adds
5-10 minutes to her workflow.

**Proposed Solution:**
Add email integration that:
1. Connects to mom's email (IMAP)
2. Searches for emails with PDF attachments
3. Downloads invoices automatically
4. Queues them for processing

**Alternatives Considered:**
- Option A: Manual download (current state) - Pro: Simple, Con: Time-consuming
- Option B: Email forwarding rule - Pro: Easy setup, Con: Still manual
- Option C: Full email integration - Pro: Fully automated, Con: Complex

**Acceptance Criteria:**
- [ ] Connect to IMAP email account
- [ ] Search for invoices by sender/subject
- [ ] Download PDF attachments
- [ ] Auto-queue for processing
- [ ] Track which emails have been processed

**Priority:**
- [x] High (significant time savings)

**Additional Context:**
Most suppliers send invoices with consistent subject lines like
"Invoice INV-12345" which could be used for filtering.
```

---

## 🎯 Issue Labels Guide

### Using Labels Effectively

**Priority Labels:**

- `critical` - System is broken, needs immediate fix
- `high` - Important functionality affected
- `medium` - Standard priority
- `low` - Nice to have, not urgent

**Type Labels:**

- `bug` - Something isn't working
- `enhancement` - New feature or improvement
- `task` - Implementation task
- `documentation` - Docs improvements
- `question` - Further information needed

**Phase Labels:**

- `phase-1` - MVP (Weeks 1-2)
- `phase-2` - Enhancement (Week 3)
- `phase-3` - Polish (Week 4)
- `post-launch` - Future enhancements

**Component Labels:**

- `backend` - Backend/API code
- `frontend` - UI code
- `extraction` - PDF/Gemini extraction
- `validation` - Data validation
- `automation` - ACSoft automation
- `database` - Database-related
- `testing` - Test-related

**Status Labels:**

- `help-wanted` - Open for contributions
- `good-first-issue` - Good for newcomers
- `blocked` - Blocked by dependency
- `wontfix` - Will not be implemented
- `duplicate` - Duplicate of another issue

---

## 📝 Documentation Contributions

### Types of Documentation

**User Documentation (README.md):**

- Installation guide
- Usage instructions
- Troubleshooting
- FAQ

**Developer Documentation:**

- Architecture overview
- API reference
- Development setup
- Contributing guide

**Code Documentation:**

- Docstrings
- Inline comments
- Type hints
- Examples

### Documentation Standards

**Writing Style:**

- Clear and concise
- Use active voice
- Provide examples
- Assume non-technical audience (for user docs)

**Formatting:**

- Use proper Markdown syntax
- Include code blocks with syntax highlighting
- Add screenshots where helpful
- Link to related documentation

**Example:**

````markdown
## Installing Dependencies

Install all required Python packages using pip:

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI - Web framework
- Gemini API client - For invoice extraction
- PyWinAuto - For ACSoft automation
- And other dependencies

**Note:** Make sure you're using Python 3.9 or higher:
```bash
python --version
```
````

---

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on the issue, not the person
- Respect different viewpoints
- Be patient and helpful

### Communication Channels

**GitHub Issues:**

- Bug reports
- Feature requests
- Technical discussions

**Pull Requests:**

- Code review
- Implementation discussions
- Technical questions

**Email:**

- Private concerns
- Security issues
- Project inquiries

### Getting Help

**For Development Questions:**

1. Check documentation (README, TECHNICAL_SPECS, AI_AGENT_INSTRUCTIONS)
2. Search existing issues
3. Ask in issue comments
4. Create new issue with "question" label

**For Bug Reports:**

1. Verify it's actually a bug
2. Check if already reported
3. Create bug report with full details

---

## 🎓 Learning Resources

### For Contributors

**Python:**

- [Real Python](https://realpython.com/)
- [Python Documentation](https://docs.python.org/)
- [PEP 8 Style Guide](https://pep8.org/)

**FastAPI:**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

**Testing:**

- [Pytest Documentation](https://docs.pytest.org/)
- [Test Driven Development](https://www.obeythetestinggoat.com/)

**Git:**

- [Pro Git Book](https://git-scm.com/book/en/v2)
- [GitHub Docs](https://docs.github.com/)

**Project-Specific:**

- [TECHNICAL_SPECS.md](TECHNICAL_SPECS.md)
- [AI_AGENT_INSTRUCTIONS.md](.github/AI_AGENT_INSTRUCTIONS.md)
- [GITHUB_WORKFLOW.md](.github/GITHUB_WORKFLOW.md)

---

## 📜 License

This project is developed for private family use. Please respect the intellectual property and privacy of the codebase.

---

## 🙏 Acknowledgments

Thank you for contributing to MAAS! Your efforts help make mom's daily work easier and give her more time for family. Every contribution, no matter how small, is appreciated.

**Special Thanks To:**

- Contributors who submit bug fixes
- Developers who add features
- Reviewers who improve code quality
- Documentation writers
- Testers who find edge cases

---

## 📞 Contact

**For Questions or Concerns:**

- Create an issue with "question" label
- Email: [project maintainer email]

**For Security Issues:**

- Do NOT create public issue
- Email directly: [security contact email]

---

**Last Updated:** December 5, 2025  
**Version:** 1.0
