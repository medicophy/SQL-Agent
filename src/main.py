#!/usr/bin/env python3
"""
SQL Agent - Command Line Interface
"""

# Add the parent directory to path so we can import src
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent import SQLAgent

def main():
    """Main entry point for command line interface"""
    print("🤖 SQL Agent - Command Line Interface")
    print("=" * 50)
    
    # Database path
    db_path = "database/chinook.db"
    
    # Initialize agent
    print("\nInitializing agent...")
    agent = SQLAgent(db_path, llm_type="ollama")
    print("Ready! Type 'exit' to quit.\n")
    
    # Interactive loop
    while True:
        question = input("\n❓ Your question: ").strip()
        if question.lower() in ['exit', 'quit', 'q']:
            break
        
        if not question:
            continue
        
        print("\n🤔 Thinking...")
        answer = agent.ask(question)
        print(f"\n💡 Answer: {answer}")
    
    agent.close()
    print("\nGoodbye! 👋")

if __name__ == "__main__":
    main()