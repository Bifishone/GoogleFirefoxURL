@echo off
chcp 65001 > nul
echo.
python3 GoogleURL.py -f domain.txt
echo.
pause > nul