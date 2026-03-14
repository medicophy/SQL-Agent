@echo off
echo Activating SQL Agent virtual environment...
call .\venv\Scripts\activate
echo.
echo ✅ Virtual environment activated!
echo.
echo Current directory: %CD%
echo Python: %VIRTUAL_ENV%
echo.
echo Commands:
echo   streamlit run src/app.py
echo   python main.py
echo   deactivate