# Test Coverage Requirements

## Mom's Accounting Automation System (MAAS)

**Version:** 1.0  
**Last Updated:** December 5, 2025

---

## Overview

This document defines test coverage requirements for the MAAS project to ensure code quality and reliability.

---

## Coverage Targets

### Overall Coverage

- **Minimum:** 80% overall code coverage
- **Target:** 85%+ overall code coverage
- **Critical paths:** 100% coverage required

### Component-Specific Coverage

| Component | Minimum Coverage | Target Coverage | Priority |
|-----------|-----------------|-----------------|----------|
| PDF Processor | 85% | 90%+ | High |
| Validator | 90% | 95%+ | Critical |
| Database Layer | 80% | 85%+ | High |
| API Endpoints | 80% | 85%+ | High |
| ACSoft Automation | 70% | 75%+ | Medium* |
| Utilities | 75% | 80%+ | Medium |

**Note:** *ACSoft automation has lower target due to GUI testing complexity. Manual testing supplements automated tests.

---

## Coverage Measurement

### Tools

- **pytest-cov:** Primary coverage tool
- **Coverage.py:** Underlying coverage engine
- **Reports:** HTML and terminal output

### Running Coverage

```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# View HTML report
open htmlcov/index.html

# Generate coverage badge (future)
coverage-badge -o coverage.svg
```

---

## Coverage Requirements by Test Type

### Unit Tests

- **Target:** 80%+ coverage
- **Focus:** Individual functions and methods
- **Exclusions:**
  - Configuration files
  - `__init__.py` files
  - Main entry points

### Integration Tests

- **Target:** 70%+ coverage
- **Focus:** Component interactions
- **Includes:**
  - API endpoint workflows
  - Database operations
  - Service interactions

### End-to-End Tests

- **Target:** 60%+ critical path coverage
- **Focus:** Complete workflows
- **Includes:**
  - Upload → Extract → Validate → Automate

---

## Critical Paths (100% Coverage Required)

### Data Validation Path

```bash
extract_invoice_data()
  → validate_invoice_data()
    → validate_required_fields()
    → validate_formats()
    → verify_calculations()
```

### Automation Safety Path

```bash
trigger_automation()
  → connect_to_acsoft()
    → populate_form_fields()
      → pause_for_review()  ← CRITICAL: Never auto-save
```

### Error Handling Path

```bash
any_operation()
  → try/except blocks
    → log_error()
      → return_error_response()
```

---

## Exclusions from Coverage

### Allowed Exclusions

- `if __name__ == "__main__":` blocks
- Debug code (marked with `# pragma: no cover`)
- Abstract methods
- Type checking code (`if TYPE_CHECKING:`)
- Defensive programming (`if False:`, unreachable code)

### Example

```python
def main():  # pragma: no cover
    """Entry point - not covered by unit tests"""
    app = create_app()
    app.run()

if __name__ == "__main__":  # pragma: no cover
    main()
```

---

## Coverage Enforcement

### Pre-Commit Checks

```bash
# Add to .pre-commit-config.yaml
- repo: local
  hooks:
    - id: pytest-cov
      name: pytest-cov
      entry: pytest --cov=app --cov-fail-under=80
      language: system
      pass_filenames: false
      always_run: true
```

### CI/CD Checks (Future)

- Fail build if coverage < 80%
- Comment coverage diff on PRs
- Track coverage trends over time

---

## Coverage Reporting

### Report Format

```bash
Name                               Stmts   Miss  Cover
------------------------------------------------------
app/__init__.py                        4      0   100%
app/services/pdf_processor.py        120     12    90%
app/services/validator.py            150      5    97%
app/services/gemini_client.py         80      8    90%
app/services/acsoft_automation.py    100     25    75%
app/api/routes/invoices.py            90      9    90%
app/models/database.py                60      6    90%
app/utils/logger.py                   30      3    90%
------------------------------------------------------
TOTAL                                634     68    89%
```

### Coverage Trends

Track coverage over time:

- Initial baseline: X%
- Phase 1 target: 80%
- Phase 2 target: 85%
- Phase 3 target: 90%

---

## Improving Coverage

### Strategies

1. **Identify gaps:** Use coverage report to find untested code
2. **Write tests:** Add unit tests for uncovered functions
3. **Refactor:** Extract testable functions from complex code
4. **Integration tests:** Cover interactions between components
5. **Edge cases:** Test boundary conditions and error paths

### Priority Order

1. Critical safety features (automation, validation)
2. Core business logic (extraction, validation)
3. API endpoints and database operations
4. Utility functions and helpers
5. UI and less critical features

---

## Coverage Review Process

### Weekly Review

- Check current coverage percentage
- Identify components below target
- Create tasks to improve coverage

### Phase Review

- Verify phase coverage targets met
- Document any justified exclusions
- Update coverage requirements if needed

---

## Documentation

### Coverage Reports Location

- HTML report: `htmlcov/index.html`
- Terminal output: Displayed after test run
- CI/CD reports: (Future) Available in pipeline

### Coverage Badge (Future)

Display coverage badge in README.md:

```markdown
![Coverage](coverage.svg)
```

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Review Schedule:** Weekly during development
