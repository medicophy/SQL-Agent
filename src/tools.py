import sqlite3
import pandas as pd
from typing import Optional
from langchain_core.tools import tool

class DatabaseTools:
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @tool
    def execute_read_only_query(self, query: str) -> str:
        """
        Execute a SQL SELECT query and return results.
        Use this when you need to retrieve data from the database.
        Always ensure the query is a SELECT statement only.
        """
        if not query.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries are allowed for safety."
        
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
    
    @tool
    def get_table_info(self, table_name: Optional[str] = None) -> str:
        """
        Get information about database tables.
        If table_name is provided, get info for that specific table.
        Otherwise, list all tables.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if table_name:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                
                info = f"Table: {table_name}\n"
                info += f"Total rows: {count}\n"
                info += "Columns:\n"
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
    
    @tool
    def get_table_sample(self, table_name: str, limit: int = 5) -> str:
        """
        Get a sample of rows from a table to understand the data.
        Use this to see what data looks like before writing complex queries.
        """
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
        """Return list of tools (methods are already decorated with @tool)"""
        return [
            self.execute_read_only_query,
            self.get_table_info,
            self.get_table_sample
        ]