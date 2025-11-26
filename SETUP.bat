@echo off
echo KyleH System Monitor - Quick Setup
echo ====================================
echo.

echo Installing dependencies...
python setup.py

echo.
echo Running component test...
python test.py

echo.
echo Setup complete!
echo.
echo To start monitoring:
echo   python monitor.py
echo.
echo To install as Windows service (requires Admin):
echo   python install_service.py
echo.
pause
