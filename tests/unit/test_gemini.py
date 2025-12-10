import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from PIL import Image

# Add project root
import sys
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from app.services.pdf_processor import PDFProcessor
from app.services.gemini_client import GeminiClient

class TestPDFProcessor:
    def test_convert_to_images_missing_file(self):
        processor = PDFProcessor()
        with pytest.raises(FileNotFoundError):
            processor.convert_to_images("non_existent_file.pdf")

    # Note: Testing success case requires a real PDF or extensive mocking of fitz.
    # For unit tests, we trust fitz works and test our wrapper logic mostly.

class TestGeminiClient:
    @patch("app.services.gemini_client.genai")
    def test_init_configures_api_key(self, mock_genai):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            client = GeminiClient()
            mock_genai.configure.assert_called_with(api_key="test_key")

    @patch("app.services.gemini_client.genai")
    def test_extract_invoice_data_success(self, mock_genai):
        # Mock Response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"invoice_number": "INV-001", "total_amount": 100}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key"}):
            client = GeminiClient()
            # Create dummy image
            img = Image.new('RGB', (10, 10))
            
            result = client.extract_invoice_data([img])
            
            assert result["invoice_number"] == "INV-001"
            assert result["total_amount"] == 100
            assert "_metadata" in result
            
    def test_extract_raises_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
             # Ensure key is missing
             client = GeminiClient() 
             # Re-init might pick up previous env checks, but call should fail
             client.api_key = None
             with pytest.raises(ValueError, match="GEMINI_API_KEY is missing"):
                 client.extract_invoice_data([])

import os
