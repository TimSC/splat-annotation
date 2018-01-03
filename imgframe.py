from PySide2 import QtGui, QtWidgets, QtCore

class MyQGraphicsScene(QtWidgets.QGraphicsScene):
	mousePress = QtCore.Signal(list)

	def __init__(self):
		QtWidgets.QGraphicsScene.__init__(self)

	def mousePressEvent(self, event):
		scenePos = event.scenePos()
		self.mousePress.emit([scenePos.x(), scenePos.y()])

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

class FrameView(QtWidgets.QWidget):
	pointSelected = QtCore.Signal(int)

	def __init__(self):
		QtWidgets.QWidget.__init__(self)

		self.selectedPointIndex = []
		self.clickedPoint = None
		self.currentFrame = None

		self.layout = QtWidgets.QVBoxLayout()
		self.setLayout(self.layout)

		self.frameCombo = FrameList()
		self.layout.addWidget(self.frameCombo)

		self.scene = MyQGraphicsScene()
		self.scene.mousePress.connect(self.MousePressEvent)
		self.view = QtWidgets.QGraphicsView(self.scene)
		self.layout.addWidget(self.view, 1)
		self.controlPoints = []

	def DrawFrame(self):
		if self.currentFrame is None: return

		frame = self.currentFrame

		self.scene.clear()
		self.scene.setSceneRect(0, 0, frame.size().width(), frame.size().height())
		pix = QtGui.QPixmap(frame)

		gpm = QtWidgets.QGraphicsPixmapItem(pix)
		self.scene.addItem(gpm)

		penWhite = QtGui.QPen(QtCore.Qt.white, 1.0, QtCore.Qt.SolidLine)
		penRed = QtGui.QPen(QtCore.Qt.red, 1.0, QtCore.Qt.SolidLine)
		for ptNum, pt in enumerate(self.controlPoints):
			currentPen = penWhite
			if self.selectedPointIndex is not None and ptNum == self.selectedPointIndex:
				currentPen = penRed

			self.scene.addLine(pt[0]-5., pt[1], pt[0]+5., pt[1], currentPen)
			self.scene.addLine(pt[0], pt[1]-5., pt[0], pt[1]+5., currentPen)

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
			dist = ((pt[0] - pos[0]) ** 2. + (pt[1] - pos[1]) ** 2.) ** 0.5
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

