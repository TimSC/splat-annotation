from PySide2 import QtGui, QtWidgets, QtCore
import annotation
import dataset_imageseq
import os

class MyQGraphicsScene(QtWidgets.QGraphicsScene):
	mousePress = QtCore.Signal(list)
	mouseMove = QtCore.Signal(list)
	mouseRelease = QtCore.Signal(list)

	def __init__(self):
		QtWidgets.QGraphicsScene.__init__(self)

	def mousePressEvent(self, event):
		scenePos = event.scenePos()
		self.mousePress.emit([scenePos.x(), scenePos.y()])

	def mouseMoveEvent(self, event):
		scenePos = event.scenePos()
		self.mouseMove.emit([scenePos.x(), scenePos.y()])

	def mouseReleaseEvent(self, event):
		scenePos = event.scenePos()
		self.mouseRelease.emit([scenePos.x(), scenePos.y()])

class FrameView(QtWidgets.QWidget):

	def __init__(self, pth):
		QtWidgets.QWidget.__init__(self)

		self.dataset = dataset_imageseq.Dataset(pth)
		self.frameList = self.dataset.GetFrameNames()
		self.currentIndex = 0

		self.selectedPointId = None
		self.currentFrame = None
		self.zoomScale = 1.0
		self.prevPressPos = None
		self.dragThreshold = 10.0
		self.dragActive = False
		self.toolMode = "select"
		self.annot = annotation.Annotation(self.frameList)
		if os.path.exists("annotation.gz"):
			self.annot.Load("annotation.gz")

		self.layout = QtWidgets.QVBoxLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)

		self.toolbar = QtWidgets.QToolBar()
		self.layout.addWidget(self.toolbar, 0)

		self.actionSave = self.toolbar.addAction("Save")
		self.actionSave.triggered.connect(self.SaveAnnotation)

		self.actionZoomIn = self.toolbar.addAction("Zoom In")
		self.actionZoomIn.triggered.connect(self.ZoomIn)
		self.actionZoomOut = self.toolbar.addAction("Zoom Out")
		self.actionZoomOut.triggered.connect(self.ZoomOut)

		self.actionSelect = self.toolbar.addAction("Select/Move")
		self.actionSelect.setCheckable(True)
		self.actionSelect.setChecked(True)
		self.actionSelect.triggered.connect(self.Select)

		self.actionAddPoint = self.toolbar.addAction("Add Point")
		self.actionAddPoint.setCheckable(True)
		self.actionAddPoint.setChecked(False)
		self.actionAddPoint.triggered.connect(self.AddPoint)

		self.actionRemovePoint = self.toolbar.addAction("Remove Point")
		self.actionRemovePoint.setCheckable(True)
		self.actionRemovePoint.setChecked(False)
		self.actionRemovePoint.triggered.connect(self.RemovePoint)

		self.actionPropagate = self.toolbar.addAction("Propagate All")
		self.actionPropagate.triggered.connect(self.Propagate)

		self.actionPropagatePoint = self.toolbar.addAction("Propagate Point")
		self.actionPropagatePoint.triggered.connect(self.PropagatePoint)

		self.scene = MyQGraphicsScene()
		self.scene.mousePress.connect(self.MousePressEvent)
		self.scene.mouseMove.connect(self.MouseMoveEvent)
		self.scene.mouseRelease.connect(self.MouseReleaseEvent)
		self.view = QtWidgets.QGraphicsView(self.scene)
		self.layout.addWidget(self.view, 1)

		self.penWhite = QtGui.QPen(QtCore.Qt.white, 1.0, QtCore.Qt.SolidLine)
		self.penRed = QtGui.QPen(QtCore.Qt.red, 1.0, QtCore.Qt.SolidLine)
		self.penGreen = QtGui.QPen(QtCore.Qt.green, 1.0, QtCore.Qt.SolidLine)
		self.penBlue = QtGui.QPen(QtCore.Qt.blue, 1.0, QtCore.Qt.SolidLine)

		self._SelectionChanged()

	def DrawFrame(self):
		if self.currentFrame is None: return

		si = self.currentFrame.size()
		frameZoomed = self.currentFrame.scaled(si.width()*self.zoomScale, si.height()*self.zoomScale)
		
		si2 = frameZoomed.size()
		self.scene.clear()
		self.scene.setSceneRect(0, 0, si2.width(), si2.height())
		pix = QtGui.QPixmap(frameZoomed)

		gpm = QtWidgets.QGraphicsPixmapItem(pix)
		self.scene.addItem(gpm)
		
		annotations = self.annot.GetAnnotations(self.currentIndex)

		for ptId, pt in annotations.items():
			currentPen = self.penGreen
			if self.selectedPointId is not None and ptId == self.selectedPointId:
				currentPen = self.penRed

			spt = (pt[0] * self.zoomScale, pt[1] * self.zoomScale)
			self.scene.addLine(spt[0]-5., spt[1], spt[0]+5., spt[1], currentPen)
			self.scene.addLine(spt[0], spt[1]-5., spt[0], spt[1]+5., currentPen)

	def SetSelectedPoint(self, ptId):
		self.selectedPointId = ptId
		self.DrawFrame()

	def GetNearestPoint(self, annotations, pos):
		bestDist = None
		bestId = None
		for ptId, pt in annotations.items():
			spt = (pt[0], pt[1])
			dist = ((spt[0] - pos[0]) ** 2. + (spt[1] - pos[1]) ** 2.) ** 0.5
			if bestDist is None or dist < bestDist:
				bestDist = dist
				bestId = ptId
		return bestId

	def MousePressEvent(self, pos):

		self.prevPressPos = pos
		self.dragActive = False
		ipt = (pos[0] / self.zoomScale, pos[1] / self.zoomScale)

		annotations = self.annot.GetAnnotations(self.currentIndex)

		if self.toolMode == "select":
			bestId = self.GetNearestPoint(annotations, ipt)
			self.SetSelectedPoint(bestId)

		elif self.toolMode == "add":
			#print ("add", ipt)
			ptId = self.annot.AddPoint(self.currentIndex, ipt)
			self.SetSelectedPoint(ptId)

		elif self.toolMode == "remove":
			bestId = self.GetNearestPoint(annotations, ipt)
			if bestId is None: return
			if self.selectedPointId == bestId:
				self.SetSelectedPoint(None)
			self.annot.RemovePoint(self.currentIndex, bestId)
			self.DrawFrame()

	def MouseMoveEvent(self, pos):

		if self.prevPressPos is None: return

		if self.toolMode == "select":

			dist = ((self.prevPressPos[0] - pos[0]) ** 2. + (self.prevPressPos[1] - pos[1]) ** 2.) ** 0.5
			if dist > self.dragThreshold:
				self.dragActive = True

			if self.dragActive:

				if self.selectedPointId is not None:

					spt = (pos[0] / self.zoomScale, pos[1] / self.zoomScale)
					self.annot.UpdatePoint(self.currentIndex, self.selectedPointId, spt)
					self.DrawFrame()

	def MouseReleaseEvent(self, pos):
		#print ("Release", pos)

		self.prevPressPos = None
		self.dragActive = False

	def SetFrame(self, frame):
		self.currentFrame = frame
		self.DrawFrame()

	def ZoomIn(self):
		self.zoomScale *= 1.5
		self.DrawFrame()

	def ZoomOut(self):
		self.zoomScale /= 1.5
		self.DrawFrame()

	def keyPressEvent(self, a):
		#shiftHeld = (a.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier != 0)
		if a.key() == ord("["):
			self.PrevFrame(False)
		if a.key() == ord("]"):
			self.NextFrame(False)
		if a.key() == ord("{"):
			self.PrevFrame(True)
		if a.key() == ord("}"):
			self.NextFrame(True)
		if a.key() == ord("-"):
			self.ZoomOut()
		if a.key() in [ord("+"), ord("=")]:
			self.ZoomIn()

	def AddPoint(self):
		self.toolMode = "add"
		self._UpdateToolButtons()

	def RemovePoint(self):
		self.toolMode = "remove"
		self._UpdateToolButtons()

	def Select(self):
		self.toolMode = "select"
		self._UpdateToolButtons()

	def Propagate(self):
		#Copy missing points from previous frame
		self.annot.Propagate(self.currentIndex)
		self.DrawFrame()

	def PropagatePoint(self):
		#Copy specified point from previous frame
		self.annot.PropagatePoint(self.currentIndex, self.selectedPointId)
		self.DrawFrame()

	def _UpdateToolButtons(self):
		self.actionSelect.setChecked(self.toolMode=="select")
		self.actionAddPoint.setChecked(self.toolMode=="add")
		self.actionRemovePoint.setChecked(self.toolMode=="remove")

	def _SelectionChanged(self):
		img = self.dataset.GetFrame(self.frameList[self.currentIndex])
		self.SetFrame(img)

	def SaveAnnotation(self):
		self.annot.SaveAnnotation()

	def NextFrame(self, onlykeyFrames):
		if not onlykeyFrames:
			ind = self.currentIndex + 1
		else:
			cursor = self.currentIndex + 1
			while cursor < len(self.frameList):
				if self.annot.FrameHasData(cursor):
					ind = cursor
					break
				cursor += 1
			ind = cursor

		if ind >= len(self.frameList):
			ind = len(self.frameList) - 1
		self.currentIndex = ind
		self._SelectionChanged()

	def PrevFrame(self, onlykeyFrames):

		if not onlykeyFrames:
			ind = self.currentIndex - 1
		else:
			cursor = self.currentIndex - 1
			while cursor >= 0:
				if self.annot.FrameHasData(cursor):
					ind = cursor
					break
				cursor -= 1
			ind = cursor
			
		if ind < 0:
			ind = 0
		self.currentIndex = ind
		self._SelectionChanged()

	def SaveAnnotation(self):
		self.annot.Save("annotation.gz")

