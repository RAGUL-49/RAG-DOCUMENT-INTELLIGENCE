import pytesseract
from PIL import Image
from typing import List, Dict
import fitz
import io
import logging

class ImageOCR:
    """Extract text from images using OCR"""
    
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_from_pdf_images(self, pdf_path: str) -> List[Dict]:
        """Extract text from all images in PDF"""
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            logging.error(f"Failed to open PDF for OCR {pdf_path}: {e}")
            return []

        ocr_results = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convert to PIL Image
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Perform OCR
                    text = pytesseract.image_to_string(image)
                    
                    if text.strip():
                        ocr_results.append({
                            "type": "ocr",
                            "content": text.strip(),
                            "page": page_num + 1,
                            "image_index": img_index + 1,
                            "source": pdf_path
                        })
                
                except Exception as e:
                    logging.warning(f"OCR error on page {page_num + 1}, image {img_index + 1} in {pdf_path}: {e}")
        
        doc.close()
        return ocr_results
