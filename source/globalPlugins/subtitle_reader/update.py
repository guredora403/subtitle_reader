#coding=utf-8

import os
import re
from sys import version_info
if version_info.major == 2:
	from urllib import quote_plus, urlopen, urlretrieve as downloadFile
else:
	from urllib.request import urlopen, urlretrieve as downloadFile
	from urllib.parse import quote_plus

from threading import Thread

from nvwave import playWaveFile as play

from .version import version
from .config import conf
from .gui import UpdateDialog, wx

soundPath = os.path.dirname(__file__) + r'\sounds'
sourceUrl = 'https://raw.githubusercontent.com/maxe-hsieh/subtitle_reader/main/source'
assetUrl = 'https://github.com/maxe-hsieh/subtitle_reader/releases/latest/download'
tempDir = os.getenv('temp')

class Update:
	def __init__(self):
		self.checkThreadObj = None
		self.dialog = None
		self.downloadThreadObj = None
		self.checkOnStartup()
	
	def checkOnStartup(self):
		if not conf['checkUpdateOnStartup']:
			return
		
		self.execute(onStartup=True)
	
	def manualCheck(self, event):
		conf['skipVersion'] = '0'
		play(soundPath + r'\updateChecking.wav')
		self.execute()
	
	def toggleCheckOnStartup(self, event):
		menu = event.GetEventObject()
		id = menu.FindItem(u'啟動時檢查更新(&A)')
		item = menu.FindItemById(id)
		status = conf['checkUpdateOnStartup'] = not conf['checkUpdateOnStartup']
		item.Check(status)
	
	def execute(self, onStartup=False):
		if self.checkThreadObj and self.checkThreadObj.is_alive():
			return
		
		if self.dialog:
			return
		
		self.checkThreadObj = Thread(target=self.checkThread, kwargs={'onStartup': onStartup})
		self.checkThreadObj.start()
	
	def checkThread(self, onStartup=False):
		info = self.newVersion = self.getNewVersion()
		if not info:
			if not onStartup:
				wx.CallAfter(self.isLatestVersion)
			
			return
		
		if info['error']:
			if not onStartup:
				wx.CallAfter(self.checkError)
			
			return
		
		if onStartup and info['version'] == conf['skipVersion']:
			return
		
		play(soundPath + r'\newVersionFound.wav')
		wx.CallAfter(self.showDialog)
	
	def getNewVersion(self):
		info = {'version': 0, 'changelog': '', 'error': None}
		try:
			res = urlopen(sourceUrl + '/manifest.ini')
			text = res.read().decode('utf-8')
			res.close()
			
			if res.getcode() != 200:
				info['error'] = True
				return info
			
			newVersion = re.findall(r'version ?= ?(.+)\r?', text)[0]
			if newVersion == version:
				return
			
			info['version'] = newVersion
			
			res = urlopen(sourceUrl + '/doc/zh_TW/changelog.md')
			text = res.read().decode('utf-8')
			res.close()
			
			info['changelog'] = text
			return info
		except:
			info['error'] = True
			return info
		
	
	def isLatestVersion(self):
		wx.MessageBox(u'您已升級到最新版本，祝您關穎愉快！', '恭喜', style=wx.ICON_EXCLAMATION)
	
	def checkError(self):
		wx.MessageBox(u'檢查更新失敗', '錯誤', style=wx.ICON_ERROR)
	
	def showDialog(self):
		dlg = self.dialog = UpdateDialog(self.newVersion['version'])
		dlg.changelogText.SetValue(self.newVersion['changelog'])
		dlg.updateNow.Bind(wx.EVT_BUTTON, self.updateNow)
		dlg.skipVersion.Bind(wx.EVT_BUTTON, self.skipVersion)
		dlg.later.Bind(wx.EVT_BUTTON, self.later)
		dlg.Bind(wx.EVT_CLOSE, self.onClose)
		dlg.Show()
	
	def updateNow(self, event):
		if self.downloadThreadObj and self.downloadThreadObj.is_alive():
			return
		
		play(soundPath + r'\updating.wav')
		self.downloadThreadObj = Thread(target=self.downloadThread)
		self.downloadThreadObj.start()
	
	def downloadThread(self):
		filename = 'subtitle_reader.nvda-addon'
		with open(tempDir + '\\' + filename, 'w'):
			pass
		
		try:
			file = downloadFile(assetUrl + '/' + filename, tempDir + '\\' + filename, reporthook=self.updateProgress)
			play(soundPath + r'\downloadCompleted.wav')
			self.dialog.Close()
			os.system('start ' + file[0])
		except:
			wx.CallAfter(self.downloadError())
		
	
	def updateProgress(self, blockCount, blockSize, total):
		percent = 100 * blockCount * blockSize / total
		wx.CallAfter(self.dialog.progress.SetValue, percent)
	
	def downloadError(self):
		play(soundPath + r'\downloadError.wav')
		wx.MessageBox(u'下載更新失敗', '錯誤', style=wx.ICON_ERROR, parent=self.dialog)
	
	def skipVersion(self, event):
		play(soundPath + r'\skipVersion.wav')
		conf['skipVersion'] = self.newVersion['version']
		self.dialog.Close()
	
	def later(self, event):
		play(soundPath + r'\closeDialog.wav')
		self.dialog.Close()
	
	def onClose(self, event):
		self.dialog.Destroy()
		self.dialog = None
	
