import os
import gzip
import uuid
import json
from PySide2 import QtGui, QtWidgets, QtCore

class Annotation(object):

	def __init__(self, frameList):
		self.annot = {}
		self.frameList = frameList

		self.penWhite = QtGui.QPen(QtCore.Qt.white, 1.0, QtCore.Qt.SolidLine)
		self.penRed = QtGui.QPen(QtCore.Qt.red, 1.0, QtCore.Qt.SolidLine)
		self.penGreen = QtGui.QPen(QtCore.Qt.green, 1.0, QtCore.Qt.SolidLine)
		self.penBlue = QtGui.QPen(QtCore.Qt.blue, 1.0, QtCore.Qt.SolidLine)

	def Load(self, fina):
		inFi = gzip.open(fina, mode='rb')
		self.annot = json.loads(inFi.read().decode('utf-8'))

	def Save(self, fina):
		
		outFi = gzip.open(fina, mode='wb')
		outFi.write(json.dumps(self.annot).encode('utf-8'))
		del outFi

	def Draw(self, scene, zoomScale, selectedObj, currentIndex):
		if currentIndex not in self.annot: return

		frameAnnot = self.annot[currentIndex]

		if 'boxes' in frameAnnot:
			for boxid, box in frameAnnot['boxes'].items():
				print (box)

				currentPen = self.penGreen
				if selectedObj is not None and "box:"+boxid == selectedObj:
					currentPen = self.penRed

				pt1 = (box[0][0] * zoomScale, box[0][1] * zoomScale)
				pt2 = (box[1][0] * zoomScale, box[1][1] * zoomScale)

				scene.addRect(pt1[0], pt1[1], 
					pt2[0]-pt1[0], pt2[1]-pt1[1], currentPen)

		#spt = (pt[0] * zoomScale, pt[1] * zoomScale)
		#scene.addLine(spt[0]-5., spt[1], spt[0]+5., spt[1], currentPen)
		#scene.addLine(spt[0], spt[1]-5., spt[0], spt[1]+5., currentPen)

	def _InitFrameIfNotExist(self, frameIndex):
		frameName = self.frameList[frameIndex]
		if frameName not in self.annot:
			self.annot[frameName] = {'points': [], 'boxes': []}

	def FrameHasData(self, frameIndex):
		frameName = self.frameList[frameIndex]
		return frameName in self.annot

	def AddPoint(self, frameIndex, pt):

		newId = str(uuid.uuid4())
		self._InitFrameIfNotExist(frameIndex)
		frameName = self.frameList[frameIndex]
		self.annot[frameName]['points'][newId] = pt
		return newId

	def RemovePoint(self, frameIndex, ptId):
		frameName = self.frameList[frameIndex]
		del self.annot[frameName][ptId]

		if len(self.annot[frameName]) == 0:
			del self.annot[frameName]

	def UpdatePoint(self, frameIndex, ptId, ptPos):

		frameName = self.frameList[frameIndex]
		self.annot[frameName][ptId] = ptPos

	def AddBox(self, currentIndex, tempCreateBox):
		print ("add box", tempCreateBox)
		newId = str(uuid.uuid4())
		if currentIndex not in self.annot: self.annot[currentIndex] = {}
		if 'boxes' not in self.annot[currentIndex]: self.annot[currentIndex]['boxes'] = {}

		self.annot[currentIndex]['boxes'][newId] = tempCreateBox[:]
		return 'box:'+newId
	
	def DeleteSelection(self, currentIndex, selectedObj):
		print ("del", selectedObj)
		selectedObjSplit = selectedObj.split(":")		

		frameAnnot = self.annot[currentIndex]

		if 'boxes' in frameAnnot:
			if selectedObjSplit[1] in frameAnnot['boxes']:
				del frameAnnot['boxes'][selectedObjSplit[1]]

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

		frameAnnot = self.annot[currentIndex]
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

