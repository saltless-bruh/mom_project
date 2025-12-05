# Test Data Documentation

## Mom's Accounting Automation System (MAAS)

**Version:** 1.0  
**Last Updated:** December 5, 2025

---

## Overview

This document describes the test data used for testing the MAAS system, including sample invoices, test databases, and fixture data.

---

## Test Data Location

### Directory Structure

```bash
tests/
├── fixtures/
│   ├── invoices/
│   │   ├── valid/              # Valid invoices for happy path testing
│   │   ├── invalid/            # Invalid invoices for error testing
│   │   ├── edge_cases/         # Edge case invoices
│   │   └── vendor_formats/     # Different vendor formats
│   ├── database/
│   │   └── test_data.sql       # Database seed data
│   ├── api_responses/
│   │   └── gemini_mock.json    # Mocked Gemini API responses
│   └── screenshots/            # Sample automation screenshots
```

---

## Invoice Test Data

### Valid Invoices

**File:** `tests/fixtures/invoices/valid/`

**Contents:**

- `invoice_001.pdf` - Standard single-page invoice (Vendor A)
- `invoice_002.pdf` - Multi-page invoice (Vendor B)
- `invoice_003.pdf` - Invoice with discounts (Vendor C)
- `invoice_004.pdf` - Invoice with multiple tax rates (Vendor D)
- `invoice_005.pdf` - Invoice with Vietnamese text (Vendor E)

**Characteristics:**

- All required fields present
- Valid formats
- Correct calculations
- High-quality scans
- Diverse layouts

### Invalid Invoices

**File:** `tests/fixtures/invoices/invalid/`

**Contents:**

- `missing_vendor.pdf` - Missing vendor name
- `missing_invoice_number.pdf` - Missing invoice number
- `invalid_date.pdf` - Invalid date format
- `calculation_error.pdf` - Arithmetic errors
- `poor_quality.pdf` - Low-quality scan

**Purpose:**

- Test validation error detection
- Test error messages
- Test error recovery

### Edge Cases

**File:** `tests/fixtures/invoices/edge_cases/`

**Contents:**

- `zero_tax.pdf` - Invoice with 0% tax
- `max_discount.pdf` - Invoice with 50% discount
- `future_date.pdf` - Invoice dated in future
- `single_item.pdf` - Invoice with only one item
- `many_items.pdf` - Invoice with 50+ items
- `large_amounts.pdf` - Invoice with very large amounts
- `small_amounts.pdf` - Invoice with fractional amounts

**Purpose:**

- Test boundary conditions
- Test handling of unusual but valid data

### Vendor Formats

**File:** `tests/fixtures/invoices/vendor_formats/`

**Contents:**

- `vendor_a_format.pdf` - Vendor A's standard format
- `vendor_b_format.pdf` - Vendor B's format (different layout)
- `vendor_c_format.pdf` - Vendor C's format (multi-column)
- `vendor_d_format.pdf` - Vendor D's format (compact)
- `vendor_e_format.pdf` - Vendor E's format (English + Vietnamese)

**Purpose:**

- Test multi-format support
- Verify extraction works across layouts
- Phase 2 testing requirement

---

## Database Test Data

### Test Database

**File:** `tests/fixtures/database/test_data.sql`

**Contents:**

```sql
-- Sample vendors
INSERT INTO vendors (vendor_id, name, tax_id, address) VALUES
  (1, 'Vendor A', '1234567890', '123 Street, City'),
  (2, 'Vendor B', '0987654321', '456 Avenue, City');

-- Sample invoices
INSERT INTO invoices (invoice_id, vendor_id, invoice_number, invoice_date, total_amount, status) VALUES
  (1, 1, 'INV-001', '2025-12-01', 1000000, 'completed'),
  (2, 2, 'INV-002', '2025-12-02', 2000000, 'pending');

-- Sample invoice items
INSERT INTO invoice_items (item_id, invoice_id, line_number, description, quantity, unit_price, total) VALUES
  (1, 1, 1, 'Item A', 10, 100000, 1000000),
  (2, 2, 1, 'Item B', 5, 200000, 1000000),
  (3, 2, 2, 'Item C', 5, 200000, 1000000);
```

**Purpose:**

- Seed test database for integration tests
- Provide consistent baseline data
- Test database queries

### Database Fixtures (pytest)

**File:** `tests/conftest.py`

```python
import pytest
from app.models.database import Database

@pytest.fixture
def db():
    """Create test database"""
    db = Database(":memory:")  # In-memory database
    db.initialize()
    yield db
    db.close()

@pytest.fixture
def sample_invoice():
    """Sample invoice data"""
    return {
        "vendor_name": "Vendor A",
        "invoice_number": "INV-001",
        "invoice_date": "2025-12-01",
        "total_amount": 1000000,
        "items": [
            {
                "line_number": 1,
                "description": "Item A",
                "quantity": 10,
                "unit_price": 100000,
                "total": 1000000
            }
        ]
    }
```

