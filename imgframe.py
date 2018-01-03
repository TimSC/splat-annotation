from PySide2 import QtGui, QtWidgets, QtCore

class FrameList(QtWidgets.QComboBox):
	selectionChanged = QtCore.Signal()

	def __init__(self):
		QtWidgets.QComboBox.__init__(self)
		QtCore.QObject.connect(self, QtCore.SIGNAL('activated(int)'), self.FrameChanged)

	def SetFrameNames(self, frameNames):
		self.clear()
		for fn in frameNames[::-1]:
			self.addItem(fn)

	def CurrentText(self):
		return self.currentText()
		
	def FrameChanged(self, ind = None):
		self.selectionChanged.emit()

class MyQGraphicsScene(QtWidgets.QGraphicsScene):
	mousePress = QtCore.Signal(list)

	def __init__(self):
		QtWidgets.QGraphicsScene.__init__(self)

	def mousePressEvent(self, event):
		scenePos = event.scenePos()
		self.mousePress.emit([scenePos.x(), scenePos.y()])

class FrameView(QtWidgets.QWidget):
	pointSelected = QtCore.Signal(int)

	def __init__(self):
		QtWidgets.QWidget.__init__(self)

		self.selectedPointIndex = []
		self.clickedPoint = None
		self.currentFrame = None
		self.zoomScale = 1.0

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
		for ptNum, pt in enumerate(self.controlPoints):
			currentPen = penWhite
			if self.selectedPointIndex is not None and ptNum == self.selectedPointIndex:
				currentPen = penRed

			spt = (pt[0] * self.zoomScale, pt[1] * self.zoomScale)
			self.scene.addLine(spt[0]-5., spt[1], spt[0]+5., spt[1], currentPen)
			self.scene.addLine(spt[0], spt[1]-5., spt[0], spt[1]+5., currentPen)

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
		self.clickedPoint = pos
		self.DrawFrame()

		bestDist = None
		bestInd = None
		for ptNum, pt in enumerate(self.controlPoints):
			spt = (pt[0] * self.zoomScale, pt[1] * self.zoomScale)
			dist = ((spt[0] - pos[0]) ** 2. + (spt[1] - pos[1]) ** 2.) ** 0.5
			if bestDist is None or dist < bestDist:
				bestDist = dist
				bestInd = ptNum
		self.pointSelected.emit(bestInd)
		self.SetSelectedPoint(bestInd)

	def GetClickedPointPos(self):
		return self.clickedPoint

	def ClearClickedPoint(self):
		self.clickedPoint = None
		self.DrawFrame()

	def SetFrame(self, frame):
		self.currentFrame = frame
		self.DrawFrame()

	def ZoomIn(self):
		self.zoomScale *= 1.5
		self.DrawFrame()

	def ZoomOut(self):
		self.zoomScale /= 1.5
		self.DrawFrame()

