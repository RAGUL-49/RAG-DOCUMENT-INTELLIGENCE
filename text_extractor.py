from typing import List, Dict
import fitz

class TextExtractor:
    """Extract text content from documents"""
    
    def extract_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract text chunks from PDF with metadata"""
        doc = fitz.open(pdf_path)
        chunks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            if text.strip():
                chunks.append({
                    "type": "text",
                    "content": text,
                    "page": page_num + 1,
                    "source": pdf_path
                })
        
        doc.close()
        return chunks
    
    def extract_paragraphs(self, text: str, page: int, source: str) -> List[Dict]:
        """Split text into paragraph chunks"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        return [{
            "type": "text",
            "content": para,
            "page": page,
            "source": source
        } for para in paragraphs]
