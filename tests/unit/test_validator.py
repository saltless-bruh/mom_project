import pytest
from app.services.validator import InvoiceValidator

class TestInvoiceValidator:
    def setup_method(self):
        self.validator = InvoiceValidator()

    def test_valid_invoice(self):
        data = {
            "vendor_name": "Test Vendor",
            "invoice_number": "INV001",
            "invoice_date": "2025-10-20",
            "total_amount": 110000,
            "tax_amount": 10000,
            "items": [
                {"quantity": 2, "unit_price": 50000, "total": 100000}
            ]
        }
        result = self.validator.validate(data)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["normalized_data"]["subtotal"] == 100000

    def test_missing_field(self):
        data = {
            "vendor_name": "Test Vendor",
             # Missing invoice_number
            "total_amount": 100
        }
        result = self.validator.validate(data)
        assert result["is_valid"] is False
        assert any("invoice_number" in e for e in result["errors"])

    def test_date_normalization(self):
        data = {
            "vendor_name": "A", "invoice_number": "1", "total_amount": 0,
            "invoice_date": "20/10/2025" # DD/MM/YYYY
        }
        result = self.validator.validate(data)
        assert result["normalized_data"]["invoice_date"] == "2025-10-20"

    def test_math_warning(self):
        data = {
            "vendor_name": "A", "invoice_number": "1", "invoice_date": "2025-10-10",
            "total_amount": 100,
            "items": [
                {"quantity": 2, "unit_price": 40, "total": 100} # 2*40=80 != 100
            ]
        }
        result = self.validator.validate(data)
        # Math mismatch triggers a WARNING, not an ERROR, so it should be VALID.
        assert result["is_valid"] is True 
        assert len(result["warnings"]) > 0
        assert any("Line 1: Math mismatch" in w for w in result["warnings"])
        
    def test_grand_total_error(self):
        data = {
            "vendor_name": "A", "invoice_number": "1", "invoice_date": "2025-10-10",
            "total_amount": 200, # mismatched
            "tax_amount": 10,
            "items": [
                {"quantity": 1, "unit_price": 100, "total": 100}
            ]
        }
        # Subtotal = 100. Tax = 10. Calc Total = 110. Scanned Total = 200. Error!
        result = self.validator.validate(data)
        assert result["is_valid"] is False
        assert any("Grand Total mismatch" in e for e in result["errors"])
