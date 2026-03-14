import os
from typing import Optional
from dotenv import load_dotenv

# Gemini + LangChain imports
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from src.schema import DatabaseSchema
from src.tools import DatabaseTools

load_dotenv()

class SQLAgent:
    def __init__(self, db_path: str, llm_type: str = "gemini"):
        self.db_path = db_path
        self.schema = DatabaseSchema(db_path)
        self.db_tools = DatabaseTools(db_path)
        self.llm = self._initialize_llm(llm_type)
        self.agent = self._create_agent()

    def _initialize_llm(self, llm_type: str, temperature: float = 0.1):
        if llm_type == "gemini":
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=temperature,  # Use the passed temperature
                convert_system_message_to_human=True
            )
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")
            
    def _create_agent(self):
        tools = self.db_tools.get_tools()
        memory = MemorySaver()
        
        # Gemini works well with clear system prompts
        system_prompt = """You are a database assistant. You have tools to query a SQLite database.
        
When asked a question:
1. Use get_table_info() first to see available tables
2. If needed, use get_table_sample() to understand data structure
3. Write and execute SQL queries using execute_read_only_query()
4. Provide clear answers based on the results

Only use SELECT queries (read-only)."""
        
        agent = create_agent(
            model=self.llm,
            tools=tools,
            checkpointer=memory,
            system_prompt=system_prompt,
            name="sql_agent",
            debug=False
        )
        return agent

    def ask(self, question: str) -> str:
        """Ask a question to the agent"""
        try:
            messages = [HumanMessage(content=question)]
            
            response = self.agent.invoke(
                {"messages": messages},
                config={
                    "configurable": {
                        "thread_id": "1",
                        "checkpoint_ns": "",
                        "checkpoint_id": None
                    }
                }
            )
            
            if response and "messages" in response and response["messages"]:
                last_message = response["messages"][-1]
                
                # Handle different response formats from Gemini
                if hasattr(last_message, 'content'):
                    # If it's a list of content parts (Gemini format)
                    if isinstance(last_message.content, list):
                        text_parts = []
                        for part in last_message.content:
                            if isinstance(part, dict) and part.get('type') == 'text':
                                text_parts.append(part.get('text', ''))
                            elif isinstance(part, str):
                                text_parts.append(part)
                        return ' '.join(text_parts)
                    # If it's a simple string
                    else:
                        return str(last_message.content)
            
            return "No response from agent."
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"
    
    def close(self):
        pass