@echo off
setlocal EnableExtensions
title Group 9 - Step 1: set up this computer
cd /d "%~dp0.."

echo.
echo  ============================================================
echo   Group 9 project - Step 1: set up this computer
echo  ============================================================
echo   Project folder: %CD%
echo.
echo   This installs the project's Python packages into a private
echo   folder named .venv and downloads the GitSkills sample,
echo   about 90 MB. It changes nothing outside this project folder.
echo   You can run it again at any time; finished steps are reused.
echo.

echo "%CD%" | find /i "OneDrive" >nul
if errorlevel 1 goto :python
echo   WARNING: this folder is inside OneDrive. OneDrive can lock the
echo   files the project creates. Best: move the whole project folder
echo   to C:\dev\ and double-click this file again from there.
echo.
choice /c YN /m "  Continue here anyway"
if errorlevel 2 exit /b 1

:python
set "PY="
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if defined PY goto :venv
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if not errorlevel 1 set "PY=python"
if defined PY goto :venv
echo   Python 3.11 or newer was not found on this computer.
echo.
echo   1. Install it from https://www.python.org/downloads/
echo      The download page is opening in your browser now.
echo   2. On the first installer screen, tick "Add python.exe to PATH".
echo   3. When it has finished, double-click this file again.
echo.
start "" https://www.python.org/downloads/
pause
exit /b 1

:venv
echo  [1/3] Creating the project environment in .venv ...
if exist ".venv\Scripts\python.exe" goto :install
%PY% -m venv .venv || goto :failed

:install
echo  [2/3] Installing the project's packages. The first time takes a few minutes ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --quiet --upgrade pip || goto :failed
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check --quiet -e . || goto :failed

echo  [3/3] Downloading the GitSkills sample. Skipped if it is already here ...
".venv\Scripts\python.exe" scripts\download_samples.py --dataset gitskills || goto :failed

echo.
echo  ============================================================
echo   Done. This computer is ready.
echo.
echo   Next, depending on your task:
echo     2-run-pipeline.bat          fresh-run check for the review
echo     3-open-labelling-page.bat   labelling, if you are a rater
echo  ============================================================
echo.
pause
exit /b 0

:failed
echo.
echo  ------------------------------------------------------------
echo   Something went wrong in the step above.
echo   Take a screenshot of this window and post it as a comment on
echo   your task on GitHub. Nothing in the project was damaged.
echo  ------------------------------------------------------------
echo.
pause
exit /b 1
