@echo off
cd /d %~dp0
echo CoinBot baslatiliyor... panel: http://127.0.0.1:8787
python dashboard.py
pause
