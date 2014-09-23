#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.

SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;删除文件（夹）

dest := ""


loop, %0%
{
	;选检查文件（夹）是否存在
	dest := %A_Index%
	if(!FileExist(dest)){
		MsgBox, %dest%不存在
		return
	}	
}

loop, %0%
{
	dest := %A_Index%
	FileRecycle, %dest%
}