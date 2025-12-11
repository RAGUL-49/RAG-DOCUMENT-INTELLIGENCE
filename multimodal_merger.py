from typing import List, Dict
from collections import defaultdict

class MultiModalMerger:
    """Merge and organize chunks from different modalities"""
    
    def merge_by_page(self, chunks: List[Dict]) -> Dict[int, List[Dict]]:
        """Group chunks by page number"""
        page_groups = defaultdict(list)
        
        for chunk in chunks:
            page = chunk['metadata'].get('page', 0)
            page_groups[page].append(chunk)
        
        return dict(page_groups)
    
    def merge_by_type(self, chunks: List[Dict]) -> Dict[str, List[Dict]]:
        """Group chunks by modality type"""
        type_groups = defaultdict(list)
        
        for chunk in chunks:
            chunk_type = chunk['metadata'].get('type', 'unknown')
            type_groups[chunk_type].append(chunk)
        
        return dict(type_groups)
    
    def create_context(self, chunks: List[Dict]) -> str:
        """Create formatted context from chunks"""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk['metadata']
            chunk_type = metadata.get('type', 'text')
            page = metadata.get('page', 'Unknown')
            
            if chunk_type == 'table':
                header = f"[Table {i}]\nPage: {page}"
            elif chunk_type == 'ocr':
                header = f"[OCR Extract {i}]\nPage: {page}, Figure: {metadata.get('image_index', 'N/A')}"
            elif chunk_type == 'chart_metadata':
                header = f"[Chart Metadata {i}]\nPage: {page}\nTitle: {metadata.get('title', 'N/A')}"
            else:
                header = f"[Text Chunk {i}]\nPage: {page}, Section: {metadata.get('section', 'N/A')}"
            
            context_parts.append(f"{header}\nContent: {chunk['content']}\n")
        
        return "\n-------------------\n".join(context_parts)