import fitz  # PyMuPDF
from typing import List, Dict, Any
from PIL import Image
import io

class PDFUtils:
    """Utilities for PDF processing"""
    
    @staticmethod
    def extract_text_by_page(pdf_path: str) -> Dict[int, str]:
        """Extract text from each page"""
        doc = fitz.open(pdf_path)
        text_by_page = {}
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_by_page[page_num + 1] = page.get_text()
        
        doc.close()
        return text_by_page
    
    @staticmethod
    def extract_images(pdf_path: str) -> List[Dict[str, Any]]:
        """Extract images from PDF"""
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                images.append({
                    "page": page_num + 1,
                    "index": img_index,
                    "image": Image.open(io.BytesIO(image_bytes)),
                    "ext": base_image["ext"]
                })
        
        doc.close()
        return images
    
    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """Get total number of pages"""
        doc = fitz.open(pdf_path)
        count = len(doc)
        doc.close()
        return count