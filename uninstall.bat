@echo off
set "TARGET_DIR=C:\MAAS"

echo Are you sure you want to uninstall MAAS?
echo This will delete the application but KEEP your data in C:\MAAS\data
pause

:: 1. Remove Shortcut
if exist "%USERPROFILE%\Desktop\MAAS.lnk" del "%USERPROFILE%\Desktop\MAAS.lnk"

:: 2. Remove App Files (Keep data)
cd /d "%TARGET_DIR%"
if exist app rmdir /s /q app
if exist frontend rmdir /s /q frontend
if exist scripts rmdir /s /q scripts
del *.py
del *.vbs
del *.bat
del *.yaml
del *.txt
del *.ini

echo.
echo Uninstallation Complete.
echo Data folder has been preserved at %TARGET_DIR%\data
pause
