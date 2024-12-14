@echo off
:: In Windows, Install by creating a hard link

set addons21=%appdata%\Anki2\addons21

echo "Current dir: %cd%"
echo "addons21 dir: %addons21%"
echo "==================================================="

echo Creating Hard Link...
mklink /j "%addons21%\Dict2Anki" "%cd%"

echo.
echo Done!

PAUSE
