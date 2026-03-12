import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any
from langchain.tools import tool

class DatabaseTools:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def _get_connection(self):
        """Get or create database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    @tool
    def execute_read_only_query(self, query: str) -> str:
        """
        Execute a SQL SELECT query and return results.
        Use this when you need to retrieve data from the database.
        Always ensure the query is a SELECT statement only.
        """
        # Safety check - only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries are allowed for safety."
        
        conn = self._get_connection()
        try:
            # Execute query and convert to DataFrame for nice formatting
            df = pd.read_sql_query(query, conn)
            if df.empty:
                return "Query executed successfully but returned no results."
            
            # Format results as string
            result = f"Found {len(df)} row(s):\n"
            result += df.to_string(index=False)
            return result
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    @tool
    def get_table_info(self, table_name: Optional[str] = None) -> str:
        """
        Get information about database tables.
        If table_name is provided, get info for that specific table.
        Otherwise, list all tables.
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if table_name:
                # Get column info for specific table
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                # Get row count
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
                # List all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                return "Available tables:\n" + "\n".join([f"  - {t[0]}" for t in tables])
        except Exception as e:
            return f"Error getting table info: {str(e)}"
    
    @tool
    def get_table_sample(self, table_name: str, limit: int = 5) -> str:
        """
        Get a sample of rows from a table to understand the data.
        Use this to see what data looks like before writing complex queries.
        """
        conn = self._get_connection()
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT {limit}", conn)
            if df.empty:
                return f"Table {table_name} is empty."
            
            result = f"Sample of {len(df)} rows from {table_name}:\n"
            result += df.to_string(index=False)
            return result
        except Exception as c:
            return f"Error getting sample: {str(e)}"
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None