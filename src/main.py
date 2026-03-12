#!/usr/bin/env python3
"""
SQL Agent - Text-to-SQL Assistant
Run with: streamlit run main.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def main():
    """Main entry point"""
    # Check if we're running in streamlit
    if 'STREAMLIT_SCRIPT_NAME' in os.environ:
        # Import and run Streamlit app
        from src.app import main as streamlit_main
        streamlit_main()
    else:
        # Run command line version
        from src.agent import SQLAgent
        
        print("🤖 SQL Agent - Command Line Interface")
        print("=" * 50)
        
        # Get database path
        db_path = input("Enter database path (default: database/chinook.db): ").strip()
        if not db_path:
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