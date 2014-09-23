#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Recommended for catching common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

SetWorkingDir, F:\qian
RunWait, %comspec% /c TortoiseProc.exe /command:commit /path:"f:\qian\" /logmsg:"build" /closeonend:1
