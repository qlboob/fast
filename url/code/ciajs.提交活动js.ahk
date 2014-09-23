#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Recommended for catching common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

RunWait, %comspec% /c TortoiseProc.exe /command:commit /path:"F:/dev_branches/build_tool/htdocs/res/hybrid/js/logic/www/weixin/fund/action" /logmsg:"" /closeonend:1
