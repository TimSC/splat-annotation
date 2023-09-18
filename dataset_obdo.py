from PySide2 import QtGui, QtWidgets
import os
import tarfile
import io

class DatasetObdo(object):
	
	def __init__(self):
		self.defaultAnnotationFiNa = "obdo.tar.gz"
		self.annot = {}
		self.imgToFilename = {}
		self.nameToImgFina = {}
		self._ReadAnnotation()
		self.links = [range(0, 5), #Chin 
			range(5, 8), #Nose
			[8, 9, 10, 11, 8], #Mouth outer shape
			range(12, 14), range(14, 16), #Eyes
			range(16, 18), range(18, 20)] #Eyebrows

	def _ReadAnnotation(self):

		self.annot = {}
		self.imgToFilename = {}
		self.nameToImgFina = {}
		self.imgNames = []
		inTar = tarfile.open(self.defaultAnnotationFiNa, mode='r:gz')

		for i, tarInfo in enumerate(inTar.getmembers()):

			fi = inTar.extractfile(tarInfo)
			if fi is None: continue
			imageName = None
			imagePoints = []
			for linum, li in enumerate(fi.readlines()):
				lis = li.strip()
				if linum == 0:
					imageName = lis					
				else:
					pt = map(float, lis.split(","))
					imagePoints.append(pt)

			imageName2 = "{:04d}: {}".format(i, imageName)
			self.annot[imageName2] = imagePoints
			self.imgToFilename[imageName2] = tarInfo.name
			self.nameToImgFina[imageName2] = imageName
			self.imgNames.append(imageName2)

	def SaveAnnotation(self, fina=None):
		if fina is None:
			fina = self.defaultAnnotationFiNa
		print (fina)
		outTar = tarfile.open(fina, mode='w:gz')

		for imageName in self.imgNames:

			outData = io.BytesIO()
			outData.write(u"{}\n".format(self.nameToImgFina[imageName]).encode("utf-8"))
			for pt in self.annot[imageName]:
				outData.write(u"{} , {}\n".format(pt[0],pt[1]).encode("utf-8"))

			tarInfo = tarfile.TarInfo(self.imgToFilename[imageName])
			tarInfo.size = len(outData.getvalue())
			outData.seek(0)
			outTar.addfile(tarInfo, fileobj=outData)

		outTar.close()

	def GetFrameNames(self):
		return self.imgNames

	def GetFrame(self, name):
		fina = self.nameToImgFina[name]
		fullFina = "/home/tim/datasets/Oobee/Sample_images/Original/{}.jpg".format(fina)
		if os.path.exists(fullFina):
			reader = QtGui.QImageReader(fullFina)
			return reader.read()
		fullFina = "/home/tim/datasets/Oobee/Sample_images/Original/{}.JPG".format(fina)
		if os.path.exists(fullFina):
			reader = QtGui.QImageReader(fullFina)
			return reader.read()

	def GetAnnotations(self, name):
		return self.annot[name]

	def SetAnnotation(self, name, pts):
		if name not in self.annot:
			raise RuntimeError("Don't use SetAnnotation for completely new frames")
		self.annot[name] = pts

	def GetLinks(self):
		return self.links

