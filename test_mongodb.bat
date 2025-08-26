@echo off
title Test MongoDB Atlas Connection
color 0B

echo.
echo ========================================
echo   🔍 Test MongoDB Atlas Connection
echo ========================================
echo.

echo 🚀 Testing connection to MongoDB Atlas...
echo 📡 URI: mongodb+srv://doorlock_user:****@doorlock-use.xvg7w8s.mongodb.net/
echo.

python test_mongodb_connection.py

echo.
echo 🔍 Connection test completed!
echo.

pause
