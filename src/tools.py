import sqlite3
import pandas as pd
from typing import Optional
from langchain_core.tools import StructuredTool

class DatabaseTools:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def _execute_read_only_query(self, query: str) -> str:
        """Execute a SQL SELECT query and return results."""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(query, conn)
            if df.empty:
                return "Query executed successfully but returned no results."
            result = f"Found {len(df)} row(s):\n"
            result += df.to_string(index=False)
            return result
        except Exception as e:
            return f"Error executing query: {str(e)}"
        finally:
            conn.close()
    
    def _get_table_info(self, table_name: Optional[str] = None) -> str:
        """Get information about database tables. If no table name provided, lists all tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if table_name:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                
                info = f"Table: {table_name}\nTotal rows: {count}\nColumns:\n"
                for col in columns:
                    info += f"  - {col[1]} ({col[2]})"
                    if col[5]:
                        info += " PRIMARY KEY"
                    info += "\n"
                return info
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return "Available tables:\n" + "\n".join([f"  - {t[0]}" for t in tables])
        except Exception as e:
            return f"Error getting table info: {str(e)}"
        finally:
            conn.close()
    
    def _get_table_sample(self, table_name: str, limit: int = 5) -> str:
        """Get sample rows from a table. Specify table_name and optional limit."""
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
            if df.empty:
                return f"Table {table_name} is empty."
            result = f"Sample of {len(df)} rows from {table_name}:\n"
            result += df.to_string(index=False)
            return result
        except Exception as e:
            return f"Error getting sample: {str(e)}"
        finally:
            conn.close()
    
    def get_tools(self):
        """Return list of tools as StructuredTool objects"""
        return [
            StructuredTool.from_function(
                func=self._execute_read_only_query,
                name="execute_read_only_query",
                description="Execute a SQL SELECT query and return results.",
                args_schema=None  # Let LangChain infer from function signature
            ),
            StructuredTool.from_function(
                func=self._get_table_info,
                name="get_table_info",
                description="Get information about database tables. If no table name provided, lists all tables.",
                args_schema=None
            ),
            StructuredTool.from_function(
                func=self._get_table_sample,
                name="get_table_sample",
                description="Get sample rows from a table. Specify table_name and optional limit.",
                args_schema=None
            )
        ]