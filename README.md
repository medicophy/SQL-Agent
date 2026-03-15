🤖 SQL Agent - Talk to Your Database in Plain English

https://img.shields.io/badge/Python-3.9+-blue
https://img.shields.io/badge/LangChain-1.2.12-green
https://img.shields.io/badge/Gemini-2.5--flash-orange
https://img.shields.io/badge/Streamlit-1.29.0-red

Turn natural language into SQL queries using Google's Gemini AI. Ask questions, get answers—no SQL knowledge required!

✨ What It Does
text
You: "How many artists are in the database?"
Agent: "There are 275 artists in the database."

You: "Show me the top 5 customers"
Agent: "1. Helena Holy - $49.62
       2. Richard Cunningham - $47.62
       3. Luis Rojas - $46.62..."
🛠️ Tech Stack
LangChain - Agent orchestration

Gemini 2.5 Flash - AI model

Streamlit - Web interface

SQLite - Database

🚀 Quick Start
bash
# 1. Clone and setup
git clone <your-repo>
cd sql-agent
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 2. Add your Gemini API key to .env
echo "GOOGLE_API_KEY=your_key_here" > .env

# 3. Run it!
streamlit run src/app.py
📸 Glimpse
https://via.placeholder.com/600x400?text=Ask+Questions+Get+Answers

🎯 Example Questions
"What tables are in this database?"

"How many customers from Brazil?"

"Show me the longest tracks"

"Which artist has the most albums?"

📁 Structure
text
sql-agent/
├── src/
│   ├── app.py        # Web UI
│   ├── agent.py      # AI agent logic
│   ├── tools.py      # Database tools
│   └── schema.py     # Schema extractor
├── database/         # Your .db files
├── requirements.txt
└── .env             # API key

Built with ❤️ using LangChain + Gemini