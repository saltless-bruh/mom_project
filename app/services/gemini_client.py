import os
import logging
import json
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from PIL import Image
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("maas.gemini_client")

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set in environment variables.")
        else:
            genai.configure(api_key=self.api_key)
            
        # Use Experimental 2.0 Flash for speed/cost, fallback to 1.5 Flash if needed
        # Note: Model names change, verifying 'gemini-2.0-flash-exp' is current best practice for low latency
        self.model_name = "gemini-2.0-flash-exp" 
        self.max_retries = 3
        
        # Invoice Extraction Schema (JSON Schema for structured output)
        self.invoice_schema = {
            "type": "object",
            "properties": {
                "seller_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "tax_id": {"type": "string"},
                        "address": {"type": "string"}
                    },
                    "required": ["name"]
                },
                "buyer_info": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "tax_id": {"type": "string"},
                        "address": {"type": "string"}
                    },
                    "required": ["name"]
                },
                "invoice_number": {"type": "string"},
                "invoice_date": {"type": "string", "description": "Format YYYY-MM-DD"},
                "total_amount": {"type": "number"},
                "tax_amount": {"type": "number"},
                "currency": {"type": "string", "enum": ["VND", "USD"]},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "line_number": {"type": "integer"},
                            "description": {"type": "string"},
                            "quantity": {"type": "number"},
                            "unit_price": {"type": "number"},
                            "total": {"type": "number"},
                             "unit": {"type": "string"}
                        },
                         "required": ["description", "total"]
                    }
                }
            },
            "required": ["seller_info", "buyer_info", "invoice_number", "invoice_date", "total_amount", "items"]
        }

    def _get_model(self):
        return genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "response_schema": self.invoice_schema
            }
        )

    def extract_invoice_data(self, images: list[Image.Image]) -> Dict[str, Any]:
        """
        Extract structured data from invoice images using Gemini.
        Returns:
            Dictionary containing extracted invoice data.
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is missing.")

        model = self._get_model()
        
        # Prepare content: specific prompt + images
        prompt = """
        Extract all data from this Vietnamese invoice into JSON. 
        - Identify seller information (selling party) and buyer information (buying party).
        - Ensure 'invoice_date' is formatted YYYY-MM-DD.
        - Normalize numbers (remove thousands separators like dots or commas).
        - If 'symbol' or 'mau_so' is present, include it in invoice_number or notes.
        - Capture all line items accurately.
        """
        
        content = [prompt] + images
        
        retry_count = 0
        while retry_count < self.max_retries:
            try:
                start_time = time.time()
                response = model.generate_content(
                    content,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                
                duration = (time.time() - start_time) * 1000
                logger.info(f"Gemini API call took {duration:.2f}ms")
                
                # Parse JSON
                try:
                    result = json.loads(response.text)
                    # Add metadata
                    result["_metadata"] = {
                        "processing_time_ms": duration,
                        "model": self.model_name,
                         # Estimate cost (very rough, 2.0 flash is free in preview currently)
                        "estimated_cost_usd": 0.0 
                    }
                    return result
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON response: {response.text}")
                    raise ValueError("Invalid JSON response from Gemini")

            except Exception as e:
                logger.warning(f"Attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                if retry_count >= self.max_retries:
                    logger.error("Max retries exceeded for Gemini API")
                    raise
                time.sleep(2 ** retry_count)  # Exponential backoff

# Global instance
gemini_client = GeminiClient()
