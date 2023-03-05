#encoding=utf-8

from __future__ import absolute_import

import addonHandler
addonHandler.initTranslation()

import wx
import gui

tray = gui.mainFrame.sysTrayIcon
toolsMenu = tray.toolsMenu

class Menu(wx.Menu):
	def __init__(self):
		super(Menu, self).__init__()
		# Translators: Subtitle Reader menu on the NVDA tools menu
		self.menuItem = toolsMenu.AppendSubMenu(self, _(u'字幕閱讀器 (&R)'))
		# Translators: Reader toggle switch on the Subtitle Reader menu
		self.switch = self.AppendCheckItem(wx.ID_ANY, _(u'閱讀器開關 (&S)'))
		self.switch.Check(True)
		
		# Translators: toggle menu item whether to prompt wher Youtube info card is already appear
		self.infoCardPrompt = self.AppendCheckItem(wx.ID_ANY, _(u'資訊卡提示(&I)'))
		self.infoCardPrompt.Check(True)
		
		# Translators: This menu item performs a check for updates to the reader
		self.checkForUpdate = self.Append(wx.ID_ANY, _(u'立即檢查更新(&C)'))
		# Translators: This is menu item that open the cnangelog
		self.openChangeLog = self.Append(wx.ID_ANY, _(u'開啟更新日誌(&O)'))
		# Translators: This menu item that can toggle automatic check for update when Subtitle Reader is start
		self.checkUpdateAutomatic = self.AppendCheckItem(wx.ID_ANY, _(u'自動檢查更新(&A)'))
		self.checkUpdateAutomatic.Check(True)
	

class UpdateDialog(wx.Dialog):
	def __init__(self, version):
		super(UpdateDialog, self).__init__(gui.mainFrame, title=_(u'字幕閱讀器 V') + str(version) + _(u' 新版資訊'))
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		# Translators: This label means the edit box content is changelog
		self.changeLogLabel = wx.StaticText(self, label=_(u'更新日誌'))
		self.changelogText = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL, size=(700, -1))
		self.progress = wx.Gauge(self, style=wx.GA_VERTICAL)
		# Translators: This button means now run the update process
		self.updateNow = wx.Button(self, label=_(u'現在更新(&U)'))
		# Translators: This button means that the automatic check for updates will skip this version
		self.skipVersion = wx.Button(self, label=_(u'跳過此版本(&S)'))
		# Translators: This button means close window until next automatic or manual check for update
		self.later = wx.Button(self, label=_(u'晚點再說(&L)'))
		self.SetSizerAndFit(self.sizer)
	
