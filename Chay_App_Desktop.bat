@echo off
chcp 65001 > nul
title CapCut AI - TTS & STT Studio
echo ===================================================
echo     CapCut AI - TTS & STT Studio Desktop App
echo ===================================================
echo.
echo Đang khởi động ứng dụng...
echo.

cd /d "%~dp0"
python app_gui.py

if %errorlevel% neq 0 (
    echo.
    echo Gặp lỗi khi khởi động. Đang thử chạy chế độ Web Server...
    python server.py
    pause
)
