Set WshShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

strPidFile = "maas.pid"

If FSO.FileExists(strPidFile) Then
    Set objFile = FSO.OpenTextFile(strPidFile, 1)
    strPid = objFile.ReadAll
    objFile.Close
    
    ' Force kill the process with that PID
    WshShell.Run "taskkill /PID " & strPid & " /F", 0, True
    
    ' Delete pid file
    FSO.DeleteFile strPidFile
    MsgBox "MAAS has been stopped.", 64, "Mom's Accounting System"
Else
    MsgBox "MAAS is not running (PID file not found).", 48, "Mom's Accounting System"
End If
