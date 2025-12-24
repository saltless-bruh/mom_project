import os
import sys
import json
import traceback
from pathlib import Path
from dotenv import load_dotenv

# Redirect output to file
log_file = open("verification_result.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

print("Starting Verification...")

try:
    # Add app to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print("Importing modules...")
    from app.services.pdf_processor import pdf_processor
    from app.services.gemini_client import gemini_client
    print("Modules imported.")

    load_dotenv()

    # 1. Select a Test Invoice
    filename = "1C24TVM_00000332.pdf"
    invoice_path = Path("docs/Hoá đơn mua hàng-20251223T043654Z-3-001/Hoá đơn mua hàng/1C24TVM_00000332.pdf")
    
    if not invoice_path.exists():
        print(f"Warning: Exact path not found: {invoice_path}")
        print("Searching in docs/...")
        found = list(Path("docs").rglob(filename))
        if found:
            invoice_path = found[0]
            print(f"Found invoice at: {invoice_path}")
        else:
            print(f"Error: Could not find {filename}")
            sys.exit(1)

    print(f"Processing: {invoice_path}")
    
    # 2. Convert to Images
    try:
        images = pdf_processor.convert_to_images(str(invoice_path))
        print(f"PDF converted to {len(images)} images.")
    except Exception as e:
        print(f"PDF Processing Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 3. Extract with Gemini
    if not os.getenv("GEMINI_API_KEY"):
         print("Error: GEMINI_API_KEY not set in environment variables.")
         sys.exit(1)

    print("Sending to Gemini 2.0 Flash...")
    try:
        data = gemini_client.extract_invoice_data(images)
        print("Extraction Successful!")
        print(json.dumps({
            "seller_info": data.get("seller_info"),
            "buyer_info": data.get("buyer_info"),
            "invoice_number": data.get("invoice_number"),
            "total_amount": data.get("total_amount")
        }, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Gemini Extraction Failed: {e}")
        traceback.print_exc()
        sys.exit(1)

    # 4. Verify Logic
    print("\n--- Verifying Logic ---")
    seller_info = data.get("seller_info", {})
    buyer_info = data.get("buyer_info", {})
    
    seller_name = seller_info.get("name", "")
    buyer_name = buyer_info.get("name", "")
    
    print(f"Extracted Seller: {seller_name}")
    print(f"Extracted Buyer: {buyer_name}")

    mom_company_keywords = ["933", "CÔNG TY TNHH MỘT THÀNH VIÊN 933"]
    is_selling = any(k in seller_name.upper() for k in mom_company_keywords)
    
    if is_selling:
        print(f"Logic Result: SELLING Invoice (OUT)")
        print(f"Reason: Seller name '{seller_name}' contains Mom's company keyword.")
    else:
        print(f"Logic Result: BUYING Invoice (IN)")
        print(f"Reason: Seller name '{seller_name}' does not match Mom's company. (Assumed Supplier)")

    print("--- Test Complete ---")

except Exception as e:
    print(f"Unhandled Exception: {e}")
    traceback.print_exc()

finally:
    log_file.close()
