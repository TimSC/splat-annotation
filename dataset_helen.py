from PySide2 import QtGui, QtWidgets
import os
import tarfile
import io

class DatasetHelen(object):
	
	def __init__(self):
		self.annot = {}
		self.imgToFilename = {}
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
			self.imgToFilename[imageName] = fina

	def SaveAnnotation(self, fina):
		outTar = tarfile.open(fina, mode='w:gz')

		for imageName in self.annot:

			outData = io.BytesIO()
			outData.write(u"{}\n".format(imageName).encode("utf-8"))
			for pt in self.annot[imageName]:
				outData.write(u"{} , {}\n".format(pt[0],pt[1]).encode("utf-8"))

			tarInfo = tarfile.TarInfo(self.imgToFilename[imageName])
			tarInfo.size = len(outData.getvalue())
			outData.seek(0)
			outTar.addfile(tarInfo, fileobj=outData)

		outTar.close()

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

	def SetAnnotations(self, name, pts):
		self.annot[name] = pts

