@echo off
title Install MongoDB Dependencies
color 0E

echo.
echo ========================================
echo   📦 Installing MongoDB Dependencies
echo ========================================
echo.

echo 🔧 Installing required packages...
echo.

pip install --user pymongo certifi

echo.
echo ✅ MongoDB dependencies installed!
echo.
echo 🚀 You can now run the PC Detection System
echo    with MongoDB Atlas connection!
echo.

pause
