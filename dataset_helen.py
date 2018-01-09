from PySide2 import QtGui, QtWidgets
import os
import tarfile
import io

class DatasetHelen(object):
	
	def __init__(self):
		self.annot = {}
		self.imgToFilename = {}
		self.nameToImgFina = {}
		self._ReadAnnotation()
		self.reversed = False
		self.links = (range(0, 41), #Chin
			range(41, 58), #Nose
			range(58, 72), #Upper outer lip
			range(72, 86), #Lower outer lip
			range(86, 101), #Upper inner lip
			range(101, 114), #Lower inner lip
			range(114, 126), #Their left eye, upper
			range(126, 134), #Their left eye, lower
			range(134, 146), #Their right eye, upper
			range(146, 154), #Their right eye, lower
			range(154, 165), #Their left eyebrow, upper
			range(165, 174), #Their left eyebrow, lower
			range(174, 185), #Their right eyebrow, upper
			range(185, 194), #Their right eyebrow, lower
			range(194, 201), #Hair
			)
		assert len(self.links[6]) == len(self.links[8])
		assert len(self.links[7]) == len(self.links[9])
		assert len(self.links[10]) == len(self.links[12])
		assert len(self.links[11]) == len(self.links[13])

	def _ReadAnnotation(self):

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
		print "/home/tim/Desktop/Helen/imgs/{}.jpg".format(fina)
		reader = QtGui.QImageReader("/home/tim/Desktop/Helen/imgs/{}.jpg".format(fina))
		if self.reversed:
			img = reader.read()
			return img.mirrored(True, False)
		return reader.read()

	def FlipPointsHorizontal(self, originalPts, width):

		pts=[]
		ptsReversed = reversed([originalPts[i] for i in self.links[0]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = reversed([originalPts[i] for i in self.links[1]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = reversed([originalPts[i] for i in self.links[2]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = reversed([originalPts[i] for i in self.links[3]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = reversed([originalPts[i] for i in self.links[4]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = reversed([originalPts[i] for i in self.links[5]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[8]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[9]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[6]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[7]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[12]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[13]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[10]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = [originalPts[i] for i in self.links[11]]
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])
		ptsReversed = reversed([originalPts[i] for i in self.links[14]])
		pts.extend([(width-pt[0], pt[1]) for pt in ptsReversed])

		assert len(pts) == len(originalPts)
		return pts

	def GetAnnotations(self, name):
		if not self.reversed:
			return self.annot[name]
		else:
			img = self.GetFrame(name)
			w = img.size().width()
			return self.FlipPointsHorizontal(self.annot[name], w)

	def SetAnnotations(self, name, pts):
		if not self.reversed:
			self.annot[name] = pts
		else:
			pass

	def GetLinks(self):
		return self.links

