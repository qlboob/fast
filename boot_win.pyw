# -*- coding: utf-8 -*-  

from tkinter import *

import os,threading,sys,re
import pythoncom
from win32com.shell import shell  
from win32com.shell import shellcon
import win32api
import sqlite3

import shutil

from ctypes import *
from ctypes.wintypes import *
import win32gui
import time

class Data:
	'''Data'''
	def __init__(self):
		#用于得到快捷方式实际的路径
		self.shortcut = pythoncom.CoCreateInstance(  
			shell.CLSID_ShellLink, None,  
			pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)  
		#得到当前文件的路径，数据库文件和exe文件夹 url文件夹都是相对于当前文件的
		self.path = sys.path[0]
		if os.path.isfile(self.path):
			self.path = os.path.dirname(self.path)
		self.path += '\\'

		#默认程序
		self.exe = False
		#everything 是否运行
		self.everythingRun = True

		#使用的正式库文件
		self.dbFile = self.path + 'db/boot.db3'
		#生成过程中的库文件
		self.tmpDbFile = self.path + 'db/boot_tmp.db3'
		#生成结束的库文件
		self.okDbFile = self.path + 'db/boot_ok.db3'
		self.initDb(self.dbFile)


	#初始化数据库连接
	def initDb(self,dbFile,oldDbFile=''):
		if oldDbFile:
			shutil.copyfile(oldDbFile,dbFile)
		#elif os.path.isfile(self.okDbFile):

			
		self.con = sqlite3.connect(dbFile)
		self.con.create_function("fileName",1,self.fileName)
		self.con.isolation_level = None 
		self.cur = self.con.cursor()
		if os.path.getsize(dbFile) < 10:
			#create db
			for sql in ['CREATE TABLE filepath ( path varchar(100), sort INT default 0 )','CREATE TABLE exepath(ab varchar(10),path varchar(100), info varchar(10), sort INT default 0)','CREATE TABLE urlpath(ab varchar(10),path varchar(100), info varchar(10), sort INT default 0)','CREATE TABLE historyfile ( path varchar(100), sort INT DEFAULT 0, PRIMARY KEY (path COLLATE NOCASE) )']:
				self.cur.execute(sql)
			self.reindex()
			self.switchDb()
	
	#切换DB
	def switchDb(self):
		if os.path.isfile(self.okDbFile):
			self.closeDb()
			os.remove(self.dbFile)
			os.rename(self.okDbFile,self.dbFile)
			self.initDb(self.dbFile)

	#关闭db
	def closeDb(self):
		self.con.close()



	#在sqlite3中加的函数,获取路径中的名称名
	def fileName(self,filePath):
		arrPath = filePath.split('\\')
		return arrPath[-1]

	#关闭数据库连接
	def __del__(self):
		self.closeDb()

	#得到快捷方式的路径
	def getPathFromLink(self,lnkpath):
		shortcut = self.shortcut
		shortcut.QueryInterface( pythoncom.IID_IPersistFile ).Load(lnkpath)
		path = shortcut.GetPath(shell.SLGP_SHORTPATH)[0]  
		return self.expandPath(path)
	#展开路径，路径中带有~号的情况
	def expandPath(self,path):
		if not os.path.exists(path):
			return path
		if '~' in path:
			arrPath = path.split('\\')
			prefixDir = arrPath.pop(0)+'\\'
			while len(arrPath):
				iDir = arrPath.pop(0)
				if '~' in iDir:
					#使用dos命令 “dir /x”找到代~目录的原名称
					handler = os.popen('dir /x "'+prefixDir+'"')
					output = handler.read()
					handler.close()
					if output:
						items = output.split("\n")
						for line in items:
							if iDir not in line:
								continue
							cells=re.split(' +',line,4)
							if 5==len(cells) and iDir==cells[3]:
								iDir=cells[4]
								break
				prefixDir += iDir+'\\'
			return prefixDir.rstrip('\\')
		return path
							


	#得到url的快捷方式的实际地址
	def getLinkUrl(self,file):
		"""get file url"""
		fp = open(file)
		for line in fp:
			if line[0:4]=='URL=':
				fp.close()
				return line[4:].strip()

	#得到文件夹下所有的文件，可以指定扩展名和是否包括子目录
	def getFolderFiles(self,folder,ext='',recursion=True):
		"""get folder files"""
		#get all files
		ret = []
		#print(folder)
		if not os.path.isdir(folder):
			return ret
		folder = folder.replace('/','\\')
		if '\\' != folder[-1]:
			folder += '\\'
		if recursion:
			for root, dirs, files in os.walk(folder, True):
				for name in files:
					ret.append(os.path.join(root,name))
		else:
			files = os.listdir(folder)
			for f in files:
				filepath = os.path.join(folder,f)
				if os.path.isfile(filepath):
					ret.append(filepath)
		#filter file ext
		if ext:
			newExt = ext.split(',')
			for i in range(len(ret)-1,-1,-1):
				flagDelete = True
				for e in newExt:
					if ret[i][-len(e):] == e:
						flagDelete=False
						break
				if flagDelete:
					del ret[i]
		#print(ret)

		return ret

	#得到快捷方式的真实地址
	def getFileTruePath(self,filelist):
		'''get file true path,if the file is lnk'''
		ret = []
		for f in filelist:
			ext = f[-4]
			if '.lnk' == ext:
				f = self.getPathFromLink(f)
			elif 'url' == ext:
				f = getLinkUrl(f)
			f = f.replace('/','\\')
			ret.append(f)
		return ret
	
	#得到打开程序的默认程序
	def getDefaultExe(self,executeFile):
		if not os.path.isfile(executeFile):
			return ''
		dotArr = executeFile.split('.')
		exeExt = dotArr[-1]
		if not self.exe:
			self.exe = {}
			files = self.getFolderFiles(self.path+'defaultexe','lnk,exe,ahk')
			if files:
				for file in files:
					fileName = os.path.basename(file)
					fileNameArr = fileName.split('.')
					ext = fileNameArr.pop()
					if 'lnk'==ext:
						try:
							targetFile = self.getPathFromLink(file)
							if not os.path.isfile(targetFile):
								continue
						except Exception as e:
							continue
						for noExtFileName in fileNameArr: 
							self.exe[noExtFileName] = targetFile
		return self.exe.get(exeExt)
		
	def getFavoriteDir(self,pattern):
		faviorDir = self.findUrl(pattern)
		if faviorDir and os.path.isdir(faviorDir) and ':\\' in faviorDir:
			if '~' in faviorDir:
				faviorDir = faviorDir.split('~')[0]
			return faviorDir
		return False


	#把exe目录的数据提出来
	def reindexExe(self):
		#reindex exe
		exeData = {}
		exeFiles = self.getFolderFiles(self.path+'exe','lnk,exe,bat,cmd,ahk')
		for p in exeFiles:
			pbase = os.path.basename(p)
			#文件名的
			#	第一段作为快速启动的缩写
			#	第二段任务提示内容
			#	最后一段作为扩展名
			pnames = pbase.split('.')
			key = pnames[0].lower()
			info = ''
			if len(pnames)>2:
				info = pnames[1]
			if pnames[-1] == 'lnk':
				#有可能快捷方式已经失效
				try:
					p = self.getPathFromLink(p)
					if not os.path.isfile(p):
						continue
				except Exception as e:
					#print(p)
					continue
			exeData[key] = {'path':p,'info':info}
		return exeData

	def reindexUrl(self):
		siteData	=	{}
		for f in self.getFolderFiles(self.path+'url'):
			pbase = os.path.basename(f)
			pnames = pbase.split('.')
			ext = pnames[-1]
			info = ''
			if len(pnames)>2:
				info = pnames[1]
			truePath = f
			if 'url'==ext:
				truePath = self.getLinkUrl(f)
			elif 'lnk'==ext:
				truePath = self.getPathFromLink(f)
				if not os.path.isfile(truePath) and not os.path.isdir(truePath):
					continue
			siteData[pnames[0].lower()] = {'path':truePath,'info':info}
		return siteData

	def reindexFiles(self):
		files = []
		configFile = self.path+'db/config.txt'
		if os.path.isfile(configFile):
			lines = open(configFile).readlines()
			for line in lines:
				line += "\t\t"
				(folder,ext) = line.split("\t",1)
				files += self.getFolderFiles(folder,ext.strip(),folder[-1]!='\\')
			ret = self.getFileTruePath(files)
			ret = set(ret)
			#print(ret)
			return list(ret)
	def reindexHistory(self):
		ret = []
		historyF = self.getTableData('historyfile')
		if not historyF:
			return ret
		for x in historyF:
			file = x[0]
			if not os.path.isfile(file) and not os.path.isdir(file):
				self.cur.execute('DELETE FROM historyfile WHERE path="{0}"'.format(file))

	def getTableData(self,table):
		self.cur.execute('SELECT * FROM {0}'.format(table));
		return self.cur.fetchall()

	def reindex(self):
		#重新创建数据库
		self.closeDb()
		self.initDb(self.tmpDbFile,self.dbFile)
		#rewrite exe data
		startTime = time.time()
		exeData = self.reindexExe()
		exeExist = self.getTableData('exepath');
		#self.cur.execute('delete from exepath')
		for v in exeExist:
			addPathInfo = exeData.get(v[0]);
			if addPathInfo and addPathInfo['path'] == v[1] and addPathInfo['info']==v[2]:
				del exeData[v[0]]
			else:
				self.cur.execute('DELETE FROM exepath WHERE ab="{0}"'.format(v[0]))
		for k,v in exeData.items():
			self.cur.execute('INSERT INTO exepath(ab,path,info) VALUES("%s","%s","%s")'%(k,v['path'],v['info']))
		exeEndTime = time.time()
		#print("exe time:")
		#print(exeEndTime-startTime)
		#rewite exe data end

		urlData = self.reindexUrl()
		urlExist = self.getTableData('urlpath')
		#self.cur.execute('delete from urlpath')
		for v in urlExist:
			addPathInfo = urlData.get(v[0])
			if addPathInfo and addPathInfo['path'] == v[1] and addPathInfo['info']==v[2]:
				del urlData[v[0]]
			else:
				# DELETE FROM urlpath WHERE ab="info" 不能删除数据
				self.cur.execute("DELETE FROM urlpath WHERE ab='{0}'".format(v[0]))
		for k,v in urlData.items():
			self.cur.execute('INSERT INTO urlpath(ab,path,info) VALUES("%s","%s","%s")'%(k,v['path'],v['info']))
		urlEndTime = time.time()
		#print('url time:')
		#print(urlEndTime - exeEndTime)

		fileData = self.reindexFiles()
		if fileData:
			#print("scan file time:")
			#print(time.time()-urlEndTime)
			fileExist= self.getTableData('filepath')
			#self.cur.execute('delete from filepath')
			for v in fileExist:
				if fileData.count(v[0]):
					fileData.remove(v[0])
				else:
					self.cur.execute('DELETE FROM filepath WHERE path="{0}"'.format(v[0]))
			for v in fileData:
				self.cur.execute('insert into filepath(path) values("%s")'%v)
			#print("file time:")
			#print(time.time()-urlEndTime)
		
		self.reindexHistory()
		self.reduceSort()

		#更新DB文件名
		self.closeDb()
		os.rename(self.tmpDbFile,self.okDbFile)

	#根据缩写找到应用程序提示列表
	def popExe(self,pattern):
		self.searchStr = pattern
		sql = 'SELECT ab,path,info FROM exepath WHERE ab like "%{0}%" ORDER BY sort DESC LIMIT 10'.format(pattern)
		self.cur.execute(sql)
		ret = self.cur.fetchall()
		#print(sql)
		#print(ret)
		if ret:
			ret = sorted(ret,key=self.sortAb)
		return ret

	def popUrl(self,pattern):
		self.searchStr = pattern
		sql = 'SELECT ab,path,info FROM urlpath WHERE ab LIKE "%{0}%"  ORDER BY sort DESC LIMIT 10'.format(pattern)
		self.cur.execute(sql)
		ret = self.cur.fetchall()
		#print(ret)
		if ret:
			ret = sorted(ret,key=self.sortAb)
		return ret
	#对缩写进行排序
	def sortAb(self,item):
		ab = item[0]
		abCnt = len(ab)
		someCnt = 0
		searchCnt = len(self.searchStr)
		while someCnt < searchCnt:
			if ab[someCnt] == self.searchStr[someCnt]:
				someCnt += 1
			else:
				break
		return abCnt/(abCnt+someCnt)


	def popFile(self,pattern,table='filepath'):
		arr = pattern.split(' ')
		where = []
		#最后一个当作文件名
		fileSearch = arr.pop()
		fileSearch = fileSearch.replace(".","%.")
		where.append('fileName(path) LIKE "%{0}%"'.format(fileSearch))
		if len(arr) > 0:
			#检查第一个是否有别名定义
			favior = arr[0]
			faviorDir = self.getFavoriteDir(favior)
			if faviorDir:
				where.append('path LIKE "{0}\\%"'.format(faviorDir.replace('/','\\')))
				arr.pop(0)

			"""
			faviorDir = self.findUrl(favior)
			if faviorDir and os.path.isdir(faviorDir): 
				# ~符号导致不能显示全路径,只拿部分路径搜索
				if '~' in faviorDir:
					faviorDir = faviorDir.split('~')[0]

				where.append('path LIKE "{0}\\%"'.format(faviorDir.replace('/','\\')))
				arr.pop(0)
			"""
			if arr:
				for d in arr:
					where.append('path LIKE "%\\{0}%\\%"'.format(d))
		sql ='SELECT path FROM %s WHERE '%table + ' AND '.join(where)
		sql += ' ORDER BY sort DESC LIMIT 10'
		sql = sql.replace('*','%')

		self.cur.execute(sql)
		ret = self.cur.fetchall()
		#print(ret)
		#print(sql)
		return ret

	"""
	提示文件路径
	"""
	def popPath(self,pattern):
		ret = []
		if not pattern:
			return ret
		pattern = pattern.replace("/",'\\')
		path = pattern
		file = ''
		if ':' == pattern[-1]:
			path = pattern + '\\'
		else:
			arrPath = pattern.split('\\')
			path = '\\'.join(arrPath[0:-1])+'\\'
			file = arrPath[-1]

		if os.path.isdir(path):
			files = os.listdir(path)
			for f in files:
				if f in ['$RECYCLE.BIN','$Recycle.Bin','System Volume Information','.git','.svn']:
					continue
				if file.lower() in f.lower():
					realPath = os.path.join(path,f)
					ele = realPath,
					ret.append(ele)
		return ret

	"""
	提示everything搜索文件
	"""
	def popEverything(self,pattern):
		ret = []
		if not pattern or not self.everythingRun:
			return ret
		cmdStr = self.path+'sys\es.exe -n 20 '
		searchStr = pattern
		arrPath = pattern.split(' ')
		if len(arrPath)>1:
			#包含空格的情况，允许路径搜索
			#cmdStr += '-p '
			faviorDir = self.getFavoriteDir(arrPath[0])
			if faviorDir:
				arrPath[0] = faviorDir
				#这样everything搜索必须前后都要加*号
				#if arrPath[-1]:
					#fileChar = [x for x in arrPath[-1]]
					#arrPath[-1]= '*'+'*'.join(fileChar) + '*'
			searchStr = ' '.join(arrPath)
		cmdStr += searchStr
		#print(cmdStr)
		startTime = time.time()
		handler = os.popen(cmdStr)
		output = handler.read()
		handler.close()
		useTime = time.time() - startTime
		#print(useTime)
		if output:
			items = output.split("\n")
			for item in items:
				if not item or (len(item)>3 and '.lnk' == item[-4:]):
					continue
				if 'Everything IPC window not found, IPC unavailable.' == item:
					self.everythingRun = False
					return ret
				ret.append((item,))
		#print(output)
		#print(ret)
		return ret
	"""
	提示历史使用过的文件
	"""
	def popHistoryFile(self,pattern):
		ret = []
		files = self.popFile(pattern,'historyfile')
		if files:
			for f in files:
				if os.path.isfile(f[0]) or os.path.isdir(f[0]):
					ret.append(f)
				else:
					sql = 'DELETE FROM historyfile WHERE path="%s"'%(f[0])
					self.cur.execute(sql)
		return ret


	def findExe(self,ab):
		sql = 'SELECT path FROM exepath WHERE ab ="%s" LIMIT 1'%ab
		self.cur.execute(sql)
		ret = self.cur.fetchone()
		if ret:
			return ret[0]

	def findUrl(self,ab):
		#这里执行 SELECT path FROM urlpath WHERE ab="info" LIMIT 1 找不到结果，不知道为什么
		sql = "SELECT path FROM urlpath WHERE ab='%s' LIMIT 1"%ab
		self.cur.execute(sql)
		ret = self.cur.fetchone()
		if ret:
			return ret[0]

	def findFile(self,arg):
		if os.path.isfile(arg) or os.path.isdir(arg) or arg.startswith('http://') or arg.startswith('https://'):
			return arg
		sql = 'SELECT path FROM filepath WHERE path="%{0}%" LIMIT 1'.format(arg)
		self.cur.execute(sql)
		ret = self.cur.fetchone()
		if ret:
			return ret[0]
	
	def addSort(self,table,key,col="ab"):
		sql = "UPDATE %s SET sort = sort + 1 WHERE %s='%s'" %(table,col,key)
		self.cur.execute(sql)
	
	#增加历史操作记录文件
	def addHistory(self,file):
		file = file.strip().replace('/','\\')
		if '\\' in file and os.path.exists(file):
			file = self.expandPath(file).lower()
			sql = 'SELECT path FROM historyfile WHERE path="%s"'%(file)
			self.cur.execute(sql)
			if self.cur.fetchone():
				#已经在历史记录中了
				sql = 'UPDATE historyfile SET sort=sort+1 WHERE path="%s"'%file
				self.cur.execute(sql)
			else:
				sql = 'SELECT * FROM filepath WHERE path="%s"'%file
				self.cur.execute(sql)
				#是否在文件列表中
				if not self.cur.fetchone():
					sql = 'INSERT INTO historyfile(path) VALUES("%s")'%file
					self.cur.execute(sql)

	
	#减少排序值，每次重建数据时，对sort值大于2的减1
	def reduceSort(self):
		tables = ['exepath','urlpath','filepath','historyfile']
		for table in tables:
			self.cur.execute("UPDATE %s SET sort=sort-1 WHERE sort > 2"%(table))



