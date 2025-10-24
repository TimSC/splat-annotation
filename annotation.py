import os
import gzip
import uuid
import json
from PySide2 import QtGui, QtWidgets, QtCore

class Annotation:

	def __init__(self, pth):
		self.annot = {}
		self.pth = pth
		if pth is not None and os.path.exists(pth):
			self.Load()

		self.penWhite = QtGui.QPen(QtCore.Qt.white, 1.0, QtCore.Qt.SolidLine)
		self.penGray = QtGui.QPen(QtCore.Qt.gray, 1.0, QtCore.Qt.SolidLine)
		self.penRed = QtGui.QPen(QtCore.Qt.red, 1.0, QtCore.Qt.SolidLine)
		self.penGreen = QtGui.QPen(QtCore.Qt.green, 1.0, QtCore.Qt.SolidLine)
		self.penBlue = QtGui.QPen(QtCore.Qt.blue, 1.0, QtCore.Qt.SolidLine)


	def Load(self):
		inFi = gzip.open(self.pth, mode='rb')
		self.annot = json.loads(inFi.read().decode('utf-8'))


	def Save(self):
		
		#Check folder exists, if not, create
		dirName = os.path.dirname(self.pth)
		os.makedirs(dirName, exist_ok=True)

		outFi = gzip.open(self.pth, mode='wb')
		outFi.write(json.dumps(self.annot).encode('utf-8'))
		del outFi


	def Draw(self, scene, zoomScale, selectedObj, currentIndex):
		cis = str(currentIndex)
		if cis in self.annot:

			frameAnnot = self.annot[cis]

			if 'boxes' in frameAnnot:
				for boxid, box in frameAnnot['boxes'].items():

					currentPen = self.penGreen
					if selectedObj is not None and "box:"+boxid == selectedObj:
						currentPen = self.penRed

					pt1 = (box[0][0] * zoomScale, box[0][1] * zoomScale)
					pt2 = (box[1][0] * zoomScale, box[1][1] * zoomScale)

					scene.addRect(pt1[0], pt1[1], 
						pt2[0]-pt1[0], pt2[1]-pt1[1], currentPen)

		# Draw ROI from the first frame
		cis = str(0)
		if currentIndex != 0 and cis in self.annot:

			frameAnnot = self.annot[cis]

			if 'boxes' in frameAnnot:
				for boxid, box in frameAnnot['boxes'].items():

					pt1 = (box[0][0] * zoomScale, box[0][1] * zoomScale)
					pt2 = (box[1][0] * zoomScale, box[1][1] * zoomScale)

					scene.addRect(pt1[0], pt1[1], 
						pt2[0]-pt1[0], pt2[1]-pt1[1], self.penGray)


	def FrameHasData(self, frameIndex):
		frameName = self.frameList[frameIndex]
		return frameName in self.annot


	def AddBox(self, currentIndex, tempCreateBox):
		print ("add box", tempCreateBox)
		newId = str(uuid.uuid4())
		cis = str(currentIndex)
		if cis not in self.annot: self.annot[cis] = {}
		if 'boxes' not in self.annot[cis]: self.annot[cis]['boxes'] = {}

		self.annot[cis]['boxes'][newId] = tempCreateBox[:]
		return 'box:'+newId
	

	def DeleteSelection(self, currentIndex, selectedObj):
		print ("del", selectedObj)
		selectedObjSplit = selectedObj.split(":")		

		cis = str(currentIndex)
		if cis not in self.annot: return
		frameAnnot = self.annot[cis]

		if selectedObjSplit[0] == 'box' and 'boxes' in frameAnnot:
			if selectedObjSplit[1] in frameAnnot['boxes']:
				del frameAnnot['boxes'][selectedObjSplit[1]]


	def DragSelection(self, currentIndex, selectedObj, spt):
		selectedObjSplit = selectedObj.split(":")	
		cis = str(currentIndex)
		
		if cis in self.annot:
			frameAnnot = self.annot[cis]

			if selectedObjSplit[0] == 'box' and 'boxes' in frameAnnot:
				if selectedObjSplit[1] in frameAnnot['boxes']:
					box = frameAnnot['boxes'][selectedObjSplit[1]]
			
					bestPt = None
					bestDist = None
					for i, pt in enumerate(box):
						dist = ((pt[0] - spt[0]) ** 2. + (pt[1] - spt[1]) ** 2.) ** 0.5
						if bestDist is None or dist < bestDist:
							bestPt = i
							bestDist = dist
					box[bestPt] = spt
				
		cis = str(0)
		
		if currentIndex != 0 and cis in self.annot:
			frameAnnot = self.annot[cis]

			if selectedObjSplit[0] == 'box' and 'boxes' in frameAnnot:
				if selectedObjSplit[1] in frameAnnot['boxes']:
					box = frameAnnot['boxes'][selectedObjSplit[1]]
			
					bestPt = None
					bestDist = None
					for i, pt in enumerate(box):
						dist = ((pt[0] - spt[0]) ** 2. + (pt[1] - spt[1]) ** 2.) ** 0.5
						if bestDist is None or dist < bestDist:
							bestPt = i
							bestDist = dist
					box[bestPt] = spt


	def RewindToDataFrame(self, startIndex, mustContainPtId=None):

		#Rewind to find a frame with annotation
		cursor = startIndex - 1
		prevFrame = None
		while prevFrame is None:
			frameName = self.frameList[cursor]
			if frameName in self.annot and (mustContainPtId is None or mustContainPtId in self.annot[frameName]):
				prevFrame = self.annot[frameName]
				continue

			if cursor == 0:
				return None #Can't rewind past beginning
			cursor -= 1
		return cursor


	def GetNearestPoint(self, currentIndex, pos):

		cis = str(currentIndex)
		if cis in self.annot:
			frameAnnot = self.annot[cis]
			bestDist = None
			bestId = None

			if 'boxes' in frameAnnot:
				for boxid, box in frameAnnot['boxes'].items():
					print ("b", box)
					for pt in box:
						dist = ((pt[0] - pos[0]) ** 2. + (pt[1] - pos[1]) ** 2.) ** 0.5
						if bestDist is None or dist < bestDist:
							bestDist = dist
							bestId = "box:"+boxid
		
		# Allow selection of ROI
		cis = str(0)
		if currentIndex != 0 and cis in self.annot:
			frameAnnot = self.annot[cis]
			bestDist = None
			bestId = None

			if 'boxes' in frameAnnot:
				for boxid, box in frameAnnot['boxes'].items():
					print ("b", box)
					for pt in box:
						dist = ((pt[0] - pos[0]) ** 2. + (pt[1] - pos[1]) ** 2.) ** 0.5
						if bestDist is None or dist < bestDist:
							bestDist = dist
							bestId = "box:"+boxid

		return bestId

