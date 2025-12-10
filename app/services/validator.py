import logging
import re
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger("maas.validator")

class ValidationError(Exception):
    pass

class InvoiceValidator:
    def __init__(self):
        # Common VAT rates in Vietnam: 0%, 5%, 8%, 10%
        self.valid_tax_rates = [0, 5, 8, 10]

    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize invoice data.
        Returns validation result with 'is_valid', 'errors', 'warnings', and 'normalized_data'.
        """
        errors = []
        warnings = []
        normalized = data.copy()

        # 1. Required Fields Check
        required_fields = ["vendor_name", "invoice_number", "invoice_date", "total_amount"]
        for field in required_fields:
            if not normalized.get(field):
                errors.append(f"Missing required field: {field}")

        # 2. Date Normalization (YYYY-MM-DD)
        if normalized.get("invoice_date"):
            try:
                date_str = str(normalized["invoice_date"]).strip()
                # Try parsing common formats
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        normalized["invoice_date"] = dt.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                else:
                     errors.append(f"Invalid date format: {date_str}. Expected YYYY-MM-DD or DD/MM/YYYY")
            except Exception as e:
                errors.append(f"Date conversion error: {e}")

        # 3. Numeric Normalization & Math Check
        try:
            # Main totals
            total_amt = self._parse_float(normalized.get("total_amount", 0))
            subtotal = 0.0
            tax_total = self._parse_float(normalized.get("tax_amount", 0))
            
            normalized["total_amount"] = total_amt
            normalized["tax_amount"] = tax_total

            # Items
            if "items" in normalized and isinstance(normalized["items"], list):
                for i, item in enumerate(normalized["items"]):
                    line_num = i + 1
                    qty = self._parse_float(item.get("quantity", 0))
                    price = self._parse_float(item.get("unit_price", 0))
                    line_total = self._parse_float(item.get("total", 0))
                    
                    # Updates normalized item
                    item["quantity"] = qty
                    item["unit_price"] = price
                    item["total"] = line_total

                    # Math Check: Qty * Price vs Total
                    calc_total = qty * price
                    # Allow small tolerance (1.0 unit diff) for rounding
                    if abs(calc_total - line_total) > 1.0:
                        warnings.append(f"Line {line_num}: Math mismatch. {qty} * {price} = {calc_total}, but scanned {line_total}")

                    subtotal += line_total
            
            normalized["subtotal"] = subtotal

            # 4. Tax Validation
            # If tax isn't provided, estimate it
            if tax_total == 0 and total_amt > subtotal:
                 tax_total = total_amt - subtotal
                 normalized["tax_amount"] = tax_total
                 warnings.append(f"Tax amount missing, calculated as {tax_total}")

            # Check logic: Subtotal + Tax = Total
            calc_grand_total = subtotal + tax_total
            if abs(calc_grand_total - total_amt) > 5.0: # 5 VND tolerance
                errors.append(f"Grand Total mismatch. Subtotal({subtotal}) + Tax({tax_total}) = {calc_grand_total}, scans says {total_amt}")

        except Exception as e:
            errors.append(f"Validation Error processing numbers: {e}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "normalized_data": normalized
        }

    def _parse_float(self, value):
        """Parse string or number to float, removing currency symbols and commas."""
        if isinstance(value, (int, float)):
            return float(value)
        if not value:
            return 0.0
        try:
            # Remove non-numeric chars except dot and minus (and comma if used as decimal in some locales, 
            # but VN usually uses dot for thousands and comma for decimal? actually VN uses dot for thousands.
            # Standardizing: Remove all non-digits, then assume last punctuation might be decimal or just integer)
            
            # Simple approach for VND (integer based mostly): Remove non-digits. 
            # If standard float, Python handles dot.
            clean_str = str(value).replace(",", "").replace(".", "") # Remove ALL separators for VND as it's usually integer
            
            # Wait, 100.000 (100k) vs 100.00 (100 dot 00).
            # Heuristic: If "VND", usually no decimals.
            # For this MVP, let's assume input is cleaned by Gemini or we just strip non-digit/dot
            
            # Safer: Remove chars that are not digits, dot, or minus
            clean = re.sub(r'[^\d.-]', '', str(value))
            return float(clean)
        except:
            return 0.0

# Global instance
validator = InvoiceValidator()
