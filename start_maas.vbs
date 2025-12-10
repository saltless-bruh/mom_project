Set WshShell = CreateObject("WScript.Shell")
strCurDir = WshShell.CurrentDirectory

' 1. Start Backend (Hidden)
' Use pythonw.exe if available (embedded), otherwise python.exe
' Assuming python/pythonw.exe exists for embedded, or system python
strPython = "python\pythonw.exe"
If Not CreateObject("Scripting.FileSystemObject").FileExists(strPython) Then
    strPython = "python" ' Fallback to system python
End If

' Run run.py in background (0 = Hide Window)
WshShell.Run Chr(34) & strPython & Chr(34) & " run.py", 0, False

' 2. Wait for backend to start (simple delay)
WScript.Sleep 3000

' 3. Open Browser in App Mode
' Chrome
strURL = "http://localhost:8765"
strChrome = "C:\Program Files\Google\Chrome\Application\chrome.exe"
strEdge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

If CreateObject("Scripting.FileSystemObject").FileExists(strChrome) Then
    WshShell.Run Chr(34) & strChrome & Chr(34) & " --app=" & strURL, 1, False
ElseIf CreateObject("Scripting.FileSystemObject").FileExists(strEdge) Then
    WshShell.Run Chr(34) & strEdge & Chr(34) & " --app=" & strURL, 1, False
Else
    WshShell.Run strURL
End If
