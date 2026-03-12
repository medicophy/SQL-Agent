import os
from typing import Optional
from dotenv import load_dotenv

# LangChain imports
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import Tool

# LLM imports (choose one based on your setup)
# For local LLM with Ollama
from langchain_community.llms import Ollama
# For OpenAI
# from langchain_openai import ChatOpenAI
# For Groq
# from langchain_groq import ChatGroq

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
            # Make sure Ollama is running: 'ollama serve' and 'ollama pull mistral'
            return Ollama(
                model="mistral:7b",  # or "llama3:8b", "codellama:7b"
                temperature=0.1,      # Low temperature for more deterministic SQL
                num_predict=2048      # Max tokens
            )
        elif llm_type == "openai":
            # return ChatOpenAI(
            #     model="gpt-3.5-turbo",
            #     temperature=0.1,
            #     api_key=os.getenv("OPENAI_API_KEY")
            # )
            pass
        elif llm_type == "groq":
            # return ChatGroq(
            #     model="llama3-70b-8192",
            #     temperature=0.1,
            #     api_key=os.getenv("GROQ_API_KEY")
            # )
            pass
        else:
            raise ValueError(f"Unknown LLM type: {llm_type}")
    
    def _create_agent(self):
        """Create the ReAct agent with tools"""
        
        # Define tools
        tools = [
            Tool(
                name="ExecuteSQL",
                func=self.db_tools.execute_read_only_query,
                description="Execute a SQL SELECT query and return results. Only use for SELECT queries."
            ),
            Tool(
                name="GetTableInfo",
                func=self.db_tools.get_table_info,
                description="Get information about database tables. Use this first to understand the schema."
            ),
            Tool(
                name="GetTableSample",
                func=self.db_tools.get_table_sample,
                description="Get sample rows from a table to understand the data format."
            )
        ]
        
        # Create the prompt template
        template = """
        You are a SQL expert assistant. Your task is to answer questions by querying a SQLite database.
        
        Database Schema:
        {schema}
        
        Available tools:
        {tools}
        
        Tool names: {tool_names}
        
        Follow this process:
        1. First, understand the question and what data is needed
        2. Check the schema to identify relevant tables and columns
        3. Look at sample data if needed to understand the format
        4. Write and execute a SQL query
        5. Explain the results in plain English
        
        IMPORTANT: 
        - Only use SELECT queries (read-only)
        - Be careful with JOINs and relationships
        - If a query returns no results, explain why
        
        Previous conversation:
        {chat_history}
        
        Human: {input}
        
        {agent_scratchpad}
        """
        
        prompt = PromptTemplate.from_template(template)
        
        # Create the agent
        agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=prompt
        )
        
        # Create executor with memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,  # Set to False in production
            handle_parsing_errors=True,
            max_iterations=5
        )
        
        return agent_executor
    
    def ask(self, question: str) -> str:
        """Ask a question to the agent"""
        try:
            # Pass schema to the agent through the prompt
            response = self.agent.invoke({
                "input": question,
                "schema": self.schema.get_formatted_schema()
            })
            return response["output"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def close(self):
        """Clean up resources"""
        self.db_tools.close()

# Example usage
if __name__ == "__main__":
    # Test the agent
    agent = SQLAgent("database/chinook.db", llm_type="ollama")
    
    questions = [
        "What tables are in this database?",
        "How many customers do we have?",
        "Show me the top 5 most expensive tracks",
        "Which artist has the most tracks?"
    ]
    
    for q in questions:
        print(f"\n{'='*50}")
        print(f"Question: {q}")
        print(f"{'='*50}")
        answer = agent.ask(q)
        print(f"Answer: {answer}")
    
    agent.close()