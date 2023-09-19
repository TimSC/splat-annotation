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

	def _ReadAnnotation(self):

		if 0:
			self.annot = {}
			self.imgToFilename = {}
			self.nameToImgFina = {}
			self.imgNames = []

			#inTar = tarfile.open("/home/tim/Desktop/Helen/annotation.tar.gz", mode='r:gz')
			inTar = tarfile.open("helentop.tar.gz", mode='r:gz')

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

	def SaveAnnotation(self, fina):
		if 0:
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
		return self.imageList

	def GetFrame(self, imageFile):

		print (os.path.join(self.pth,imageFile))
		reader = QtGui.QImageReader(os.path.join(self.pth, imageFile))
		return reader.read()

	def GetAnnotations(self, name):
		return []

	def SetAnnotation(self, name, pts):
		pass

	def GetLinks(self):
		return []

