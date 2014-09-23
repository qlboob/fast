#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.

SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;移动文件（夹）

cnt = %0%
dest := ""

if 0 < 2
{
	MsgBox, 参数少于2个
	return
}

loop, %0%
{
	dest := %A_Index%
	if(cnt>A_Index || cnt>2){
		;检查源地址是否存在
		if(!FileExist(dest)){
			MsgBox, %dest%不存在
			return
		}
	}
	
}


;多个文件或文件夹移动到一个目录
if 0 > 2
{
	;不是文件夹
	if(!isDir(dest)){
		MsgBox, %dest%不是目录
	}
	loopCnt := cnt-1
	loop %loopCnt%{
		src := %A_Index%
		if(isFile(src)){
			FileMove, %src%, %dest%
		}else{
			SplitPath,src,fileName
			FileCopyDir, %src%, %dest%\%fileName%
		}
		if ErrorLevel{
			MsgBox, 移动%src%失败
			return
		}
	}
}
else{
	;移动一个文件或文件夹
	src = %1%
	SplitPath, src, srcFileName,srcFilePath,srcExt
	SplitPath,dest,destFileName,destFilePath,destExt
	if(isDir(src)){
		if(isDir(dest)){
			;目标地址已经是一个目录，移动到其子目录
			FileMoveDir, %src%, %dest%\%srcFileName%
		}else if(isDir(destFilePath)){
			;移动并改名
			FileMoveDir, %src%,%dest%
		}else if(canUseFileName(dest)){
			;复制到同级目录，并改名
			FileMoveDir, %src%, %srcFilePath%\%dest%
		}else{
			MsgBox, %destFilePath%不是目录
			return
		}
	}
	else{
		if(isDir(dest)){
			;直接移动到目录
			FileMove, %src%, %dest%
		}else if(isDir(destFilePath)){
				if(srcExt && srcExt!=destExt){
					;自动补齐扩展名
					FileMove, %src%, %dest%.%srcExt%
				}else{
					FileMove, %src%, %dest%
				}
		}else{
			if(canUseFileName(dest)){
				if(srcExt && srcExt!=destExt){
					;自动补齐扩展名
					FileMove, %src%, %srcFilePath%\%dest%.%srcExt%
				}else{
					FileMove,%src%,%srcFilePath%\%dest%
				}
			}else{
				MsgBox,%destFilePath%不是目录
				return
			}
		}
	}
	if ErrorLevel{
		MsgBox, 移动%src%失败
		return
	}
}

isDir(path){
	if(!FileExist(path)){
		return false
	}
	file := FileOpen(path,"r")
	if(IsObject(file)){
		return false
	}
	return true
	
}


isFile(path){
	if(!FileExist(path)){
		return false
	}
	file := FileOpen(path,"r")
	if(IsObject(file)){
		return true
	}
	return false
	
}

canUseFileName(name){
	chars := [":","/","\","*","?"]
	loop % chars.MaxIndex(){
		char := chars[A_Index]
		if(instr(name,char)){
			return false
		}
	}
	return true
}