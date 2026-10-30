@echo off
rem Hueco Mundo HUD - one-click update.
rem Pulls the latest version from GitHub, rebuilds the HUD and installs it into TF2's custom folder.
rem The project folder itself is the HUD: dropped into tf\custom (e.g. as "HuecoMundoHUD-main") it is built
rem in place; anywhere else the HUD is copied into tf\custom\huecomundo-hud.
set "BRANCH=main"

cd /d "%~dp0"
title Hueco Mundo HUD - update
if not exist ".git" if not exist "tools\build.py" goto wrongplace

echo.
echo  TF2 must be closed. Press any key to continue.
pause >nul
rem Git, Python 3, Pillow and numpy are checked before anything changes;
rem a missing one is named with where to get it.
call :tools
if errorlevel 1 exit /b 1
echo.
echo  [1/2] Pulling the latest changes from GitHub...
if exist ".git" goto pull
echo  This folder has no git data yet, linking it to GitHub...
git init -q
git remote add origin https://github.com/Ingalther/HuecoMundoHUD.git
git fetch origin %BRANCH% || goto nofetch
git checkout -f -B %BRANCH% origin/%BRANCH% && goto pull || goto nofiles
if errorlevel 1 goto nofiles

:pull
rem Local differences in the HUD parts (resource, scripts, materials, info.vdf) are reset first so they
rem cannot block the pull; nothing is lost, step 2 rebuilds them. Older versions kept them in huecomundo-hud.
git checkout -- resource scripts materials info.vdf 2>nul
git clean -fdq -- resource scripts materials cfg huecomundo-hud 2>nul
git checkout -- huecomundo-hud 2>nul
git fetch origin %BRANCH% || goto nofetch
rem Git now swaps this file.
git reset -q --hard origin/%BRANCH% && goto build || goto nofiles
if errorlevel 1 goto nofiles

:build
rem update.bat 1.0 and 1.1 read on at byte 1068 or 1631 of this file (CRLF) once git has replaced it under
rem them, so the two "if errorlevel 1 goto nofiles" lines above must keep starting there: a change above
rem them keeps its byte count. From 1.2 on, update.bat goes on by label right after git (goto pull, goto
rem build), so the labels pull, build, nofetch and nofiles must stay, and so must the ones below.
call :tools
if errorlevel 1 exit /b 1
echo.
echo  [2/2] Building the HUD and installing it into TF2...
%PY% tools\build.py --install
if errorlevel 1 goto nobuild
echo.
echo  Done! You can start TF2.
pause
exit /b 0

:tools
rem Finds Python 3 (PY) and checks for Git, Python 3, Pillow and numpy. When one is missing it says which
rem and how to get it, and returns 1.
set "PY="
set "HM_NOGIT="
set "HM_NOPKG="
git --version >nul 2>&1 || set "HM_NOGIT=1"
python -c "import sys; sys.exit(sys.version_info[0] != 3)" >nul 2>&1 && set "PY=python"
if not defined PY py -3 -c "import sys" >nul 2>&1 && set "PY=py -3"
if defined PY %PY% -c "import PIL, numpy" >nul 2>&1 || set "HM_NOPKG=1"
if not defined HM_NOGIT if defined PY if not defined HM_NOPKG exit /b 0
set "HM_PIP=%PY%"
if not defined PY set "HM_PIP=py"
if not defined PY set "HM_NOPKG=1"
echo.
echo  update.bat needs a few free tools to download and build the HUD, and this PC is missing:
if defined HM_NOGIT echo   - Git: get it from https://git-scm.com/download/win and install it with the default options.
if not defined PY echo   - Python 3: get it from https://www.python.org/downloads/ and install it with the default options.
if defined HM_NOPKG echo   - Pillow and numpy, two add-ons for Python: open a Command Prompt and run   %HM_PIP% -m pip install pillow numpy
echo  Then run update.bat again.
echo.
echo  Without these tools you can update by hand: download the newest ZIP from
echo  https://github.com/Ingalther/HuecoMundoHUD/releases/latest and put its folder into tf\custom
echo  in place of this one.
pause
exit /b 1

:wrongplace
echo.
echo  This update.bat is not inside the Hueco Mundo HUD project folder.
echo  Run the update.bat that sits next to the "tools" folder, not a copy of it.
echo  Folder used now: %CD%
pause
exit /b 1

:nofetch
echo.
echo  Git could not download the new version from GitHub; the lines above say why. Most often the internet
echo  connection is down, or a firewall or antivirus blocks Git. Fix that, then run update.bat again.
goto report

:nofiles
echo.
echo  Git could not put the new version in place; the lines above say why. Most often a program still has
echo  files of this folder open (TF2, an editor, an antivirus scan): close it, then run update.bat again.
goto report

:nobuild
echo.
echo  The new version is downloaded, but building the HUD failed; the lines above say why.
goto report

:failed
:report
echo  If it keeps failing, send a screenshot of this window when you report the problem.
pause
exit /b 1
