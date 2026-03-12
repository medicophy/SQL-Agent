import sqlite3
from typing import Dict, List, Any

class DatabaseSchema:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.schema_info = self._extract_schema()
        self.sample_rows = self._get_sample_rows()
    
    def _extract_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract complete schema information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get foreign keys
            cursor.execute(f"PRAGMA foreign_key_list({table_name});")
            foreign_keys = cursor.fetchall()
            
            schema[table_name] = {
                'columns': [
                    {
                        'name': col[1],
                        'type': col[2],
                        'notnull': col[3],
                        'pk': col[5]
                    } for col in columns
                ],
                'foreign_keys': [
                    {
                        'column': fk[3],
                        'references': f"{fk[2]}({fk[4]})"
                    } for fk in foreign_keys
                ]
            }
        
        conn.close()
        return schema
    
    def _get_sample_rows(self, limit: int = 3) -> Dict[str, List]:
        """Get sample rows to help LLM understand data patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        samples = {}
        
        for table_name in self.schema_info.keys():
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
                rows = cursor.fetchall()
                if rows:
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = [col[1] for col in cursor.fetchall()]
                    samples[table_name] = {
                        'columns': columns,
                        'rows': rows
                    }
            except:
                continue
        
        conn.close()
        return samples
    
    def get_formatted_schema(self) -> str:
        """Return schema in a format suitable for LLM prompts"""
        formatted = "Database Schema:\n\n"
        
        for table_name, info in self.schema_info.items():
            formatted += f"Table: {table_name}\n"
            
            # Columns
            formatted += "  Columns:\n"
            for col in info['columns']:
                pk = " (PRIMARY KEY)" if col['pk'] else ""
                nullable = " NOT NULL" if col['notnull'] else ""
                formatted += f"    - {col['name']}: {col['type']}{pk}{nullable}\n"
            
            # Foreign keys
            if info['foreign_keys']:
                formatted += "  Relationships:\n"
                for fk in info['foreign_keys']:
                    formatted += f"    - {fk['column']} → {fk['references']}\n"
            
            # Sample data
            if table_name in self.sample_rows:
                formatted += "  Sample data:\n"
                sample = self.sample_rows[table_name]
                for row in sample['rows'][:2]:  # Show first 2 rows
                    formatted += f"    - {dict(zip(sample['columns'], row))}\n"
            
            formatted += "\n"
        
        return formatted
    
    def get_table_names(self) -> List[str]:
        return list(self.schema_info.keys())

# Test the schema extraction
if __name__ == "__main__":
    schema = DatabaseSchema("database/chinook.db")
    print(schema.get_formatted_schema())