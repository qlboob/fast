/*
windows hosts文件切换工具

*/
package main

import (
	"os"
	"io/ioutil"
	"fmt"
)
func main(){
	files := make([]string, 0)
	if 2==len(os.Args){
		files = append(files,"conf/"+os.Args[1]+".txt")
	}
	files = append(files,"conf/common.txt")

	result := ""
	for _,file := range files {
		result += read3(file)
		result += "\r\n"
		//fmt.Println("文件"+file)
	}
	resultFile,err := os.Create("c:\\windows\\system32\\drivers\\etc\\hosts")
	if nil==err{
		defer resultFile.Close()
		resultFile.WriteString(result)
	} else{
		fmt.Println("打开文件失败")
	}

	//fmt.Println(result)
}


func read3(path string)string{  
    fi,err := os.Open(path)  
    if err != nil{
		fmt.Println("文件"+path+"不存在")
		return ""
	}  
    defer fi.Close()  
    fd,err := ioutil.ReadAll(fi)  
    // fmt.Println(string(fd))  
    return string(fd)  
}  
