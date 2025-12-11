from typing import List, Dict
import re

class ChartMetadataExtractor:
    """Extract metadata from charts and figures"""
    
    def extract_chart_info(self, text: str, page: int, source: str) -> List[Dict]:
        """Extract chart titles, labels, and units from text"""
        charts = []
        
        # Pattern matching for common chart indicators
        chart_patterns = [
            r'Figure \d+[:\.]?\s*([^\n]+)',
            r'Chart \d+[:\.]?\s*([^\n]+)',
            r'Graph \d+[:\.]?\s*([^\n]+)',
            r'Table \d+[:\.]?\s*([^\n]+)'
        ]
        
        for pattern in chart_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                title = match.group(1).strip()
                
                # Extract surrounding context
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 200)
                context = text[start:end]
                
                charts.append({
                    "type": "chart_metadata",
                    "title": title,
                    "content": context,
                    "page": page,
                    "source": source
                })
        
        return charts