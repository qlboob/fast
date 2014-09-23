#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.


if 0 !=2
{
	MsgBox, 参数必须是两个
	return
}

target = %1%

newLnk = %2%

if(!FileExist(target)){
	MsgBox, 目标不存在
	return
}
SplitPath, newLnk,fileName, path,ext
if(ext!="lnk"){
	newLnk .= ".lnk"
}

FileCreateShortcut, %target%, %newLnk%


if ErrorLevel {
	MsgBox, 创建失败
}