---

## API Mock Data

### Gemini API Responses

**File:** `tests/fixtures/api_responses/gemini_mock.json`

**Contents:**

```json
{
  "success_response": {
    "vendor_name": "Vendor A",
    "vendor_tax_id": "1234567890",
    "vendor_address": "123 Street, City",
    "invoice_number": "INV-001",
    "invoice_date": "2025-12-01",
    "payment_terms": "Net 30",
    "items": [
      {
        "line_number": 1,
        "description": "Product A",
        "quantity": 10,
        "unit": "pcs",
        "unit_price": 100000,
        "discount_percent": 0,
        "tax_rate": 10,
        "subtotal": 1000000,
        "discount": 0,
        "tax": 100000,
        "total": 1100000
      }
    ],
    "subtotal": 1000000,
    "discount_total": 0,
    "tax_total": 100000,
    "total_amount": 1100000,
    "confidence": 0.95
  },
  "low_confidence_response": {
    "vendor_name": "Vendor A",
    "invoice_number": "INV-002",
    "total_amount": 500000,
    "confidence": 0.75
  },
  "error_response": {
    "error": "API_TIMEOUT",
    "message": "Request timeout after 30s"
  }
}
```

**Usage:**

```python
import json

@pytest.fixture
def mock_gemini_response():
    with open('tests/fixtures/api_responses/gemini_mock.json') as f:
        return json.load(f)['success_response']
```

---

## Test Data Generation

### Invoice Generator Script

**File:** `tests/generate_test_data.py`

```python
"""Generate test invoice data"""

def generate_invoice_pdf(vendor: str, format: str, output_path: str):
    """Generate test invoice PDF"""
    # Implementation for generating test PDFs
    pass

def generate_test_database(output_path: str):
    """Generate test database with sample data"""
    # Implementation for generating test DB
    pass

def anonymize_invoice(input_pdf: str, output_pdf: str):
    """Anonymize sensitive data in invoice"""
    # Implementation for anonymizing PDFs
    pass
```

**Usage:**

```bash
python tests/generate_test_data.py --invoices 10 --formats 5
```

---

## Data Privacy & Anonymization

### Anonymization Process

**Sensitive Data:**

- Vendor names → "Vendor A", "Vendor B", etc.
- Tax IDs → "1234567890", "0987654321", etc.
- Addresses → Generic addresses
- Amounts → Rounded amounts

**Example:**

```bash
Real Invoice:
  Vendor: ABC Manufacturing Co., Ltd.
  Tax ID: 0123456789-012
  Address: 123 Real Street, Hanoi, Vietnam
  Amount: 12,345,678 VND

Anonymized Invoice:
  Vendor: Vendor A
  Tax ID: 1234567890
  Address: 123 Street, City
  Amount: 12,000,000 VND
```

### Consent & Usage

- All test invoices are anonymized
- No real vendor data in repository
- Mom's approval obtained for formats
- Test data for development only

---

## Test Data Maintenance

### Adding New Test Data

1. **Collect real invoice**
2. **Anonymize sensitive data**
3. **Store in appropriate folder**
4. **Document characteristics**
5. **Update this document**

### Updating Test Data

- Review quarterly
- Update for new vendor formats
- Remove obsolete formats
- Maintain diversity

### Version Control

- All test data in Git
- Binary files tracked with Git LFS (future)
- Document changes in commit messages

---

## Performance Test Data

### Large Dataset

**File:** `tests/fixtures/invoices/performance/`

**Contents:**

- 100 diverse invoices for load testing
- Mix of formats, sizes, and complexities
- Realistic distribution

**Usage:**

```python
def test_bulk_processing():
    """Test processing 100 invoices"""
    invoices = load_performance_test_data()
    start_time = time.time()
    
    for invoice in invoices:
        process_invoice(invoice)
    
    total_time = time.time() - start_time
    avg_time = total_time / len(invoices)
    
    assert avg_time < 120  # < 2 minutes per invoice
```

---

## Appendix: Sample Invoice Data

### Invoice Schema

```json
{
  "vendor_name": "string",
  "vendor_tax_id": "string",
  "vendor_address": "string",
  "invoice_number": "string",
  "invoice_date": "YYYY-MM-DD",
  "payment_terms": "string",
  "items": [
    {
      "line_number": "integer",
      "description": "string",
      "quantity": "number",
      "unit": "string",
      "unit_price": "number",
      "discount_percent": "number",
      "tax_rate": "number",
      "subtotal": "number",
      "discount": "number",
      "tax": "number",
      "total": "number"
    }
  ],
  "subtotal": "number",
  "discount_total": "number",
  "tax_total": "number",
  "total_amount": "number"
}
```

---

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Review Schedule:** Quarterly
