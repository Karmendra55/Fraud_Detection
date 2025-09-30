@echo off
title 🚀 Fraud Detection App Launcher

echo ================================
echo      FRAUD DETECTION APP LAUNCHER
echo ================================
echo.
echo Checking environment...

:: Run Streamlit
echo Streamlit found!
echo Launching app...
echo.
streamlit run main.py


:: Keep the window open after closing the app
echo.
echo Streamlit has exited. Press any key to close this window.
pause >nul

