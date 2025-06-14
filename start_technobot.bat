@echo off
title TECHNOBOT - Corporate Safe Startup
color 0A

echo.
echo ========================================
echo   🤖 TECHNOBOT - CORPORATE SAFE MODE
echo ========================================
echo.
echo 🔒 Chế độ an toàn cho môi trường công ty
echo 📍 Không tạo share link (Trellix safe)
echo 🌐 Chỉ chạy local trên máy này
echo.

REM Check if Python 3.11 is available
python3.11 --version >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Tìm thấy Python 3.11
    set PYTHON_CMD=python3.11
) else (
    python --version | findstr "3.11" >nul 2>&1
    if %errorlevel% == 0 (
        echo ✅ Tìm thấy Python 3.11
        set PYTHON_CMD=python
    ) else (
        echo ❌ Không tìm thấy Python 3.11
        echo Vui lòng cài đặt Python 3.11
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Khởi động TECHNOBOT...
echo ⚠️ Để dừng: Nhấn Ctrl+C
echo.

REM Set environment variables for safe mode
set GRADIO_SHARE=False
set GRADIO_SERVER_NAME=127.0.0.1

REM Start TECHNOBOT
%PYTHON_CMD% start_technobot.py

echo.
echo 🛑 TECHNOBOT đã dừng
pause 