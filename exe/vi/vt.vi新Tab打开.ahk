#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
IfWinExist ahk_class Vim
{
	WinActivate
	SendInput {ESC}:tabedit %1%{Enter}
}
else{
	run, d:\gvim\vim74\gvim.exe
	winwaitactive ahk_class Vim
	SendInput {ESC}:e %1%{Enter}
}
