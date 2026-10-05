@echo off
rem Hueco Mundo HUD - one-click update.
rem Pulls the latest version from GitHub, rebuilds the HUD and installs it into TF2's custom folder.
rem The project folder itself is the HUD: dropped into tf\custom (e.g. as "HuecoMundoHUD-main") it is built
rem in place; anywhere else the HUD is copied into tf\custom\huecomundo-hud.
set "BRANCH=main"

cd /d "%~dp0"
title Hueco Mundo HUD - update

echo.
echo  TF2 must be closed. Press any key to continue.
pause >nul

echo.
echo  [1/2] Pulling the latest changes from GitHub...
rem A copy without its git data (ZIP download, folder copied without the hidden .git folder) is linked back
rem to GitHub first. A lone update.bat away from the project folder stops here instead.
if exist ".git" goto pull
if not exist "tools\build.py" goto wrongplace
echo  This folder has no git data yet, linking it to GitHub...
git init -q
git remote add origin https://github.com/Ingalther/HuecoMundoHUD.git
git fetch origin %BRANCH%
if errorlevel 1 goto failed
git checkout -f -B %BRANCH% origin/%BRANCH%
if errorlevel 1 goto failed
:pull
rem build.py regenerates the HUD parts (resource, scripts, materials, info.vdf) every run. Local
rem differences in them are reset first so they cannot block the pull; nothing is lost, step 2 rebuilds them.
rem (huecomundo-hud is where older versions kept them.)
git checkout -- resource scripts materials info.vdf 2>nul
git clean -fdq -- resource scripts materials cfg huecomundo-hud 2>nul
git checkout -- huecomundo-hud 2>nul
git fetch origin %BRANCH%
if errorlevel 1 goto failed
git reset -q --hard origin/%BRANCH%
if errorlevel 1 goto failed

echo.
echo  [2/2] Building the HUD and installing it into TF2...
set "PY=python"
python --version >nul 2>&1 || set "PY=py"
%PY% tools\build.py --install
if errorlevel 1 goto failed

echo.
echo  Done! You can start TF2.
pause
exit /b 0

:wrongplace
echo.
echo  This update.bat is not inside the Hueco Mundo HUD project folder.
echo  Run the update.bat that sits next to the "tools" folder, not a copy of it.
echo  Folder used now: %CD%
pause
exit /b 1

:failed
echo.
echo  Something went wrong. Send a screenshot of this window when you report the problem.
pause
exit /b 1
