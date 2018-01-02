from PySide2 import QtGui, QtWidgets
import os

class DatasetHelen(object):
	
	def __init__(self):
		self.annot = {}
		self._ReadAnnotation()

	def _ReadAnnotation(self):

		self.annot = {}
		annotationPath = "/home/tim/Desktop/Helen/annotation"
		for fina in os.listdir(annotationPath):
			fullFina = os.path.join(annotationPath, fina)

			fi = open(fullFina, "rt")
			imageName = None
			imagePoints = []
			for linum, li in enumerate(fi.readlines()):
				lis = li.strip()
				if linum == 0:
					imageName = lis					
				else:
					pt = map(float, lis.split(","))
					imagePoints.append(pt)

			self.annot[imageName] = imagePoints
			#print imageName, self.annot[imageName]

	def GetFrameNames(self):
		frameNames = list(self.annot.keys())
		frameNames.sort()
		return frameNames

	def GetFrame(self, name):
		print "/home/tim/Desktop/Helen/imgs/{}.jpg".format(name)
		reader = QtGui.QImageReader("/home/tim/Desktop/Helen/imgs/{}.jpg".format(name))
		return reader.read()

	def GetAnnotations(self, name):
		return self.annot[name]

