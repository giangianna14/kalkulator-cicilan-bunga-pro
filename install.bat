@echo off
echo ================================
echo KALKULATOR CICILAN & BUNGA PRO
echo ================================
echo.
echo Menginstall dependencies...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python tidak terdeteksi!
    echo Silakan install Python terlebih dahulu dari https://python.org
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip tidak terdeteksi!
    echo Silakan install pip terlebih dahulu
    pause
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ERROR: Gagal menginstall dependencies!
    pause
    exit /b 1
)

echo.
echo ================================
echo INSTALASI BERHASIL!
echo ================================
echo.
echo Untuk menjalankan aplikasi, ketik:
echo streamlit run app.py
echo.
echo Atau double-click file: run_app.bat
echo.
pause
