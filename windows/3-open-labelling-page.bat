@echo off
setlocal EnableExtensions
title Group 9 - Step 3: open your labelling page
cd /d "%~dp0.."

echo.
echo  ============================================================
echo   Group 9 project - Step 3: open your labelling page
echo  ============================================================
echo   For second raters only. Before your first session, read
echo   docs\validation\ANNOTATION_GUIDELINE.md once, fully.
echo   Never open another rater's label files, such as any file
echo   ending in _jd_r1.csv.
echo.

if not exist ".venv\Scripts\python.exe" goto :nosetup

:askrater
set "RATER="
set /p "RATER=  Your rater id - la for Leticia, ah for Allie, hk for Hina: "
if /i "%RATER%"=="la" (set "RATER=la" & goto :askkind)
if /i "%RATER%"=="ah" (set "RATER=ah" & goto :askkind)
if /i "%RATER%"=="hk" (set "RATER=hk" & goto :askkind)
echo   Please type la, ah, or hk.
goto :askrater

:askkind
set "KIND="
set /p "KIND=  The kind you are labelling - drift, lineage, or signals: "
if /i "%KIND%"=="drift" (set "KIND=drift" & goto :build)
if /i "%KIND%"=="lineage" (set "KIND=lineage" & goto :build)
if /i "%KIND%"=="signals" (set "KIND=signals" & goto :build)
echo   Please type drift, lineage, or signals.
goto :askkind

:build
echo.
echo  [1/2] Preparing your label sheet and reading packets ...
echo        An existing sheet is kept, never overwritten.
".venv\Scripts\python.exe" scripts\annotation_kit.py sheet --rater %RATER% --round 1 --kind %KIND% || goto :failed
echo  [2/2] Writing your labelling page ...
".venv\Scripts\python.exe" scripts\annotation_kit.py ui --rater %RATER% --round 1 --kind %KIND% || goto :failed
set "PAGE=data\annotations\work\label_%KIND%_%RATER%_r1.html"
if not exist "%PAGE%" goto :failed

echo.
echo  ============================================================
echo   Your page is opening in your web browser:
echo   %PAGE%
echo.
echo   - Label in sessions of 30 to 40 minutes. The page remembers
echo     your work in this browser; reopen it with this file.
echo   - At the end of every session, click Download CSV in the page.
echo   - Then drag the downloaded file onto 4-save-my-labels.bat.
echo  ============================================================
echo.
start "" "%PAGE%"
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
