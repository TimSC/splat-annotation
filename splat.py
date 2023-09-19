# Absolutely minimal example of PySide2 application with window

from PySide2 import QtGui, QtWidgets
import imgframe
import os
import dataset_imageseq

currentIndex = None
frameList = []

def SelectionChanged():
	global frameView, frameList, currentIndex, dataset
	img = dataset.GetFrame(frameList[currentIndex])
	frameView.SetFrame(img)
	annotations = dataset.GetAnnotations(frameList[currentIndex])
	frameView.SetControlPoints(annotations)

def ControlPointsChanged(pts):
	dataset.SetAnnotation(frameList[currentIndex], pts)

def SaveAnnotation():
	dataset.SaveAnnotation()

def NextFrame():
	global frameView, frameList, currentIndex, dataset
	ind = currentIndex + 1
	if len(frameList) < 0:
		ind = len(frameList) - 1
	currentIndex = ind
	SelectionChanged()

def PrevFrame():
	global frameView, frameList, currentIndex, dataset
	ind = currentIndex - 1
	if ind < 0:
		ind = 0
	currentIndex = ind
	SelectionChanged()

if __name__=="__main__":

	# Get entrypoint through which we control underlying Qt framework
	app = QtWidgets.QApplication([])

	#dataset = dataset_helen.DatasetHelen()
	dataset = dataset_imageseq.Dataset()

	# Qt automatically creates top level application window if you
	# instruct it to show() any GUI element
	window = QtWidgets.QWidget()
	layout = QtWidgets.QVBoxLayout()
	window.setLayout(layout)

	toolbar = QtWidgets.QToolBar()
	layout.addWidget(toolbar, 0)
	actionSave = toolbar.addAction("Save")
	actionSave.triggered.connect(SaveAnnotation)

	frameList = dataset.GetFrameNames()
	currentIndex = 0

	frameView = imgframe.FrameView()
	frameView.controlPointsChanged.connect(ControlPointsChanged)
	frameView.nextFrame.connect(NextFrame)
	frameView.prevFrame.connect(PrevFrame)
	frameView.SetLinks(dataset.GetLinks())
	layout.addWidget(frameView)

	SelectionChanged()
	window.show()

	# IMPORTANT: `window` variable now contains a reference to a top
	# level window, and if you lose the variable, the window will be
	# destroyed by PySide automatically, e.g. this won't show:
	# 
	#   QLabel('New Window').show()
	#
	# This is true for other PySide2 objects, so be careful.

	# Start Qt/PySide2 application. If we don't show any windows, the
	# app would just loop at this point without the means to exit
	app.exec_()


