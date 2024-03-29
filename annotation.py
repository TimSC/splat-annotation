import os
import gzip
import uuid
import json

class Annotation(object):

	def __init__(self, frameList):
		self.annot = {}
		self.frameList = frameList

	def GetAnnotations(self, frameIndex):
		frameName = self.frameList[frameIndex]

		if frameName in self.annot:
			return self.annot[frameName]
		return {}

	def Load(self, fina):
		inFi = gzip.open(fina, mode='rb')
		self.annot = json.loads(inFi.read().decode('utf-8'))

	def Save(self, fina):
		
		outFi = gzip.open(fina, mode='wb')
		outFi.write(json.dumps(self.annot).encode('utf-8'))
		del outFi

	def _InitFrameIfNotExist(self, frameIndex):
		frameName = self.frameList[frameIndex]
		if frameName not in self.annot:
			self.annot[frameName] = {}

	def FrameHasData(self, frameIndex):
		frameName = self.frameList[frameIndex]
		return frameName in self.annot

	def AddPoint(self, frameIndex, pt):

		newId = str(uuid.uuid4())
		self._InitFrameIfNotExist(frameIndex)
		frameName = self.frameList[frameIndex]
		self.annot[frameName][newId] = pt
		return newId

	def RemovePoint(self, frameIndex, ptId):
		frameName = self.frameList[frameIndex]
		del self.annot[frameName][ptId]

		if len(self.annot[frameName]) == 0:
			del self.annot[frameName]

	def UpdatePoint(self, frameIndex, ptId, ptPos):

		frameName = self.frameList[frameIndex]
		self.annot[frameName][ptId] = ptPos
	
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

	def Propagate(self, frameIndex):

		#Rewind to find a frame with annotation
		prevIndex = self.RewindToDataFrame(frameIndex)
		if prevIndex is None: return False
		prevFrame = self.GetAnnotations(prevIndex)

		#Copy points to current frame
		self._InitFrameIfNotExist(frameIndex)
		currentFrame = self.GetAnnotations(frameIndex)

		for ptId, pt in prevFrame.items():
			if ptId not in currentFrame:
				currentFrame[ptId] = pt

		return True

	def PropagatePoint(self, frameIndex, ptId):
		#Rewind to find a frame with annotation
		prevIndex = self.RewindToDataFrame(frameIndex, ptId)
		if prevIndex is None: return False
		prevFrame = self.GetAnnotations(prevIndex)

		#Copy point to current frame
		if ptId in prevFrame:
			self._InitFrameIfNotExist(frameIndex)
			currentFrame = self.GetAnnotations(frameIndex)

			if ptId not in currentFrame:
				currentFrame[ptId] = prevFrame[ptId]

		return True

