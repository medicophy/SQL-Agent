import streamlit as st
import pandas as pd
import sys
import os
import time
import re
from datetime import datetime

# Add the parent directory to path so we can import src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import SQLAgent

# Page config
st.set_page_config(
    page_title="SQL Agent Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Chat message styling */
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4caf50;
    }
    .sql-query {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 0.5rem;
        border-radius: 0.5rem;
        font-family: monospace;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    .timestamp {
        color: #666;
        font-size: 0.8rem;
        margin-bottom: 0.2rem;
    }
    /* Metrics styling */
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.title("🤖 SQL Agent")
    st.markdown("---")
    
    # Configuration Section
    with st.expander("⚙️ Configuration", expanded=True):
        # Database selection
        db_path = st.text_input(
            "Database Path",
            value="database/chinook.db",
            help="Path to your SQLite database file"
        )
        
        # Model selection
        model_options = {
            "gemini-2.5-flash": "Gemini 2.5 Flash (Fast)",
            "gemini-2.5-pro": "Gemini 2.5 Pro (Powerful)"
        }
        selected_model = st.selectbox(
            "Model",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=0
        )
        
        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Higher = more creative, Lower = more precise"
        )
        
        # Initialize agent button
        if st.button("🚀 Initialize Agent", use_container_width=True):
            with st.spinner("Initializing agent..."):
                try:
                    # You'll need to modify agent.py to accept temperature
                    st.session_state.agent = SQLAgent(db_path, llm_type="gemini")
                    st.session_state.schema = st.session_state.agent.schema.get_formatted_schema()
                    st.session_state.db_stats = get_database_stats(db_path)
                    st.success("✅ Agent ready!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed: {str(e)}")
    
    # Database Info Section
    if 'db_stats' in st.session_state:
        with st.expander("📊 Database Stats", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tables", st.session_state.db_stats['table_count'])
            with col2:
                st.metric("Total Rows", f"{st.session_state.db_stats['total_rows']:,}")
            
            # Show table list
            st.markdown("**Tables:**")
            for table in st.session_state.db_stats['tables'][:5]:
                st.markdown(f"- {table}")
            if len(st.session_state.db_stats['tables']) > 5:
                st.markdown(f"... and {len(st.session_state.db_stats['tables'])-5} more")
    
    # Schema Viewer
    if 'schema' in st.session_state:
        with st.expander("📖 Database Schema", expanded=False):
            st.code(st.session_state.schema, language="sql")
    
    # Conversation Management
    with st.expander("💬 Conversation", expanded=False):
        st.markdown(f"**ID:** `{st.session_state.conversation_id}`")
        st.markdown(f"**Messages:** {len(st.session_state.messages)}")
        if st.button("🔄 New Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.rerun()
    
    # Query History
    if st.session_state.query_history:
        with st.expander("📜 Query History", expanded=False):
            for i, query in enumerate(st.session_state.query_history[-5:]):
                with st.container():
                    st.markdown(f"**{i+1}.** `{query[:50]}...`")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.8rem;'>
        Built with LangChain + Gemini<br>
        v1.0.0
    </div>
    """, unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.title("🤖 Text-to-SQL Agent")
    st.markdown("Ask questions about your database in plain English!")

with col2:
    if 'agent' in st.session_state:
        st.markdown("""
        <div style='background-color: #e8f5e8; padding: 0.5rem; border-radius: 0.5rem; text-align: center;'>
            🟢 Agent Ready
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background-color: #ffebee; padding: 0.5rem; border-radius: 0.5rem; text-align: center;'>
            ⚪ Initialize Agent
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Chat interface
if 'agent' not in st.session_state:
    st.info("👈 Please initialize the agent from the sidebar first")
else:
    # Create two columns for chat and results
    chat_col, viz_col = st.columns([3, 2])
    
    with chat_col:
        st.subheader("💬 Conversation")
        
        # Display chat history with formatting
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Timestamp
                if "timestamp" in message:
                    st.markdown(f"<div class='timestamp'>{message['timestamp']}</div>", 
                              unsafe_allow_html=True)
                
                # Message content
                if message["role"] == "user":
                    st.markdown(f"<div class='user-message'>{message['content']}</div>", 
                              unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='assistant-message'>{message['content']}</div>", 
                              unsafe_allow_html=True)
                
                # If there are SQL queries in the response, show them
                if "sql_queries" in message:
                    with st.expander("📝 View SQL Queries"):
                        for sql in message["sql_queries"]:
                            st.markdown(f"<div class='sql-query'>{sql}</div>", 
                                      unsafe_allow_html=True)
        
        # Chat input
        if prompt := st.chat_input("Ask me about your data..."):
            # Add user message
            user_msg = {
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.messages.append(user_msg)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    start_time = time.time()
                    response = st.session_state.agent.ask(prompt)
                    end_time = time.time()
                    
                    # Try to extract SQL queries from response
                    sql_queries = extract_sql_queries(response)
                    
                    # Add assistant message
                    assistant_msg = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "response_time": f"{end_time - start_time:.2f}s",
                        "sql_queries": sql_queries
                    }
                    st.session_state.messages.append(assistant_msg)
                    
                    # Add to query history if SQL was used
                    if sql_queries:
                        st.session_state.query_history.extend(sql_queries)
                    
                    # Rerun to show the new message
                    st.rerun()
    
    with viz_col:
        st.subheader("📊 Analysis")
        
        if st.session_state.messages:
            last_msg = st.session_state.messages[-1]
            if last_msg["role"] == "assistant":
                # Response metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Response Time", last_msg.get('response_time', 'N/A'))
                with col2:
                    st.metric("SQL Queries", len(last_msg.get('sql_queries', [])))
                with col3:
                    st.metric("Message Length", len(last_msg['content']))
                
                # Try to display data if the response contains tabular data
                try:
                    # Look for patterns that might indicate tabular data
                    if "Found" in last_msg['content'] and "row(s)" in last_msg['content']:
                        # Extract and display as table
                        lines = last_msg['content'].split('\n')
                        data_lines = [line for line in lines if '  ' in line]
                        if data_lines:
                            st.markdown("**📋 Results Preview:**")
                            # Create a simple dataframe from the text
                            # This is a simplified example - you might want better parsing
                            st.code(last_msg['content'])
                except:
                    pass

# Helper functions
def get_database_stats(db_path):
    """Get basic statistics about the database"""
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        # Get row counts
        total_rows = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            total_rows += cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'table_count': len(tables),
            'tables': tables,
            'total_rows': total_rows
        }
    except:
        return {'table_count': 0, 'tables': [], 'total_rows': 0}

def extract_sql_queries(text):
    """Extract SQL queries from response text"""
    # Look for patterns that might indicate SQL
    sql_patterns = [
        r'SELECT.*?FROM.*?(?:;|$)',
        r'select.*?from.*?(?:;|$)',
        r'PRAGMA.*?;',
        r'pragma.*?;'
    ]
    
    queries = []
    for pattern in sql_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        queries.extend([m.strip() for m in matches if len(m.strip()) > 10])
    
    return list(set(queries))  # Remove duplicates