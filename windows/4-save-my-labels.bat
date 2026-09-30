@echo off
setlocal EnableExtensions
title Group 9 - Step 4: check and save my labels
cd /d "%~dp0.."

echo.
echo  ============================================================
echo   Group 9 project - Step 4: check and save my labels
echo  ============================================================
echo   Checks the CSV you downloaded from your labelling page and
echo   saves it into data\annotations. Run it after every session.
echo.

if not exist ".venv\Scripts\python.exe" goto :nosetup

set "CSV=%~1"
if defined CSV goto :import
echo   Tip: next time, drag the downloaded CSV onto this .bat file.
echo.
set /p "CSV=  Or paste the full path of the downloaded CSV here: "
if not defined CSV goto :nofile
set "CSV=%CSV:"=%"

:import
if not exist "%CSV%" goto :nofile
echo.
".venv\Scripts\python.exe" scripts\annotation_kit.py import "%CSV%" || goto :badfile

echo.
echo  ============================================================
echo   Saved. Your labels are checked and stored in data\annotations.
echo   That folder is opening now.
echo.
echo   When the whole kind is labelled, upload ONLY your own file,
echo   for example drift_la_r1.csv, to data/annotations/ on GitHub:
echo   docs\NO_GIT_GUIDE.md, recipe 5. Until then, keep labelling
echo   and run this again after each session.
echo  ============================================================
echo.
start "" explorer "data\annotations"
pause
exit /b 0

:badfile
echo.
echo   The labels were not saved. The lines above say what to fix,
echo   for example a missing reason in the notes. Fix it in the
echo   labelling page, click Download CSV again, and retry.
echo.
pause
exit /b 1

:nofile
echo   No file found at: %CSV%
echo.
pause
exit /b 1

:nosetup
echo   Run 1-set-up.bat first. It installs what this step needs.
echo.
pause
exit /b 1
