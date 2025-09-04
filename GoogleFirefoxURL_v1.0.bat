@echo off
chcp 65001 > nul
echo.
python3 banner.py
echo.
echo [*] 目前版本为 v1.0
echo.
echo [*] 开发作者为 辉小鱼
echo.
start cmd /k "python3 FireFoxURL.py -f domain.txt"
echo.
start cmd /k "python3 GoogleURL.py -f domain.txt"
echo.
echo.
pause > nul