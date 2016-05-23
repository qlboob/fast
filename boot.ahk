#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Recommended for catching common errors.
#SingleInstance Force
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
DetectHiddenWindows, On

^!L::
WinShow, ahk_class TkTopLevel
IfWinExist, ahk_class TkTopLevel
	WinActivate
else
	run boot_ahk.pyw
return
