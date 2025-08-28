@echo off
echo ========================================
echo   Multi-Environment Door Lock System
echo ========================================
echo.
echo Available Environments:
echo 1. School/College (with uniform detection)
echo 2. Hotel (face recognition only)
echo 3. Office (face recognition only)
echo 4. Hospital (medical uniform detection)
echo 5. Factory (safety uniform detection)
echo.
echo Starting Admin Panel...
echo.

python -m streamlit run admin_panel.py

pause
