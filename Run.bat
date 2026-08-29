@echo off
cd /d "%~dp0"
echo Computing intersection of a line with a unit sphere centered on the origin...
python 104intersection 1 0 0 0 1 0 0 1
echo.
pause
