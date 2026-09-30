@echo off
setlocal EnableExtensions
title Group 9 - Step 2: run the pipeline and compare
cd /d "%~dp0.."

echo.
echo  ============================================================
echo   Group 9 project - Step 2: run the pipeline and compare
echo  ============================================================
echo   Reruns the full P-01 analysis on this computer and checks
echo   that it matches the results committed in the results folder.
echo   Your results folder is not changed: the new run goes to
echo   build\fresh_run. The run needs about 1 GB of free memory,
echo   so close other large programs first.
echo.

if not exist ".venv\Scripts\python.exe" goto :nosetup

".venv\Scripts\python.exe" scripts\fresh_run_check.py
set "RC=%ERRORLEVEL%"
if "%RC%"=="1" goto :failed
if not exist "build\fresh_run\REPORT.md" goto :failed

echo.
if "%RC%"=="0" echo   RESULT: every file matches. The reproduction succeeded.
if "%RC%"=="2" echo   RESULT: some files differ. The report lists them; post it on your task.
echo.
echo   The report is opening in Notepad. Your guided task says where
echo   to paste its table, or you can upload the file itself:
echo   build\fresh_run\REPORT.md
echo.
start "" notepad "build\fresh_run\REPORT.md"
pause
exit /b 0

:nosetup
echo   Run 1-set-up.bat first. It installs what this step needs.
echo.
pause
exit /b 1

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
