import camelot
import pandas as pd
from typing import List, Dict
import json

import logging
class TableExtractor:
    """Extract tables from documents and convert to JSON"""
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict]:
        """Extract tables using Camelot"""
        tables = []
        
        try:
            # Extract tables from all pages
            table_list = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
            
            for i, table in enumerate(table_list):
                df = table.df
                
                # Convert to JSON structure
                table_json = self._dataframe_to_json(df)
                
                tables.append({
                    "type": "table",
                    "content": table_json,
                    "table_index": i + 1,
                    "page": table.page,
                    "source": pdf_path,
                    "raw_df": df.to_dict()
                })
        
        except Exception as e:
            logging.warning(f"Could not extract tables from {pdf_path}: {e}")
        
        return tables
    
    def _dataframe_to_json(self, df: pd.DataFrame) -> str:
        """Convert DataFrame to structured JSON"""
        # Use first row as headers if available
        if len(df) > 0:
            df.columns = df.iloc[0]
            df = df[1:]
        
        return json.dumps(df.to_dict(orient='records'), indent=2)