import fitz  # pymupdf
import logging
from pathlib import Path
from PIL import Image
import io

logger = logging.getLogger("maas.pdf_processor")

class PDFProcessor:
    @staticmethod
    def get_pdf_metadata(pdf_path: str) -> dict:
        """Extract basic metadata from PDF."""
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            page_count = doc.page_count
            doc.close()
            return {
                "page_count": page_count,
                "author": metadata.get("author"),
                "creator": metadata.get("creator"),
                "producer": metadata.get("producer"),
            }
        except Exception as e:
            logger.error(f"Failed to get metadata for {pdf_path}: {e}")
            raise

    @staticmethod
    def convert_to_images(pdf_path: str, zoom_x: float = 2.0, zoom_y: float = 2.0) -> list[Image.Image]:
        """
        Convert PDF pages to PIL Images.
        Args:
            pdf_path: Path to PDF file.
            zoom_x: Horizontal zoom factor (resolution).
            zoom_y: Vertical zoom factor (resolution).
        Returns:
            List of PIL Image objects.
        """
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        images = []
        try:
            doc = fitz.open(path)
            mat = fitz.Matrix(zoom_x, zoom_y)  # Zoom for better OCR resolution
            
            for page in doc:
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
                
            doc.close()
            logger.info(f"Converted {len(images)} pages from {path.name}")
            return images
            
        except Exception as e:
            logger.error(f"Failed to convert PDF {pdf_path}: {e}")
            raise

# Global instance
pdf_processor = PDFProcessor()
