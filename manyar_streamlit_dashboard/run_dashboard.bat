@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Membuat virtual environment...
    python -m venv .venv
)
call ".venv\Scripts\activate.bat"
echo Memasang dependensi dashboard...
python -m pip install -r requirements.txt
echo Menjalankan Manyar Auto Service BI Dashboard...
python -m streamlit run app.py
pause
