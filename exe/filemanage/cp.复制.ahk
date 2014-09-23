#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;TODO 复制前先检查目标位置是否有同名文件或文件夹

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


;多个文件或文件夹复制到一个目录
if 0 > 2
{
	;不是文件夹
	if(!isDir(dest)){
		MsgBox, %dest%不是目录
	}
	loopCnt := cnt-1
	loop %loopCnt%{
		src := %A_Index%
		SplitPath,src,fileName
		destFileName =%dest%\%fileName%
		if(isFile(src)){
			if(isFile(destFileName)){
				MsgBox, 4, 是否覆盖, 文件%destFileName%已经存在是否覆盖
				IfMsgBox YES
					FileCopy, %src%, %dest%, 1
			}else if(isDir(destFileName)){
				MsgBox, 已经存在文件夹【%destFileName%】，不能复制文件
			}else{
				FileCopy, %src%, %dest%
			}
		}else{
			if(isFile(destFileName)){
				MsgBox, 已经存在文件【%destFileName%】，不能复制文件夹
			}else if(isDir(destFileName)){
				MsgBox, 4, 是否覆盖, 文件夹【%destFileName%】已经存在是否覆盖
				IfMsgBox YES
					FileCopy, %src%, %dest%, 1
			}else{
				FileCopyDir, %src%, %dest%\%fileName%
			}
		}
		if ErrorLevel{
			MsgBox, 复制%src%失败
			return
		}
	}
}
else{
	;复制一个文件或文件夹
	src = %1%
	SplitPath, src, srcFileName,srcFilePath,srcExt
	SplitPath,dest,destFileName,destFilePath,destExt
	if(isDir(src)){
		if(isDir(dest)){
			;目标地址已经是一个目录，复制到其子目录
			newDir = %dest%\%srcFileName%
			if(isFile(newDir)){
				MsgBox, 已经存在文件【%newDir%】，不能复制文件夹
			}else if(isDir(newDir)){
				MsgBox, 4, 是否覆盖，文件夹【%newDir%】已经存在是否覆盖
				IfMsgBox YES
					FileCopyDir,%src%,%dest%\%srcFileName%, 1
			}else{
				FileCopyDir,%src%,%dest%\%srcFileName%
			}
		}else if(isDir(destFilePath)){
			;复制并改名
			if(isFile(dest)){
				MsgBox, 已经存在文件【%dest%】，不能复制文件夹
			}else{
				FileCopyDir,%src%,%dest%
			}
		}else if(canUseFileName(dest)){
			;复制到同级目录，并改名
			newDir =%srcFilePath%\%dest%
			if(isFile(newDir)){
				MsgBox, 已经存在文件【%newDir%】，不能复制文件夹
			}else if(isDir(newDir)){
				MsgBox, 4, 是否覆盖, 文件夹【%newDir%】已经存在是否覆盖
				IfMsgBox YES
					FileCopyDir, %src%, %srcFilePath%\%dest%, 1
			}else{
				FileCopyDir, %src%, %srcFilePath%\%dest%
			}
		}else{
			MsgBox, %destFilePath%不是目录
			return
			
		}
	}
	else{
		if(isDir(dest)){
			;直接复制到目录
			newFile = %dest%\%srcFileName%
			if(isFile(newFile)){
				MsgBox, 4, 是否覆盖，文件【%newFile%】已经存在是否覆盖
				IfMsgBox YES
					FileCopy, %src%, %dest%, 1
			}else if(isDir(newFile)){
				MsgBox, 已经存在文件夹 【%newFile%】不能复制
			}else{
				FileCopy, %src%, %dest%
			}
		}else if(isDir(destFilePath)){
				newFile = %dest%
				if(srcExt && srcExt!=destExt){
					;自动补齐扩展名
					newFile = %dest%.%srcExt%
				}
				if(isFile(newFile)){
					MsgBox, 4, 是否覆盖，文件【%newFile%】已经存在是否覆盖
					IfMsgBox YES
						FileCopy, %src%, %newFile%, 1
				}else if(isDir(newFile)){
					MsgBox, 已经存在文件夹【%newFile%】，不能复制
				}else{
					FileCopy, %src%, %newFile%
				}
		}else{
			if(canUseFileName(dest)){
				newFile = %srcFilePath%\%dest%
				if(srcExt && srcExt!=destExt){
					;自动补齐扩展名
					newFile = %srcFilePath%\%dest%.%srcExt%
				}
				if(isFile(newFile)){
					MsgBox, 4, 是否覆盖, 文件【%newFile%】已经存在是否覆盖
					IfMsgBox YES
						FileCopy, %src%, %newFile%, 1
				}else if(isDir(newFile)){
					MsgBox, 已经存在文件夹【%newFile%】，不能复制
				}else{
					FileCopy, %src%, %newFile%
				}
			}else{
				MsgBox,%destFilePath%不是目录
				return
			}
		}
	}
	if ErrorLevel{
		MsgBox, 复制%src%失败
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