class ReindexThread(threading.Thread):
	'''thread for reindex db'''
	def __init__(self,data):
		threading.Thread.__init__(self)
		self.data=data
	def run(self):
		self.data.reindex();
class Window:
	def __init__(self,close=True):
		#执行完成是否关闭窗口，不关闭则隐藏窗口
		self.close = close
		self.data = Data()
		self.lastCommandList=[]
		self.lastArgList=[]
		#参数列表
		self.argv = []
		self.executePath = ''
		#在提示列表中选择的文本，第一个为commmand框内容，第二个为arg框内容
		self.selectTxt = ['','']
		#上次文本框的输入内容
		self.lastInput = ['','']
		#提示的条目数
		self.maxItem = 10
		#ctrlkey 是否按下
		self.ctrlKey=False

		app = Tk()
		self.app = app
		app.title('快速启动程序——秦嘉奇')

		#输入框的宽高
		width = 320
		height = 22

		#可执行文件的输入框
		commandField = self.commandField = Entry(app)
		commandField.focus()
		commandField.place(height=height,width=width)

		#参数输入框
		argField = self.argField = Entry(app)
		argField.place(height=height,x=width,width=width)

		#备选选择列表
		listbox = self.listbox = Listbox(app)
		listbox.place(height=height*10,y=height,width=width*2)

		self.label = Label(app,text='欢迎使用自启动程序',anchor="w",justify='left')
		self.label.place(height=height,width=width*2,y=height*10)
		
		app.geometry('{0}x{1}'.format(width*2,height*11))

		self.addEvent()
	
	def addEvent(self):
		'''add event for every widget'''
		self.commandField.bind('<Control-j>',lambda e,x=1:self.moveItem(e,x))
		self.commandField.bind('<Control-k>',lambda e,x=-1:self.moveItem(e,x))
		self.commandField.bind('<Control-l>',lambda e:self.useInput(e))
		self.commandField.bind('<KeyPress>',self.keyPressEvent)
		self.commandField.bind('<KeyRelease>',self.commandKeyEvent)
		self.commandField.bind('<Tab>',lambda e:self.emptyPop())
		self.commandField.bind('<Control-w>',lambda e:self.delWord(e))
		#self.commandField.bind('<Control-Enter>',lambda e:self.ctrlExecute(e))

		self.argField.bind('<Control-j>',lambda e,x=1:self.moveItem(e,x,1))
		self.argField.bind('<Control-k>',lambda e,x=-1:self.moveItem(e,x,1))
		self.argField.bind('<Control-l>',lambda e:self.useInput(e,1))
		self.argField.bind('<Control-i>',lambda e:self.addArg(e,True))
		self.argField.bind('<Control-o>',lambda e:self.addArg(e,False))
		self.argField.bind('<KeyPress>',self.keyPressEvent)
		self.argField.bind('<KeyRelease>',self.argKeyEvent)
		#self.argField.bind('<Shift-KeyPress-Tab>',lambda e:self.emptyPop())
		self.argField.bind('<Tab>',self.argTabExecute)
		self.argField.bind('<Control-w>',lambda e:self.delWord(e))

		#listbox
		#阻止listbox得到焦点
		self.listbox.bind('<FocusIn>',lambda e:self.commandField.focus())

	#提示的item的信息
	def getPopInfo(self,cstr,d):
		for method in [self.data.popUrl,self.data.popFile,self.data.popPath,self.data.popHistoryFile,self.data.popEverything]:
			if len(d) < self.maxItem:
				d += method(cstr) or []
				#print(d)
			else:
				break
		return d

	def commandKeyEvent(self,e):
		self.keyPressEvent(e)
		cstr = self.commandField.get()
		print(e.keycode)
		if 13==e.keycode:
			if self.ctrlKey:
				self.useInput(e)
			self.execute()
		elif cstr == self.lastInput[0]:
			#与上次输入内容相同不做更新
			return
		else:
			self.inputStr=cstr
			d = self.data.popExe(cstr)
			d = self.getPopInfo(cstr,d)
			self.setPop(d,e.widget)
			#设置上一次输入
			self.lastInput[0] = cstr
			#清空上一次选择
			self.selectTxt[0] = ''
	
	def keyPressEvent(self,e,val=True):
		if '2'==e.type:
			#KeyPress
			val=True
		elif '3'==e.type:
			#KeyRelease
			val=False
		if 17==e.keycode:
			self.ctrlKey = val
			print(val)
			
	def argKeyEvent(self,e):
		self.keyPressEvent(e)
		astr = self.argField.get()
		if 13 == e.keycode:
			if self.ctrlKey:
				self.useInput(e)
			self.execute()
		elif astr == self.lastInput[1]:
			#与上次输入内容相同不做更新
			return
		else:
			self.inputStr=astr
			d = self.getPopInfo(astr,[])
			self.setPop(d,e.widget)
			self.lastInput[1] = astr
			self.selectTxt[1] = ''


	"""
	ctrl-j ctrl-k 移动选择提示
	"""
	def moveItem(self,e,dirt=1,filedIndex=0):
		#print(e.widget.get())
		widget = e.widget
		size = self.listbox.size()
		if not size:
			return
		select = self.listbox.curselection()
		index = {-1:0,1:-1}[dirt]
		if select:
			index = int(select[0])
		index += dirt
		index %= size
		self.listbox.select_clear(0,size-1)
		self.listbox.selection_set(index)
		
		#TODO 可能越界
		item = self.lastCommandList[index] if widget == self.commandField else self.lastArgList[index]
		self.selectTxt[filedIndex] = item[0]
		if os.path.isdir(item[0]):
			#如果是文件夹自动替换输入框内容
			self.lastAutoStr = item[0]
			widget.delete(0,END)
			widget.insert(END,item[0])
			self.lastInput[filedIndex] = item[0]

	"""
	ctrl-i 压入参数
	"""
	def addArg(self,e,emptyInput):
		#先看是否有选择
		widget = e.widget
		str = widget.get()
		select = self.listbox.curselection()
		if select:
			self.argv.append(self.lastArgList[int(select[0])][0])
		elif str:
			self.argv.append(str)
		else:
			emptyInput = True
			if len(self.argv):
				self.argv.pop()
		if emptyInput:
			widget.delete(0,END)

		#self.label.text(' '.join(self.argv))
		self.label.config({'text':' '.join(self.argv)})


	"""
	把备选框的路径输入到输入框中
	"""
	def useInput(self,e,filedIndex=0):
		widget = e.widget
		select = self.listbox.curselection()
		currentStr = widget.get()
		#currentList = self.lastArgList if filedIndex else self.lastCommandList
		currentList = self.lastArgList if widget==self.argField else self.lastCommandList
		replaceStr = ''
		index = 0
		if select:
			#在有选择的情况下，使用选择的
			fileT = currentList[int(select[0])]
			if len(fileT) > 1:
				index = 1 
			replaceStr = fileT[index]
		else:
			for v in currentList:
				if currentStr == v[0]:
					if len(v)>1:
						index = 1 
						replaceStr = v[index]
						break
			#没有选择使用完全匹配，如果只有一个直接使用
			if len(currentList)>0 and not replaceStr:
				v=currentList[0]
				if len(v)>1:
					replaceStr = v[1]
				else:
					replaceStr=v[0]
					
		if os.path.isdir(replaceStr):
			replaceStr += '\\'


		if replaceStr:
			widget.delete(0,END)
			widget.insert(END,replaceStr)
		return replaceStr


	#参数框输入tab直接使用候选执行
	def argTabExecute(self,e):
		replaceStr = self.useInput(e,1)
		if replaceStr:
			self.execute()
		#事件中通过return break可以阻止事件后续及冒泡
		return 'break'

	#使用修行执行
	def ctrlExecute(self,e):
		replaceStr = self.useInput(e)
		if replaceStr:
			self.execute()
		return 'break'

	#得到参数
	def getExecuteArg(self,arg):
		argv = self.argv[:]
		ret = []
		if arg:
			argv += [arg]
		if len(argv):
			str = argv[-1]
			for str in argv:
				self.data.addSort('urlpath',str)
				str = self.data.findUrl(str) or self.data.findFile(str) or str
				if os.path.isfile(str):
					self.data.addSort('filepath',str,'path')
					self.executePath = os.path.dirname(str)
				elif os.path.isdir(str):
					self.executePath = str
				if ' ' in str:
					str = '"'+str+'"'
				ret.append(str)
		return ' '.join(ret)
				



	def execute(self):
		'''execute program'''
		command = self.selectTxt[0] or self.commandField.get()
		arg = self.selectTxt[1] or self.argField.get()
		filepath = ''
		if not command:
			#多线程中不能使用Data.getPathFromLink()函数,必须在主线程中初始化
			#ReindexThread(self.data).start()
			#self.data.reindex()

			#不能通过sys.argv 得到传递的参数
			win32api.ShellExecute(0,'open',self.data.path+"/boot_reindex.pyw",'reindex','',1)
		else:
			exe = self.data.findExe(command)
			url = self.data.findUrl(command)
			if exe:
				"""
				urlAndStr = arg.split(' ',2)
				if len(urlAndStr) ==2:
					url = self.data.findUrl(urlAndStr[0])
					if url:
						filepath = url + urlAndStr[1].replace(' ','+')
				if not filepath and arg:
					filepath = self.data.findUrl(arg) or self.data.findFile(arg) or arg

				#增加点击次数
				self.data.addSort('exepath',command)
				self.data.addSort('urlpath',arg)
				self.data.addSort('filepath',arg,'path')
				"""
				self.data.addSort('exepath',command)
				filepath = self.getExecuteArg(arg)

			elif url:
				exe = url
				if arg:
					exe += arg.strip().replace(' ','+')
				#增加点击次数
				self.data.addSort('urlpath',command)
			else:
				exe = command
				filepath = self.getExecuteArg(arg)
				#如果只输入文件名，使用默认程序打开
				defaultExe = self.data.getDefaultExe(exe)
				if defaultExe and not filepath:
					filepath = exe
					exe = defaultExe
					

				#增加点击次数
				self.data.addSort('filepath',command,'path')

			try:
				
				"""
				ShellExecute(hwnd, op , file , params , dir , bShow )
				hwnd：父窗口的句柄，如果没有父窗口，则为0
				op：要进行的操作，为“open”、“print”或者为空
				file：要运行的程序，或者打开的脚本
				params：要向程序传递的参数，如果打开的为文件，则为空
				dir：程序初始化的目录
				bShow：是否显示窗口
				在使用mklink创建的软件链接，直接打开文件会失败
				"""
				exeDir = '' #运行目录
				filepath = filepath.strip()
				if self.executePath:
					exeDir = self.executePath
					self.executePath = ''
				elif os.path.exists(filepath):
					exeDir = os.path.dirname(filepath)
					if ' ' in filepath:
						filepath = '"'+filepath+'"'
				elif os.path.exists(exe):
					exeDir = os.path.dirname(exe)
				self.reset()
				win32api.ShellExecute(0, 'open', exe, filepath,exeDir,1)
				#增加历史访问文件
				self.data.addHistory(command)
				self.data.addHistory(arg)
			except Exception as e:
				#google search
				self.commandField.delete(0,END)
				self.commandField.insert(END,'g')
				self.argField.delete(0,END)
				self.argField.insert(END,command + ' ' + arg)
				self.execute()

			self.argField.delete(0,END)
			self.commandField.delete(0,END)
			self.commandField.focus()

		hideAhk = self.data.path + 'sys/hide.exe'
		if not self.close and os.path.isfile(hideAhk):
			win32api.ShellExecute(0, 'open', hideAhk, '','./',1)
		else:
			self.app.destroy()

	#删除一个单词
	def delWord(self,e):
		widget = e.widget
		currentStr = widget.get()
		strLen = len(currentStr)
		if strLen:
			i = strLen-1
			char = currentStr[i]
			lastIsChar = re.match('\w',char)
			while i>-1:
				i = i-1
				char = currentStr[i]
				if not re.match('\w',char): #非字母
					if not lastIsChar:
						i = i + 1
					break
			widget.delete(i,END)

	#设置提示的内容
	def setPop(self,d,widget):
		if d:
			#已经插入的个数
			insertCnt = 0
			#用于去重，key表示已经插入的path
			insertedPath = {}
			#插入的字符串
			insertStr = ''
			#当前的路径
			path = ''
			#给command list的序列
			lastList = []

			size = self.listbox.size()
			if size:
				self.listbox.delete(0,size)
			for i in d:
				dLen = len(i)
				if dLen>2 and i[2]:
					insertStr = i[0] + ' ' + i[2] +' ' + i[1]
				else:
					insertStr = '%s '*dLen%i
				if dLen>2:
					path = i[1]
				else:
					path = i[0]
				#print(path,i)
				if insertedPath.get(path.upper()):
					if 1==dLen:
						continue
				insertedPath[path.upper()]=True
				self.listbox.insert(END,insertStr)
				insertCnt+=1
				lastList.append(i)
				if insertCnt == self.maxItem:
					break
			if widget == self.commandField:
				self.lastCommandList = lastList
			else:
				self.lastArgList = lastList
			#print(d)
			#print(insertedPath)
			#self.listbox.selection_set(first=0,last=0)
		self.data.switchDb()
	#清空提示
	def emptyPop(self):
		size = self.listbox.size()
		if size:
			self.listbox.delete(0,size)

	#请空上次的输入和上次的选择,参数
	def reset(self):
		self.lastInput=['','']
		self.selectTxt=['','']
		self.argv = []
		self.label.config({'text':''})
		self.emptyPop()

	def run(self):
		self.app.mainloop()

	def getWindowId(self):
		return win32gui.GetForegroundWindow();

	def sorted(self,item):
		s = item[0]
		sw = 2 if s.startswith(self.inputStr) else 1
		lenght = len(s)
		return lenght/(lenght+sw)

if '__main__'==__name__ :
	Window().run()
	#Data().reindex()
