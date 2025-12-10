import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import os

# Add project root needed for imports inside app.main
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.main import app
from app.models.database import db_manager

client = TestClient(app)

@pytest.mark.asyncio
async def test_upload_invoice():
    # Create dummy PDF
    dummy_pdf = Path("tests/dummy.pdf")
    with open(dummy_pdf, "wb") as f:
        f.write(b"%PDF-1.4 dummy content")
    
    try:
        with open(dummy_pdf, "rb") as f:
            response = client.post(
                "/api/invoices/upload",
                files={"file": ("dummy.pdf", f, "application/pdf")}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["invoice_number"] == "PENDING"
        assert "id" in data
        
        # Test List
        list_response = client.get("/api/invoices")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert len(list_data["invoices"]) >= 1
        assert list_data["invoices"][0]["id"] == data["id"]
        
    finally:
        if dummy_pdf.exists():
            dummy_pdf.unlink()
