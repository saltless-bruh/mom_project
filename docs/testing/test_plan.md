# Test Plan

## Mom's Accounting Automation System (MAAS)

**Version:** 1.0  
**Last Updated:** December 5, 2025  
**Status:** Active

---

## 1. Overview

### 1.1 Purpose

This document outlines the comprehensive testing strategy for the MAAS project, ensuring the system meets quality, reliability, and performance requirements.

### 1.2 Scope

Testing covers:

- Unit testing (80%+ coverage)
- Integration testing (70%+ coverage)
- End-to-end testing
- Performance testing
- User acceptance testing (UAT)

### 1.3 Testing Objectives

- Verify functional requirements are met
- Ensure data accuracy (95%+ extraction)
- Validate performance targets (< 2 min per invoice)
- Confirm safety mechanisms (no auto-save)
- Validate error handling and recovery

---

## 2. Test Strategy

### 2.1 Unit Testing

**Tool:** pytest  
**Coverage Target:** 80%+  
**Location:** `tests/unit/`

**Components to Test:**

- PDF processor functions
- Validator functions
- Database operations (CRUD)
- Gemini client (with mocks)
- Automation helper functions
- API endpoint logic

**Best Practices:**

- Test one function/method at a time
- Use mocks for external dependencies
- Test happy path and error cases
- Use fixtures for test data
- Run fast (< 5 minutes total)

### 2.2 Integration Testing

**Tool:** pytest  
**Coverage Target:** 70%+  
**Location:** `tests/integration/`

**Workflows to Test:**

- Upload → Extraction workflow
- Extraction → Validation workflow
- Validation → Automation workflow
- API endpoints with database
- Error scenarios and recovery

**Best Practices:**

- Test component interactions
- Use real database (test instance)
- Mock only external services (Gemini API)
- Clean up test data after each test
- Run in isolation

### 2.3 End-to-End Testing

**Tool:** pytest + manual testing  
**Location:** `tests/e2e/`

**Scenarios to Test:**

- Complete invoice processing workflow
- Multiple invoice formats
- Error handling and recovery
- User correction workflow
- Automation with ACSoft (manual)

**Best Practices:**

- Test complete user workflows
- Use realistic test data
- Include edge cases
- Manual verification for UI/automation

### 2.4 Performance Testing

**Tool:** pytest + custom metrics  
**Location:** `tests/performance/`

**Metrics to Measure:**

- PDF extraction time (< 5s per page)
- Validation time (< 1s)
- Automation time (< 30s)
- End-to-end time (< 2 min)
- API response times

**Best Practices:**

- Test with realistic data sizes
- Test with multiple invoices
- Measure average and percentiles
- Test under load (50-100 invoices)

### 2.5 User Acceptance Testing (UAT)

**Participants:** Mom (primary user)  
**Timeline:** Week 4 (Phase 3)

**Test Cases:**

- Installation on mom's computer
- Processing 10-20 real invoices
- Error handling and recovery
- Usability and ease of use
- Overall satisfaction

---

## 3. Test Environment

### 3.1 Development Environment

- **OS:** Windows 10/11
- **Python:** 3.9+
- **Database:** SQLite (test instance)
- **ACSoft:** Mock or test instance

### 3.2 Test Data

- **Location:** `tests/fixtures/`
- **Contents:**
  - Sample invoices (5+ formats)
  - Anonymized data
  - Edge cases (missing fields, errors)
  - Performance test data (large dataset)

### 3.3 CI/CD Environment (Future)

- Automated test runs on PR
- Test coverage reporting
- Performance regression detection

---

## 4. Test Cases

### 4.1 Unit Test Cases

**PDF Processor Tests:**

- Test valid PDF upload
- Test invalid file type
- Test large file (> 50MB)
- Test corrupted PDF
- Test multi-page PDF

**Validator Tests:**

- Test complete valid data
- Test missing required fields
- Test invalid date format
- Test calculation errors
- Test duplicate detection

**Database Tests:**

- Test CRUD operations
- Test transaction rollback
- Test concurrent access
- Test query performance

### 4.2 Integration Test Cases

**Upload & Extraction:**

- Upload PDF → Extract data → Store in DB
- Handle extraction errors
- Verify confidence scores
- Test with diverse formats

**Validation & Correction:**

- Extract → Validate → Return errors
- Correct data → Re-validate → Update DB
- Test edge cases

**Automation:**

- Validate → Automate → Capture screenshots
- Handle ACSoft connection errors
- Verify no auto-save occurs

### 4.3 End-to-End Test Cases

**Standard Workflow:**

1. Upload invoice PDF
2. Review extraction results
3. Approve data
4. Automate ACSoft entry
5. Verify in ACSoft
6. Manual save

**Error Scenarios:**

1. Low confidence extraction
2. Validation errors
3. Automation failure
4. Duplicate invoice

---

## 5. Test Schedule

### Phase 1 (Weeks 1-2)

- [ ] Week 1: Unit tests for core components
- [ ] Week 2: Integration tests for workflows
- [ ] Week 2: E2E test with 10 sample invoices

### Phase 2 (Week 3)

- [ ] Integration tests for multi-format support
- [ ] Integration tests for error recovery
- [ ] E2E test with 30 invoices

### Phase 3 (Week 4)

- [ ] Performance testing
- [ ] UAT with mom
- [ ] Final regression testing

---

## 6. Test Metrics

### 6.1 Coverage Metrics

- Unit test coverage: 80%+
- Integration test coverage: 70%+
- Critical path coverage: 100%

### 6.2 Quality Metrics

- Extraction accuracy: 95%+
- Validation accuracy: 100%
- Test pass rate: 95%+
- Bug detection rate: Track issues found

### 6.3 Performance Metrics

- PDF extraction: < 5s per page
- Validation: < 1s
- Automation: < 30s
- End-to-end: < 2 min

---

## 7. Defect Management

### 7.1 Bug Priority

- **P0 (Critical):** System unusable, data loss
- **P1 (High):** Major feature broken
- **P2 (Medium):** Minor feature issue
- **P3 (Low):** Cosmetic issue

### 7.2 Bug Workflow

1. Log in GitHub Issues
2. Assign priority
3. Fix in appropriate branch
4. Write regression test
5. Verify fix
6. Close issue

---

## 8. Test Reports

### 8.1 Daily Test Report

- Tests run today
- Pass/fail count
- New issues found
- Coverage changes

### 8.2 Phase Test Report

- All tests executed
- Overall pass/fail rate
- Coverage achieved
- Issues summary
- Go/no-go recommendation

---

## 9. Exit Criteria

### Phase 1 Exit

- [ ] 80%+ unit test coverage
- [ ] All integration tests pass
- [ ] 10 invoices processed successfully
- [ ] No P0 bugs

### Phase 2 Exit

- [ ] All Phase 1 criteria met
- [ ] 5+ formats supported
- [ ] 30 invoices processed successfully
- [ ] Error rate < 5%

### Phase 3 Exit

- [ ] All Phase 2 criteria met
- [ ] Performance targets met
- [ ] UAT approved by mom
- [ ] No P0/P1 bugs
- [ ] Documentation complete

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Next Review:** After each phase completion
