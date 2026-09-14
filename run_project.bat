@echo off
setlocal

cd /d "%~dp0"

where py >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python Launcher was not found.
    echo Install Python 3.9 or newer with Tkinter, then run this file again.
    pause
    exit /b 1
)

py -3 -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Tkinter is not available in the selected Python installation.
    echo Install Python with the Tcl/Tk option enabled, then run this file again.
    pause
    exit /b 1
)

echo Starting the single-file Pile-Supported Embankment Designer application...
py -3 standalone_app.py
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo The application exited with code %EXIT_CODE%.
    pause
)

exit /b %EXIT_CODE%