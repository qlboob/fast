#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Recommended for catching common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

SetWorkingDir, F:\build_tool_test
RunWait, %comspec% /c TortoiseProc.exe /command:update /path:"f:\build_tool_test\" /closeonend:1