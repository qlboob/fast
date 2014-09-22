from boot_win import Window
import sys

if len(sys.argv)>1 and 'reindex'==sys.argv[1]:
	Data().reindex()
else:
	Window(False).run()
if len(sys.argv)>1:
	outoput = open('e:/data.txt', 'w')
	outoput.write(sys.argv[1])
