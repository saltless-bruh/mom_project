# MAAS Deployment Guide: Auto-Start Desktop Application

**Document Version:** 1.0  
**Last Updated:** December 5, 2025  
**Target User:** Developers deploying MAAS for non-technical users

---

## Table of Contents

1. [Overview](#overview)
2. [Phase 1: PWA Deployment](#phase-1-pwa-deployment)
3. [Phase 2-3: Electron Deployment](#phase-2-3-electron-deployment)
4. [Installation Procedures](#installation-procedures)
5. [Testing Procedures](#testing-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Overview

### Critical Requirement

**The end user (mom) cannot use terminal commands or run Python scripts manually.**

The system MUST provide:
- ✅ One-click desktop icon launch
- ✅ No visible terminal/console windows
- ✅ No manual commands required
- ✅ Automatic backend startup
- ✅ User-friendly error messages

### Deployment Strategy

**Phase 1 (MVP):** Progressive Web App (PWA) with VBScript launcher  
**Phase 2-3:** Electron desktop application with embedded Python backend

### Why Two Phases?

**Phase 1 (PWA):**
- ✅ Faster to implement (2-3 days)
- ✅ Proves concept with minimal overhead
- ✅ No Node.js/Electron learning curve
- ❌ Still uses browser (Chrome required)
- ❌ Less polished UX

**Phase 2-3 (Electron):**
- ✅ Native desktop application
- ✅ Professional UX (no browser chrome)
- ✅ Auto-update support
- ✅ System tray integration
- ❌ More complex to build (1 week)
- ❌ Larger package size

---

## Phase 1: PWA Deployment

### Architecture Overview

```
Desktop Shortcut → start_maas.vbs → Python Backend (hidden) → Chrome --app mode
                                          ↓
                                    localhost:8765
                                          ↓
                                    Vue.js Frontend
```

### Components

1. **`start_maas.vbs`** - Launcher script (double-click this)
2. **`run.py`** - FastAPI backend entry point (hidden)
3. **`stop_maas.vbs`** - Clean shutdown script
4. **`install.bat`** - Installer script
5. **Embedded Python** - Self-contained Python runtime

### File Structure

```
C:\MAAS\
├── python\                 # Embedded Python 3.9 runtime
│   ├── python.exe
│   ├── python39.dll
│   ├── python39._pth       # Import configuration
│   └── Lib\                # Standard library
│       └── site-packages\  # Dependencies (fastapi, uvicorn, etc.)
├── app\                    # Application code
│   ├── api\
│   ├── models\
│   ├── services\
│   └── utils\
├── frontend\               # Vue.js frontend
│   ├── static\
│   └── templates\
├── data\                   # User data (invoices, database)
│   ├── invoices\
│   ├── screenshots\
│   └── maas.db
├── logs\                   # Application logs
├── config.yaml             # Configuration file
├── run.py                  # Backend entry point
├── start_maas.vbs          # Launcher script
├── stop_maas.vbs           # Shutdown script
└── README.txt              # User instructions
```

---

## Phase 1 Implementation Guide

### Step 1: Create Launcher Script

**File:** `start_maas.vbs`

```vbscript
' MAAS Launcher Script - Starts backend invisibly and opens browser
' Author: MAAS Development Team
' Version: 1.0
' Last Updated: 2025-12-05

Option Explicit

Dim objShell, objFSO, objHTTP
Dim pythonExe, scriptDir, backendScript, chromeExe
Dim maxRetries, retryCount, healthCheckPassed
Dim portInUse

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get script directory
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Paths
pythonExe = scriptDir & "\python\python.exe"
backendScript = scriptDir & "\run.py"
chromeExe = "C:\Program Files\Google\Chrome\Application\chrome.exe"

' Check if backend already running
portInUse = IsPortInUse(8765)
If portInUse Then
    ' Backend already running, just open browser
    WScript.Echo "MAAS is already running. Opening interface..."
    Call OpenBrowser(chromeExe)
    WScript.Quit 0
End If

' Validate files exist
If Not objFSO.FileExists(pythonExe) Then
    MsgBox "Error: Python not found at: " & pythonExe & vbCrLf & vbCrLf & _
           "Please reinstall MAAS.", vbCritical, "MAAS Error"
    WScript.Quit 1
End If

If Not objFSO.FileExists(backendScript) Then
    MsgBox "Error: Backend script not found at: " & backendScript & vbCrLf & vbCrLf & _
           "Please reinstall MAAS.", vbCritical, "MAAS Error"
    WScript.Quit 1
End If

' Start backend invisibly
On Error Resume Next
objShell.Run """" & pythonExe & """ """ & backendScript & """", 0, False
If Err.Number <> 0 Then
    MsgBox "Error starting backend: " & Err.Description, vbCritical, "MAAS Error"
    WScript.Quit 1
End If
On Error GoTo 0

' Wait for backend to be ready
maxRetries = 30  ' 30 seconds timeout
retryCount = 0
healthCheckPassed = False

WScript.Echo "Starting MAAS backend..."

Do While retryCount < maxRetries And Not healthCheckPassed
    WScript.Sleep 1000  ' Wait 1 second
    retryCount = retryCount + 1
    
    ' Check health endpoint
    On Error Resume Next
    Set objHTTP = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    objHTTP.Open "GET", "http://localhost:8765/health", False
    objHTTP.setTimeouts 1000, 1000, 1000, 1000  ' 1 second timeouts
    objHTTP.Send
    
    If Err.Number = 0 And objHTTP.Status = 200 Then
        healthCheckPassed = True
    End If
    On Error GoTo 0
    
    Set objHTTP = Nothing
Loop

If Not healthCheckPassed Then
    MsgBox "Error: Backend failed to start after " & maxRetries & " seconds." & vbCrLf & vbCrLf & _
           "Please check logs\maas.log for details.", vbCritical, "MAAS Error"
    WScript.Quit 1
End If

' Backend ready, open browser
WScript.Echo "MAAS is ready! Opening interface..."
Call OpenBrowser(chromeExe)

WScript.Quit 0

'-----------------------------------
' Functions
'-----------------------------------

Function IsPortInUse(port)
    ' Check if port is already in use
    Dim objHTTP
    On Error Resume Next
    Set objHTTP = CreateObject("MSXML2.ServerXMLHTTP.6.0")
    objHTTP.Open "GET", "http://localhost:" & port & "/health", False
    objHTTP.setTimeouts 500, 500, 500, 500
    objHTTP.Send
    
    If Err.Number = 0 And objHTTP.Status = 200 Then
        IsPortInUse = True
    Else
        IsPortInUse = False
    End If
    On Error GoTo 0
    Set objHTTP = Nothing
End Function

Sub OpenBrowser(chromeExe)
    ' Open browser in app mode (fullscreen, no URL bar)
    Dim browserCmd
    
    If objFSO.FileExists(chromeExe) Then
        ' Chrome found, use app mode
        browserCmd = """" & chromeExe & """ --app=http://localhost:8765 " & _
                     "--window-size=1280,800 --window-position=100,50"
        objShell.Run browserCmd, 1, False
    Else
        ' Chrome not found, use default browser
        MsgBox "Chrome not found. Opening in default browser." & vbCrLf & vbCrLf & _
               "For best experience, install Google Chrome.", vbInformation, "MAAS"
        objShell.Run "http://localhost:8765", 1, False
    End If
End Sub
```

---

### Step 2: Hide Console in Backend

**File:** `run.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAAS Backend Entry Point
Starts FastAPI server with hidden console window on Windows.
"""

import sys
import logging
from pathlib import Path

# Hide console window on Windows
if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes

    # Get console window handle
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    hwnd = kernel32.GetConsoleWindow()
    
    if hwnd:
        # Hide console window
        user32 = ctypes.WinDLL("user32", use_last_error=True)
        SW_HIDE = 0
        user32.ShowWindow(hwnd, SW_HIDE)

# Set up logging before importing app
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "maas.log"),
        logging.StreamHandler(sys.stdout)  # Still log to stdout for debugging
    ]
)

logger = logging.getLogger(__name__)

# Import and start application
try:
    import uvicorn
    from app.main import app
    
    logger.info("=" * 60)
    logger.info("MAAS Backend Starting")
    logger.info("=" * 60)
    
    # Start server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8765,
        log_level="info",
        access_log=True
    )
    
except Exception as e:
    logger.critical(f"Failed to start backend: {e}", exc_info=True)
    sys.exit(1)
```

---

### Step 3: Create Shutdown Script

**File:** `stop_maas.vbs`

```vbscript
' MAAS Shutdown Script - Cleanly stops backend and closes browser
' Author: MAAS Development Team
' Version: 1.0

Option Explicit

Dim objShell, objWMI, objProcess, colProcesses
Dim pythonProcessFound, chromeProcessFound

Set objShell = CreateObject("WScript.Shell")
Set objWMI = GetObject("winmgmts:\\.\root\cimv2")

pythonProcessFound = False
chromeProcessFound = False

' Kill Python backend processes
Set colProcesses = objWMI.ExecQuery("SELECT * FROM Win32_Process WHERE CommandLine LIKE '%run.py%'")
For Each objProcess in colProcesses
    On Error Resume Next
    objProcess.Terminate()
    If Err.Number = 0 Then
        pythonProcessFound = True
    End If
    On Error GoTo 0
Next

' Kill Chrome processes for localhost:8765
Set colProcesses = objWMI.ExecQuery("SELECT * FROM Win32_Process WHERE Name = 'chrome.exe' AND CommandLine LIKE '%localhost:8765%'")
For Each objProcess in colProcesses
    On Error Resume Next
    objProcess.Terminate()
    If Err.Number = 0 Then
        chromeProcessFound = True
    End If
    On Error GoTo 0
Next

If pythonProcessFound Or chromeProcessFound Then
    WScript.Echo "MAAS stopped successfully."
Else
    WScript.Echo "MAAS was not running."
End If

Set objWMI = Nothing
Set objShell = Nothing
```

---

### Step 4: Create Installer

**File:** `install.bat`

```batch
@echo off
REM MAAS Installer Script
REM Author: MAAS Development Team
REM Version: 1.0

echo =========================================
echo MAAS Installation
echo =========================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Please run this installer as Administrator.
    echo Right-click install.bat and select "Run as administrator"
    pause
    exit /b 1
)

REM Set installation directory
set INSTALL_DIR=C:\MAAS
echo Installing to: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
)

REM Copy files
echo Copying files...
xcopy /E /I /Y python "%INSTALL_DIR%\python"
xcopy /E /I /Y app "%INSTALL_DIR%\app"
xcopy /E /I /Y frontend "%INSTALL_DIR%\frontend"
xcopy /E /I /Y data "%INSTALL_DIR%\data"
xcopy /E /I /Y logs "%INSTALL_DIR%\logs"

copy /Y config.yaml "%INSTALL_DIR%\"
copy /Y run.py "%INSTALL_DIR%\"
copy /Y start_maas.vbs "%INSTALL_DIR%\"
copy /Y stop_maas.vbs "%INSTALL_DIR%\"
copy /Y README.txt "%INSTALL_DIR%\"

echo Files copied successfully.
echo.

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MAAS.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_maas.vbs'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.IconLocation = '%INSTALL_DIR%\app\static\favicon.ico'; $Shortcut.Description = 'Mom''s Accounting Automation System'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo Desktop shortcut created successfully.
) else (
    echo Warning: Failed to create desktop shortcut.
)
echo.

REM Optional: Add to startup folder
set /p ADD_STARTUP="Add MAAS to Windows startup? (Y/N): "
if /i "%ADD_STARTUP%"=="Y" (
    powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MAAS.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\start_maas.vbs'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Save()"
    echo MAAS will start automatically on Windows startup.
)
echo.

echo =========================================
echo Installation Complete!
echo =========================================
echo.
echo MAAS has been installed to: %INSTALL_DIR%
echo Desktop shortcut: %USERPROFILE%\Desktop\MAAS.lnk
echo.
echo To start MAAS:
echo   1. Double-click the MAAS icon on your desktop
echo   2. Wait a few seconds for the interface to open
echo.
echo To stop MAAS:
echo   - Run %INSTALL_DIR%\stop_maas.vbs
echo.
echo For help, see %INSTALL_DIR%\README.txt
echo.
pause
```

---

### Step 5: Create User Instructions

**File:** `README.txt`

```
================================================================================
MAAS - Mom's Accounting Automation System
================================================================================

Version: 1.0
Last Updated: December 5, 2025

================================================================================
GETTING STARTED
================================================================================

1. STARTING MAAS:
   - Double-click the "MAAS" icon on your desktop
   - Wait a few seconds for the interface to open
   - The application will open in a browser window

2. STOPPING MAAS:
   - Close the browser window
   - Or: Double-click C:\MAAS\stop_maas.vbs

3. PROCESSING INVOICES:
   - Click "Upload Invoice" button
   - Select PDF invoice file
   - Review extracted data
   - Click "Process" to automate ACSoft

================================================================================
TROUBLESHOOTING
================================================================================

Problem: "Backend failed to start"
Solution:
  1. Check if another program is using port 8765
  2. Restart your computer
  3. Check logs: C:\MAAS\logs\maas.log

Problem: "Chrome not found"
Solution:
  - Install Google Chrome from https://www.google.com/chrome/
  - Or: The system will use your default browser (may look different)

Problem: Desktop shortcut not working
Solution:
  1. Navigate to C:\MAAS\
  2. Double-click start_maas.vbs

Problem: "Error starting backend"
Solution:
  1. Check if Python is properly installed: C:\MAAS\python\python.exe
  2. Reinstall MAAS
  3. Contact support with logs from C:\MAAS\logs\

================================================================================
FILES AND FOLDERS
================================================================================

C:\MAAS\
  ├── python\           - Python runtime (do not delete!)
  ├── app\              - Application code
  ├── frontend\         - User interface files
  ├── data\             - Your invoice data (invoices, database)
  ├── logs\             - Application logs (for troubleshooting)
  ├── start_maas.vbs    - Launcher script (run this to start MAAS)
  ├── stop_maas.vbs     - Shutdown script (run this to stop MAAS)
  └── README.txt        - This file

================================================================================
UNINSTALLING MAAS
================================================================================

To remove MAAS:
  1. Run C:\MAAS\stop_maas.vbs to stop the application
  2. Delete C:\MAAS\ folder
  3. Delete desktop shortcut
  4. Delete startup shortcut (if added):
     %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MAAS.lnk

IMPORTANT: Backup data\ folder before uninstalling if you want to keep invoices!

================================================================================
SUPPORT
================================================================================

For help or issues:
  - Check troubleshooting section above
  - Review logs: C:\MAAS\logs\maas.log
  - Contact: [Your support email/contact]

================================================================================
```

---

## Installation Procedures

### For Developers (Building the Package)

**Prerequisites:**
- Windows 10/11
- Python 3.9.7+ installed (for development)
- Google Chrome installed

**Steps:**

1. **Download Python Embeddable Package:**
   ```bash
   # Download from https://www.python.org/downloads/windows/
   # Get "Windows embeddable package (64-bit)" for Python 3.9.x
   # Extract to project_root/python/
   ```

2. **Configure Embedded Python:**
   ```bash
   # Edit python39._pth to enable imports
   echo python39.zip >> python/python39._pth
   echo . >> python/python39._pth
   echo Lib >> python/python39._pth
   echo Lib/site-packages >> python/python39._pth
   ```

3. **Install pip in Embedded Python:**
   ```bash
   # Download get-pip.py
   curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
   
   # Install pip in embedded Python
   python/python.exe get-pip.py
   ```

4. **Install Dependencies:**
   ```bash
   python/python.exe -m pip install -r requirements.txt
   ```

5. **Test Embedded Python:**
   ```bash
   # Test imports work
   python/python.exe -c "import fastapi; print('OK')"
   ```

6. **Create Distribution Package:**
   ```bash
   # Create package directory
   mkdir MAAS_Package
   
   # Copy files
   xcopy /E /I python MAAS_Package\python
   xcopy /E /I app MAAS_Package\app
   xcopy /E /I frontend MAAS_Package\frontend
   xcopy /E /I data MAAS_Package\data
   xcopy /E /I logs MAAS_Package\logs
   
   copy config.yaml MAAS_Package\
   copy run.py MAAS_Package\
   copy start_maas.vbs MAAS_Package\
   copy stop_maas.vbs MAAS_Package\
   copy install.bat MAAS_Package\
   copy README.txt MAAS_Package\
   ```

7. **Create Installer Archive:**
   ```bash
   # Create ZIP file
   powershell Compress-Archive -Path MAAS_Package\* -DestinationPath MAAS_v1.0.zip
   ```

### For End Users (Installing MAAS)

**Prerequisites:**
- Windows 10/11
- Google Chrome installed (recommended)

**Steps:**

1. **Extract ZIP File:**
   - Download `MAAS_v1.0.zip`
   - Extract to temporary location (e.g., Downloads)

2. **Run Installer:**
   - Right-click `install.bat`
   - Select "Run as administrator"
   - Follow prompts

3. **Test Installation:**
   - Double-click "MAAS" desktop icon
   - Wait for interface to open
   - Verify application loads

4. **(Optional) Configure Auto-Start:**
   - Installer will prompt to add to startup
   - Select "Y" if you want MAAS to start on Windows boot

---

## Testing Procedures

### Pre-Deployment Testing

**Test Environment:**
- Clean Windows 10/11 virtual machine
- No Python installed (verify embedded Python works)
- Google Chrome installed

**Test Checklist:**

#### 1. Installation Testing
- [ ] Extract package to temp directory
- [ ] Run installer as administrator
- [ ] Verify files copied to C:\MAAS\
- [ ] Verify desktop shortcut created
- [ ] Verify shortcut icon correct
- [ ] Test startup shortcut (if added)

#### 2. Launch Testing
- [ ] Double-click desktop shortcut
- [ ] Verify no console window appears
- [ ] Verify browser opens automatically (within 30 seconds)
- [ ] Verify interface loads correctly
- [ ] Verify no error messages

#### 3. Backend Testing
- [ ] Open browser to http://localhost:8765/health
- [ ] Verify health check returns {"status": "healthy"}
- [ ] Check C:\MAAS\logs\maas.log for errors
- [ ] Verify log file created and populated

#### 4. Shutdown Testing
- [ ] Close browser window
- [ ] Verify backend still running (check Task Manager)
- [ ] Run stop_maas.vbs
- [ ] Verify all processes terminated
- [ ] Verify clean shutdown logged

#### 5. Restart Testing
- [ ] Launch MAAS again
- [ ] Verify "already running" detection works
- [ ] Verify opens existing instance
- [ ] Stop and start multiple times
- [ ] Verify no orphan processes

#### 6. Error Scenario Testing
- [ ] Delete python\python.exe, test error message
- [ ] Block port 8765, test error handling
- [ ] Kill backend manually, test recovery
- [ ] Remove Chrome, test fallback browser
- [ ] Simulate network failure, test behavior

#### 7. User Acceptance Testing
- [ ] Test with non-technical user (mom)
- [ ] Observe workflow without instructions
- [ ] Note any confusion points
- [ ] Test with 5-10 real invoices
- [ ] Verify workflow acceptable

---

## Troubleshooting

### Common Issues

#### Issue: "Backend failed to start after 30 seconds"

**Symptoms:**
- VBScript shows error message
- Browser never opens
- C:\MAAS\logs\maas.log shows errors

**Causes:**
1. Port 8765 already in use
2. Python not found
3. Dependency import errors
4. Firewall blocking localhost

**Solutions:**
1. **Check port:**
   ```bash
   netstat -ano | findstr :8765
   ```
   If port in use, kill process or change port in config.yaml

2. **Verify Python:**
   ```bash
   C:\MAAS\python\python.exe --version
   ```
   Should print: `Python 3.9.x`

3. **Check dependencies:**
   ```bash
   C:\MAAS\python\python.exe -c "import fastapi; import uvicorn"
   ```
   Should not error

4. **Check firewall:**
   - Open Windows Defender Firewall
   - Check if Python.exe blocked
   - Add exception if needed

---

#### Issue: "Chrome not found"

**Symptoms:**
- VBScript shows warning
- Default browser opens instead
- URL bar visible (not app mode)

**Solutions:**
1. Install Google Chrome
2. Or: Update `start_maas.vbs` with correct Chrome path:
   ```vbscript
   chromeExe = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
   ```
3. Or: Accept default browser (functionality same, UX different)

---

#### Issue: Desktop shortcut doesn't work

**Symptoms:**
- Double-click shortcut does nothing
- Or: Shows VBScript error

**Solutions:**
1. **Verify shortcut target:**
   - Right-click shortcut → Properties
   - Target should be: `C:\MAAS\start_maas.vbs`
   - Start in: `C:\MAAS`

2. **Recreate shortcut manually:**
   - Right-click desktop → New → Shortcut
   - Location: `C:\MAAS\start_maas.vbs`
   - Name: MAAS

3. **Run directly:**
   - Navigate to C:\MAAS
   - Double-click start_maas.vbs

---

#### Issue: "MAAS is already running" but browser not open

**Symptoms:**
- VBScript says already running
- Browser window not visible
- Backend responding to health checks

**Solutions:**
1. **Open manually:**
   - Open Chrome
   - Navigate to http://localhost:8765

2. **Restart MAAS:**
   ```bash
   C:\MAAS\stop_maas.vbs
   # Wait 5 seconds
   C:\MAAS\start_maas.vbs
   ```

---

#### Issue: Backend crashes on startup

**Symptoms:**
- Logs show Python errors
- ImportError or ModuleNotFoundError
- Backend never reaches "ready" state

**Solutions:**
1. **Check logs:**
   ```bash
   notepad C:\MAAS\logs\maas.log
   ```
   Look for error details

2. **Reinstall dependencies:**
   ```bash
   C:\MAAS\python\python.exe -m pip install --force-reinstall -r requirements.txt
   ```

3. **Verify file structure:**
   - Ensure app/ folder exists
   - Ensure app/main.py exists
   - Ensure config.yaml exists

4. **Test Python directly:**
   ```bash
   C:\MAAS\python\python.exe C:\MAAS\run.py
   ```
   Check error output

---

### Debugging Tools

#### 1. Check Backend Health
```bash
# PowerShell
Invoke-WebRequest -Uri http://localhost:8765/health

# Or browser
http://localhost:8765/health
```

#### 2. Check Running Processes
```bash
# Find Python processes
tasklist | findstr python

# Find Chrome processes
tasklist | findstr chrome
```

#### 3. Check Port Usage
```bash
netstat -ano | findstr :8765
```

#### 4. View Logs
```bash
# View log file
notepad C:\MAAS\logs\maas.log

# Tail log (PowerShell)
Get-Content C:\MAAS\logs\maas.log -Wait -Tail 50
```

#### 5. Test Embedded Python
```bash
# Test Python works
C:\MAAS\python\python.exe --version

# Test imports
C:\MAAS\python\python.exe -c "import fastapi; import uvicorn; import google.generativeai; print('OK')"
```

---

## Maintenance

### Regular Maintenance Tasks

#### Daily (Automated)
- Log rotation (automatically handled by logging module)
- Health check monitoring (built into launcher)

#### Weekly (Manual)
- Review logs for errors: `C:\MAAS\logs\maas.log`
- Check disk space: `C:\MAAS\data\`
- Backup database: Copy `C:\MAAS\data\maas.db`

#### Monthly (Manual)
- Update dependencies (if security patches released)
- Review Gemini API costs
- Clean up old screenshots: `C:\MAAS\data\screenshots\`
- Archive old invoices: `C:\MAAS\data\invoices\`

### Updating MAAS

**Process:**
1. Stop MAAS: `C:\MAAS\stop_maas.vbs`
2. Backup data: Copy `C:\MAAS\data\` to safe location
3. Backup database: Copy `C:\MAAS\data\maas.db`
4. Extract new version to temporary location
5. Run installer (will overwrite files in C:\MAAS\)
6. Restore data directory (if needed)
7. Test launch: Double-click desktop icon
8. Verify application works correctly

### Backing Up Data

**Critical Files:**
- `C:\MAAS\data\maas.db` - Database (invoices, vendors, audit trail)
- `C:\MAAS\data\invoices\` - PDF files
- `C:\MAAS\data\screenshots\` - Automation screenshots (optional)
- `C:\MAAS\config.yaml` - Configuration (if customized)

**Backup Script:**
```batch
@echo off
REM Backup MAAS data
set BACKUP_DIR=%USERPROFILE%\Documents\MAAS_Backups
set BACKUP_DATE=%DATE:~-4%-%DATE:~4,2%-%DATE:~7,2%

mkdir "%BACKUP_DIR%\%BACKUP_DATE%"
xcopy /E /I /Y "C:\MAAS\data" "%BACKUP_DIR%\%BACKUP_DATE%\data"
copy /Y "C:\MAAS\config.yaml" "%BACKUP_DIR%\%BACKUP_DATE%\"

echo Backup complete: %BACKUP_DIR%\%BACKUP_DATE%
pause
```

---

## Phase 2-3: Electron Deployment

### Architecture Overview

```
MAAS.exe (Electron) → Main Process → Python Backend (embedded) → REST API
                            ↓
                      Renderer Process → Vue.js Frontend
```

### Advantages Over PWA

1. **Native Application:**
   - No browser chrome (URL bar, tabs, etc.)
   - Professional desktop app experience
   - Custom window controls

2. **Better Integration:**
   - System tray icon with status indicator
   - Native notifications
   - Auto-update support
   - File associations (optional)

3. **Simplified Deployment:**
   - Single installer (.exe)
   - All dependencies embedded
   - Cleaner uninstall process

4. **Enhanced Security:**
   - No browser security restrictions
   - Direct IPC communication (faster)
   - Better process isolation

### Implementation Guide

**(Detailed Electron implementation guide to be added in Phase 2)**

**Key Components:**
1. Electron main process (`main.js`)
2. Electron renderer process (Vue.js)
3. Python backend (embedded)
4. NSIS installer configuration
5. Auto-update server integration

**See:** `spec/Tasks.md` Task-9 for detailed implementation checklist.

---

## Appendix

### A. File Permissions

**Required Permissions:**
- `C:\MAAS\` - Full control (read, write, execute)
- `C:\MAAS\data\` - Full control (read, write)
- `C:\MAAS\logs\` - Full control (write)

**Firewall Rules:**
- Allow Python.exe to bind to localhost:8765
- No internet access required (all local)

### B. System Requirements

**Minimum:**
- Windows 10 (64-bit)
- 4 GB RAM
- 500 MB disk space
- 1280x800 screen resolution
- Google Chrome (recommended)

**Recommended:**
- Windows 11 (64-bit)
- 8 GB RAM
- 1 GB disk space (for invoice storage)
- 1920x1080 screen resolution
- Google Chrome latest version

### C. Port Usage

**Port 8765:**
- Used by FastAPI backend
- Bound to localhost only (127.0.0.1)
- Not exposed to network
- Required for frontend communication

**Changing Port:**
1. Edit `config.yaml`:
   ```yaml
   server:
     port: 8765  # Change this
   ```
2. Edit `start_maas.vbs`:
   ```vbscript
   ' Update health check and browser URL
   objHTTP.Open "GET", "http://localhost:8765/health", False
   browserCmd = """" & chromeExe & """ --app=http://localhost:8765"
   ```

### D. Chrome App Mode

**What is App Mode?**
- Fullscreen browser window without chrome
- No URL bar, tabs, or bookmarks bar
- Looks like native desktop application

**Command:**
```bash
chrome.exe --app=http://localhost:8765
```

**Additional Flags:**
- `--window-size=1280,800` - Set window size
- `--window-position=100,50` - Set window position
- `--disable-restore-session-state` - Don't restore tabs
- `--disable-background-networking` - Disable background sync

### E. Security Considerations

**Local-Only Deployment:**
- Backend binds to 127.0.0.1 (localhost only)
- No external network access required
- All data stays on local computer
- No data sent to cloud (except Gemini API)

**Gemini API:**
- PDF sent to Google for OCR
- Ensure PDFs don't contain highly sensitive data
- Or: Implement local OCR alternative (Tesseract)

**Database Encryption:**
- Phase 1: SQLite unencrypted (local security)
- Phase 3: Consider SQLCipher for encryption

**API Keys:**
- Stored in config.yaml (local file)
- Never committed to git
- Read-only by MAAS user only

### F. Support Contacts

**For Technical Issues:**
- Email: [your-email@example.com]
- Phone: [your-phone]

**For Feature Requests:**
- GitHub Issues: [repo-url]

**For Security Issues:**
- Security email: [security@example.com]

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-12-05 | Development Team | Initial deployment guide |

---

**End of Document**
