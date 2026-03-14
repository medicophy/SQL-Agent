import os
from typing import Optional
from dotenv import load_dotenv

# Modern LangChain imports
from langchain_core.messages import HumanMessage
from langchain.prompts import PromptTemplate
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.llms import Ollama

from src.schema import DatabaseSchema
from src.tools import DatabaseTools

load_dotenv()

class SQLAgent:
    def __init__(self, db_path: str, llm_type: str = "ollama"):
        """
        Initialize the SQL Agent
        
        Args:
            db_path: Path to SQLite database
            llm_type: "ollama", "openai", or "groq"
        """
        self.db_path = db_path
        self.schema = DatabaseSchema(db_path)
        self.db_tools = DatabaseTools(db_path)
        self.llm = self._initialize_llm(llm_type)
        self.agent = self._create_agent()
    
    def _initialize_llm(self, llm_type: str):
        """Initialize the language model"""
        if llm_type == "ollama":
            return Ollama(
                model="mistral:7b",
                temperature=0.1,
                num_predict=2048
            )
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")
    
    def _create_agent(self):
        """Create the agent with tools"""
        
        # Get tools from DatabaseTools (they are already decorated with @tool)
        tools = self.db_tools.get_tools()
        
        # Create memory saver (replaces ConversationBufferMemory)
        memory = MemorySaver()
        
        # Create the agent using the modern factory
        agent = create_agent(
            model=self.llm,
            tools=tools,
            checkpointer=memory,
            name="sql_agent",
            debug=False  # Set to True to see detailed logs
        )
        
        return agent
    
    def ask(self, question: str) -> str:
        """Ask a question to the agent"""
        try:
            # Create message with schema context
            schema_context = self.schema.get_formatted_schema()
            full_question = f"""Database Schema:
{schema_context}

Question: {question}

Answer the question by using the available tools to query the database.
Only use SELECT queries (read-only).
First check table info to understand the schema, then write and execute SQL queries."""

            # Invoke the agent with the question
            response = self.agent.invoke({
                "messages": [HumanMessage(content=full_question)]
            })
            
            # Extract the last message (the answer)
            if response and "messages" in response and response["messages"]:
                return response["messages"][-1].content
            return "No response from agent."
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def close(self):
        """Clean up resources"""
        pass

if __name__ == "__main__":
    # Test the agent
    print("Initializing SQL Agent...")
    agent = SQLAgent("database/chinook.db", llm_type="ollama")
    
    test_questions = [
        "What tables are in this database?",
        "How many artists are there?",
        "Show me the first 3 artists"
    ]
    
    for q in test_questions:
        print(f"\n{'='*50}")
        print(f"Question: {q}")
        print(f"{'='*50}")
        answer = agent.ask(q)
        print(f"Answer: {answer}")
    
    agent.close()