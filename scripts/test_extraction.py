import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

# Load Env
load_dotenv(ROOT_DIR / ".env")

from app.services.pdf_processor import pdf_processor
from app.services.gemini_client import gemini_client

def test_extraction(pdf_path: str):
    print(f"Testing extraction for: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print("Error: File not found.")
        return

    try:
        # 1. Convert to Images
        print("Converting PDF to images...")
        images = pdf_processor.convert_to_images(pdf_path)
        print(f"Generated {len(images)} images.")
        
        # 2. Extract with Gemini
        print("Sending to Gemini API...")
        data = gemini_client.extract_invoice_data(images)
        
        # 3. Print Result
        print("\n--- Extraction Result ---")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("-------------------------")
        
    except Exception as e:
        print(f"Extraction Failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_extraction.py <path_to_invoice.pdf>")
    else:
        test_extraction(sys.argv[1])
