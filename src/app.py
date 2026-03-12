import streamlit as st
import pandas as pd
from src.agent import SQLAgent
import time

# Page config
st.set_page_config(
    page_title="SQL Agent Assistant",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 Text-to-SQL Agent")
st.markdown("""
Ask questions about your database in plain English, and I'll convert them to SQL and show you the results!
""")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Database selection
    db_path = st.text_input(
        "Database Path",
        value="database/chinook.db",
        help="Path to your SQLite database file"
    )
    
    # LLM selection
    llm_type = st.selectbox(
        "LLM Backend",
        options=["ollama", "openai", "groq"],
        index=0,
        help="Choose which LLM to use"
    )
    
    if llm_type == "ollama":
        st.info("Make sure Ollama is running with: `ollama serve`")
    
    # Initialize agent button
    if st.button("🚀 Initialize Agent"):
        with st.spinner("Initializing agent..."):
            try:
                st.session_state.agent = SQLAgent(db_path, llm_type)
                st.session_state.schema = st.session_state.agent.schema.get_formatted_schema()
                st.success("Agent ready!")
            except Exception as e:
                st.error(f"Failed to initialize: {str(e)}")
    
    # Show schema toggle
    if st.checkbox("Show Database Schema"):
        if 'schema' in st.session_state:
            st.code(st.session_state.schema, language="sql")
        else:
            st.warning("Initialize agent first")

# Main chat interface
if 'agent' not in st.session_state:
    st.info("👈 Please initialize the agent from the sidebar first")
else:
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # If there's a dataframe to display (for assistant responses)
            if "dataframe" in message:
                st.dataframe(message["dataframe"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Show thinking process in expander
                with st.expander("See agent's reasoning"):
                    st.write("Agent is working...")
                    # We can't easily capture intermediate steps here,
                    # but in production you'd want to stream them
                
                # Get answer
                response = st.session_state.agent.ask(prompt)
                
                # Try to parse if response contains table data
                try:
                    # Look for SQL results in the response
                    if "Found" in response and "row(s)" in response:
                        # Extract and display as dataframe if possible
                        st.markdown(response.split("\n")[0])  # Show summary
                        # The rest of the response might be tabular data
                        # You could parse it into a dataframe here
                    else:
                        st.markdown(response)
                except:
                    st.markdown(response)
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })

# Footer
st.markdown("---")
st.markdown("Built with LangChain + Streamlit")