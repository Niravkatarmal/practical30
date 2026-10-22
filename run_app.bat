@echo off
title Personal Expense Manager
python app.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with an error.
    pause
)
