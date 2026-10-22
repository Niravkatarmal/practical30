@echo off
echo ========================================================
echo   Building Personal Expense Manager Windows Executable
echo ========================================================
echo.

:: Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller not detected. Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PyInstaller. Please check internet connection.
        pause
        exit /b %errorlevel%
    )
)

echo Building standalone single-file Windows executable...
python -m PyInstaller --onefile --windowed --name "ExpenseManager" --exclude-module scipy --exclude-module pandas --exclude-module IPython --exclude-module notebook --exclude-module nbformat --exclude-module tornado --exclude-module jupyter --exclude-module PIL --exclude-module jinja2 --exclude-module lark --clean app.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo   BUILD SUCCESSFUL!
    echo   Executable located at: dist\ExpenseManager.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Build failed. Please review the output above.
)

pause
