from PySide2 import QtGui, QtWidgets, QtCore
import annotation
import dataset_imageseq
import dataset_video
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

		self.frameList = None
		self.currentIndex = 0
		self.dataset = None

		self.selectedObj = None
		self.tempCreateBox = None
		self.currentFrame = None
		self.zoomScale = 1.0
		self.prevPressPos = None
		self.dragThreshold = 10.0
		self.dragActive = False
		self.toolMode = "select"
		self.annot = annotation.Annotation()
		#if os.path.exists("annotation.gz"):
		#	self.annot.Load("annotation.gz")

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

		#self.actionAddPoint = self.toolbar.addAction("Add Point")
		#self.actionAddPoint.setCheckable(True)
		#self.actionAddPoint.setChecked(False)
		#self.actionAddPoint.triggered.connect(self.AddPoint)

		#self.actionRemovePoint = self.toolbar.addAction("Remove Point")
		#self.actionRemovePoint.setCheckable(True)
		#self.actionRemovePoint.setChecked(False)
		#self.actionRemovePoint.triggered.connect(self.RemovePoint)

		#self.actionPropagate = self.toolbar.addAction("Propagate All")
		#self.actionPropagate.triggered.connect(self.Propagate)

		#self.actionPropagatePoint = self.toolbar.addAction("Propagate Point")
		#self.actionPropagatePoint.triggered.connect(self.PropagatePoint)

		self.actionAddBox = self.toolbar.addAction("Add Box")
		self.actionAddBox.setCheckable(True)
		self.actionAddBox.triggered.connect(self.AddBox)

		self.scene = MyQGraphicsScene()
		self.scene.mousePress.connect(self.MousePressEvent)
		self.scene.mouseMove.connect(self.MouseMoveEvent)
		self.scene.mouseRelease.connect(self.MouseReleaseEvent)
		self.view = QtWidgets.QGraphicsView(self.scene)
		self.view.setMouseTracking(True)
		self.layout.addWidget(self.view, 1)

		self.penWhite = QtGui.QPen(QtCore.Qt.white, 1.0, QtCore.Qt.SolidLine)

		self._SelectionChanged()

	def SetPath(self, pth):
		print ("pth", pth)
		self.dataset = dataset_video.DatasetVideo(pth)
		self.annot = annotation.Annotation()

		self.currentIndex = 0
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
		
		self.annot.Draw(self.scene, self.zoomScale, self.selectedObj, self.currentIndex)

		if self.toolMode == "addbox" and self.tempCreateBox is not None:
			self.scene.addRect(self.tempCreateBox[0][0], self.tempCreateBox[0][1], 
				self.tempCreateBox[1][0]-self.tempCreateBox[0][0], self.tempCreateBox[1][1]-self.tempCreateBox[0][1], self.penWhite)

	def SetSelected(self, objId):
		self.selectedObj = objId
		self.DrawFrame()

	def MousePressEvent(self, pos):

		self.prevPressPos = pos
		self.dragActive = False
		ipt = (pos[0] / self.zoomScale, pos[1] / self.zoomScale)

		if self.toolMode == "select":
			bestId = self.annot.GetNearestPoint(self.currentIndex, ipt)
			self.SetSelected(bestId)

		#elif self.toolMode == "add":
		#	#print ("add", ipt)
		#	ptId = self.annot.AddPoint(self.currentIndex, ipt)
		#	self.SetSelected(ptId)

		#elif self.toolMode == "remove":
		#	bestId = self.annot.GetNearestPoint(self.currentIndex, ipt)
		#	if bestId is None: return
		#	if self.selectedPointId == bestId:
		#		self.SetSelected(None)
		#	self.annot.RemovePoint(self.currentIndex, bestId)
		#	self.DrawFrame()

		elif self.toolMode == "addbox":
			if self.tempCreateBox is None:
				self.tempCreateBox = [ipt, None]
			else:
				self.annot.AddBox(self.currentIndex, self.tempCreateBox)
				self.tempCreateBox = None
				self.DrawFrame()

			#ptId = self.annot.AddPoint(self.currentIndex, ipt)
			#self.SetSelected(ptId)

	def MouseMoveEvent(self, pos):

		if self.toolMode == "addbox" and self.tempCreateBox is not None:
			# Show box creation
			spt = (pos[0] / self.zoomScale, pos[1] / self.zoomScale)
			self.tempCreateBox[1] = spt
			self.DrawFrame()

		if self.prevPressPos is None: return

		if self.toolMode == "select":

			dist = ((self.prevPressPos[0] - pos[0]) ** 2. + (self.prevPressPos[1] - pos[1]) ** 2.) ** 0.5
			if dist > self.dragThreshold:
				self.dragActive = True

			if self.dragActive:
				pass
				#if self.selectedObj is not None:

				#	spt = (pos[0] / self.zoomScale, pos[1] / self.zoomScale)
				#	self.annot.UpdatePoint(self.currentIndex, self.selectedPointId, spt)
				#	self.DrawFrame()


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
		if a.key() == QtCore.Qt.Key_Delete:
			self.DeleteSelection()

	#def AddPoint(self):
	#	self.toolMode = "add"
	#	self._UpdateToolButtons()

	#def RemovePoint(self):
	#	self.toolMode = "remove"
	#	self._UpdateToolButtons()

	def Select(self):
		self.toolMode = "select"
		self._UpdateToolButtons()

	def AddBox(self):
		self.toolMode = "addbox"
		self._UpdateToolButtons()

	def DeleteSelection(self):
		self.annot.DeleteSelection(self.currentIndex, self.selectedObj)
		self.SetSelected(None)

	def _UpdateToolButtons(self):
		self.actionSelect.setChecked(self.toolMode=="select")
		#self.actionAddPoint.setChecked(self.toolMode=="add")
		#self.actionRemovePoint.setChecked(self.toolMode=="remove")
		self.actionAddBox.setChecked(self.toolMode=="addbox")

	def _SelectionChanged(self):
		if self.dataset is not None:
			img = self.dataset.GetFrame(self.currentIndex)
			self.SetFrame(img)

	def SaveAnnotation(self):
		self.annot.SaveAnnotation()

	def NextFrame(self, onlykeyFrames):
		if not onlykeyFrames:
			ind = self.currentIndex + 1
		else:
			cursor = self.currentIndex + 1
			while cursor < self.dataset.NumFrames():
				if self.annot.FrameHasData(cursor):
					ind = cursor
					break
				cursor += 1
			ind = cursor

		if ind >= self.dataset.NumFrames():
			ind = self.dataset.NumFrames() - 1
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

