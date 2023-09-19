from PySide2 import QtGui, QtWidgets
import os
import tarfile
import io

class Dataset(object):
	
	def __init__(self):
		self.annot = {}

		self.pth = "/media/tim/D21AEC821AEC64C7/datasets/medical/vid1/"
		self.imageList = os.listdir(self.pth)
		self.imageList.sort()

	def GetFrameNames(self):
		return self.imageList

	def GetFrame(self, imageFile):

		print (os.path.join(self.pth,imageFile))
		reader = QtGui.QImageReader(os.path.join(self.pth, imageFile))
		return reader.read()


