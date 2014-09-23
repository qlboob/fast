#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Recommended for catching common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.


;新建文件
filePath = %1%
;filePath = f:\1.txt
stringreplace,filePath,filePath,/,\,All
;最后一个“\”的位置
StringGetPos,pos,filePath,\,R
;路径中的文件名
StringLeft,dir, filePath,pos+1
StringMid, fileName, filePath, pos+2

StringGetPos, pos, fileName, ., R
StringLeft,onlyName,fileName,pos
;扩展名
stringMid,ext, fileName,pos+1
;如果没有扩展名
if(-1==pos){
	onlyName := ext
	ext =
}

srcFile := "../../newfile/new.txt"
if(ext){
	if(FileExist(srcFile)){
		srcFile = ../../newfile/new%ext%
	}
}
filecopy, %srcFile% , %filePath%
if ErrorLevel{
	MsgBox, 0, 创建文件失败,创建文件失败, 2
	return
}
msgbox, 4, 是否打开%filePath%, 是否打开%filePath%, 4
ifmsgbox YES
	Run, %filePath%
