from typing import List, Dict
import json
from pathlib import Path
import logging

from .text_extractor import TextExtractor
from .table_extractor import TableExtractor
from .image_ocr import ImageOCR
from .chart_metadata import ChartMetadataExtractor
from .chunker import Chunker
from ..utils.config import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class IngestionPipeline:
    """Main pipeline for document ingestion"""
    
    def __init__(self):
        self.text_extractor = TextExtractor()
        self.table_extractor = TableExtractor()
        self.ocr = ImageOCR()
        self.chart_extractor = ChartMetadataExtractor()
        self.chunker = Chunker()
    
    def process_document(self, pdf_path: str) -> List[Dict]:
        """Process a single document, making the process more robust with error handling."""
        doc_path = Path(pdf_path)
        if not doc_path.exists():
            logging.error(f"File not found: {pdf_path}")
            return []

        logging.info(f"Processing: {pdf_path}")
        all_chunks = []
        
        try:
            # 1. Extract text
            logging.info("  - Extracting text...")
            text_chunks = self.text_extractor.extract_from_pdf(pdf_path)
            all_chunks.extend(text_chunks)
            
            # 2. Extract tables
            logging.info("  - Extracting tables...")
            table_chunks = self.table_extractor.extract_tables_from_pdf(pdf_path)
            all_chunks.extend(table_chunks)
            
            # 3. Extract OCR from images
            logging.info("  - Running OCR on images...")
            ocr_chunks = self.ocr.extract_from_pdf_images(pdf_path)
            all_chunks.extend(ocr_chunks)
            
            # 4. Extract chart metadata from text chunks
            logging.info("  - Extracting chart metadata...")
            for chunk in text_chunks:
                charts = self.chart_extractor.extract_chart_info(
                    chunk["content"], 
                    chunk["page"], 
                    chunk["source"]
                )
                all_chunks.extend(charts)

        except Exception as e:
            logging.error(f"A critical error occurred during extraction for {pdf_path}: {e}", exc_info=True)
            # Depending on desired behavior, you might want to return here or continue with what was extracted.
            # For now, we'll continue to the chunking step with what we have.
        
        # 5. Chunk all applicable items for better retrieval
        logging.info("  - Chunking extracted content...")
        final_chunks = []
        for chunk in all_chunks:
            # The chunker can decide if a chunk needs splitting
            final_chunks.extend(self.chunker.process_chunk(chunk))
        
        logging.info(f"  ✓ Generated {len(final_chunks)} chunks for {pdf_path}")
        return final_chunks
    
    def save_chunks(self, chunks: List[Dict], output_path: str):
        """Save processed chunks to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        logging.info(f"  ✓ Saved {len(chunks)} chunks to {output_path}")
