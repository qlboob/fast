loop, 100{
	IfWinExist, ahk_class Chrome_WidgetWin_1
	{
		winclose
	}else{
		break
	}

}
