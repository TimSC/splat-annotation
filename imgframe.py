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

	def __init__(self):
		QtWidgets.QWidget.__init__(self)

		self.dataset = dataset_imageseq.Dataset()
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

		self.actionPropagate = self.toolbar.addAction("Propagate")
		self.actionPropagate.triggered.connect(self.Propagate)

		self.scene = MyQGraphicsScene()
		self.scene.mousePress.connect(self.MousePressEvent)
		self.scene.mouseMove.connect(self.MouseMoveEvent)
		self.scene.mouseRelease.connect(self.MouseReleaseEvent)
		self.view = QtWidgets.QGraphicsView(self.scene)
		self.layout.addWidget(self.view, 1)
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

		penWhite = QtGui.QPen(QtCore.Qt.white, 1.0, QtCore.Qt.SolidLine)
		penRed = QtGui.QPen(QtCore.Qt.red, 1.0, QtCore.Qt.SolidLine)
		penBlue = QtGui.QPen(QtCore.Qt.blue, 1.0, QtCore.Qt.SolidLine)
		
		annotations = self.annot.GetAnnotations(self.currentIndex)

		for ptId, pt in annotations.items():
			currentPen = penWhite
			if self.selectedPointId is not None and ptId == self.selectedPointId:
				currentPen = penRed

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
		if a.key() == ord("["):
			self.PrevFrame()
		if a.key() == ord("]"):
			self.NextFrame()
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

	def _UpdateToolButtons(self):
		self.actionSelect.setChecked(self.toolMode=="select")
		self.actionAddPoint.setChecked(self.toolMode=="add")
		self.actionRemovePoint.setChecked(self.toolMode=="remove")

	def _SelectionChanged(self):
		img = self.dataset.GetFrame(self.frameList[self.currentIndex])
		self.SetFrame(img)

	def SaveAnnotation(self):
		self.annot.SaveAnnotation()

	def NextFrame(self):
		ind = self.currentIndex + 1
		if len(self.frameList) < 0:
			ind = len(self.frameList) - 1
		self.currentIndex = ind
		self._SelectionChanged()

	def PrevFrame(self):
		ind = self.currentIndex - 1
		if ind < 0:
			ind = 0
		self.currentIndex = ind
		self._SelectionChanged()

	def SaveAnnotation(self):
		self.annot.Save("annotation.gz")

