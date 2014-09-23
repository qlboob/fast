#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

filePath = %1%

FileCreateDir, %filePath%
if ErrorLevel{
	MsgBox, 0, 创建文件夹失败,创建文件夹“%filePath%”失败, 2
	return
}

MsgBox, 4, 打开目录,是否打开目录%filePath% ,4
IfMsgBox YES
	run, %filePath%
