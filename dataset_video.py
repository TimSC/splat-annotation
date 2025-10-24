from PySide2 import QtGui, QtWidgets, QtCore
import os
import tarfile
import io
import tempfile
import subprocess

class DatasetVideo:
	
	def __init__(self, pth):

		self.pth = pth
		self.tmpDir = None
		self.fullyExtracted = False
		self.imageList = None
		self.Extract(True)

	def GetFrame(self, frameIndex):

		if frameIndex == len(self.imageList)-1 and not self.fullyExtracted:
			self.Extract()
			self.fullyExtracted = True

		reader = QtGui.QImageReader(os.path.join(self.tmpDir.name, self.imageList[frameIndex]))
		return reader.read()

	def NumFrames(self):
		return len(self.imageList)

	def Extract(self, limit=False):

		self.tmpDir = tempfile.TemporaryDirectory()
		
		if os.path.exists(self.pth):
			cmd = ['ffmpeg', '-i', self.pth]
			if limit:
				cmd.extend(('-to', '1'))
			cmd.append(os.path.join(self.tmpDir.name, 'vid%05d.jpg'))
		print (cmd)
		subprocess.run(cmd)

		self.imageList = os.listdir(self.tmpDir.name)
		self.imageList.sort()

