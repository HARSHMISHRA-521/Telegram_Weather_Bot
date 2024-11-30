@echo off
echo Starting Admin Panel...
start cmd /k "python admin_panel.py"

echo Starting Telegram Bot...
start cmd /k "python bot.py"

echo Both Admin Panel and Telegram Bot are running.
pause
