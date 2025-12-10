@echo off
set "TARGET_DIR=C:\MAAS"
set "SOURCE_DIR=%~dp0"

echo Installing Mom's Accounting Automation System...
echo Source: %SOURCE_DIR%
echo Target: %TARGET_DIR%

:: 1. Create Directory
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

:: 2. Copy Files (Excluding git, venv, temporary files)
xcopy "%SOURCE_DIR%*" "%TARGET_DIR%\" /E /Y /I /Q /EXCLUDE:install_exclude.txt

:: 3. Create Shortcut (using temporary PowerShell script)
set "S_PATH=%USERPROFILE%\Desktop\MAAS.lnk"
set "S_TARGET=%TARGET_DIR%\start_maas.vbs"
set "S_ICON=%TARGET_DIR%\frontend\static\favicon.ico"
set "S_WORK=%TARGET_DIR%"

echo Creating Desktop Shortcut...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%S_PATH%');$s.TargetPath='%S_TARGET%';$s.WorkingDirectory='%S_WORK%';$s.IconLocation='%S_ICON%';$s.Save()"

echo.
echo Installation Complete!
echo You can now launch MAAS from your Desktop.
pause
