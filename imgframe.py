from PySide2 import QtGui, QtWidgets, QtCore

class FrameList(QtWidgets.QComboBox):
	selectionChanged = QtCore.Signal()

	def __init__(self):
		QtWidgets.QComboBox.__init__(self)
		QtCore.QObject.connect(self, QtCore.SIGNAL('activated(int)'), self.FrameChanged)

	def SetFrameNames(self, frameNames):
		self.clear()
		for fn in frameNames:
			self.addItem(fn)

	def FrameChanged(self, ind = None):
		self.selectionChanged.emit()

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
	controlPointsChanged = QtCore.Signal(list)
	nextFrame = QtCore.Signal()
	prevFrame = QtCore.Signal()

	def __init__(self):
		QtWidgets.QWidget.__init__(self)

		self.selectedPointIndex = None
		self.currentFrame = None
		self.zoomScale = 1.0
		self.prevPressPos = None
		self.dragThreshold = 10.0
		self.dragActive = False
		self.links = []

		self.layout = QtWidgets.QVBoxLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)

		self.toolbar = QtWidgets.QToolBar()
		self.layout.addWidget(self.toolbar, 0)
		self.actionZoomIn = self.toolbar.addAction("Zoom In")
		self.actionZoomIn.triggered.connect(self.ZoomIn)
		self.actionZoomOut = self.toolbar.addAction("Zoom Out")
		self.actionZoomOut.triggered.connect(self.ZoomOut)

		self.scene = MyQGraphicsScene()
		self.scene.mousePress.connect(self.MousePressEvent)
		self.scene.mouseMove.connect(self.MouseMoveEvent)
		self.scene.mouseRelease.connect(self.MouseReleaseEvent)
		self.view = QtWidgets.QGraphicsView(self.scene)
		self.layout.addWidget(self.view, 1)
		self.controlPoints = []

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
		for ptNum, pt in enumerate(self.controlPoints):
			currentPen = penWhite
			if self.selectedPointIndex is not None and ptNum == self.selectedPointIndex:
				currentPen = penRed

			spt = (pt[0] * self.zoomScale, pt[1] * self.zoomScale)
			self.scene.addLine(spt[0]-5., spt[1], spt[0]+5., spt[1], currentPen)
			self.scene.addLine(spt[0], spt[1]-5., spt[0], spt[1]+5., currentPen)

		if len(self.controlPoints) > 0:
			for indexList in self.links:
				indexList = list(indexList)
				l = len(indexList)

				#print (l1, l2, len(self.controlPoints))
				for li in range(1, l):
					if indexList[li] >= len(self.controlPoints) or \
						indexList[li-1] >= len(self.controlPoints):
						print ("Link range outside of available points", len(self.controlPoints))
						continue
					pt1 = self.controlPoints[indexList[li-1]]
					pt2 = self.controlPoints[indexList[li]]
					spt1 = (pt1[0] * self.zoomScale, pt1[1] * self.zoomScale)
					spt2 = (pt2[0] * self.zoomScale, pt2[1] * self.zoomScale)
					self.scene.addLine(spt1[0], spt1[1], spt2[0], spt2[1], penWhite)

	def SetControlPoints(self, pts):
		if pts is None:
			self.controlPoints = []
		else:
			self.controlPoints = pts
		self.DrawFrame()

	def SetSelectedPoint(self, ptInd):
		self.selectedPointIndex = ptInd
		self.DrawFrame()

	def MousePressEvent(self, pos):

		self.prevPressPos = pos
		self.dragActive = False

		bestDist = None
		bestInd = None
		for ptNum, pt in enumerate(self.controlPoints):
			spt = (pt[0] * self.zoomScale, pt[1] * self.zoomScale)
			dist = ((spt[0] - pos[0]) ** 2. + (spt[1] - pos[1]) ** 2.) ** 0.5
			if bestDist is None or dist < bestDist:
				bestDist = dist
				bestInd = ptNum
		print (bestInd)
		self.SetSelectedPoint(bestInd)

	def MouseMoveEvent(self, pos):

		if self.prevPressPos is None: return

		dist = ((self.prevPressPos[0] - pos[0]) ** 2. + (self.prevPressPos[1] - pos[1]) ** 2.) ** 0.5
		if dist > self.dragThreshold:
			self.dragActive = True

		if self.dragActive:

			if self.selectedPointIndex is not None:

				spt = (pos[0] / self.zoomScale, pos[1] / self.zoomScale)
				self.controlPoints[self.selectedPointIndex] = spt
				self.DrawFrame()
				self.controlPointsChanged.emit(self.controlPoints)

	def MouseReleaseEvent(self, pos):
		#print ("Release", pos)

		self.prevPressPos = None
		self.dragActive = False

	def SetFrame(self, frame):
		self.currentFrame = frame
		self.DrawFrame()

	def SetLinks(self, linksIn):
		self.links = linksIn
		self.DrawFrame()

	def ZoomIn(self):
		self.zoomScale *= 1.5
		self.DrawFrame()

	def ZoomOut(self):
		self.zoomScale /= 1.5
		self.DrawFrame()

	def keyPressEvent(self, a):
		if a.key() == ord("["):
			self.prevFrame.emit()
		if a.key() == ord("]"):
			self.nextFrame.emit()
		if a.key() == ord("-"):
			self.ZoomOut()
		if a.key() in [ord("+"), ord("=")]:
			self.ZoomIn()

