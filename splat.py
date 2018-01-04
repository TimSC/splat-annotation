# Absolutely minimal example of PySide2 application with window

from PySide2 import QtGui, QtWidgets
import imgframe
import os
import dataset_helen

def SelectionChanged():
	global frameView, frameList, dataset
	img = dataset.GetFrame(frameList.currentText())
	frameView.SetFrame(img)
	annotations = dataset.GetAnnotations(frameList.currentText())
	frameView.SetControlPoints(annotations)

def ControlPointsChanged(pts):
	dataset.SetAnnotations(frameList.currentText(), pts)

def SaveAnnotation():
	dataset.SaveAnnotation("emma.tar.gz")

def NextFrame():
	global frameView, frameList, dataset
	ind = frameList.currentIndex() + 1
	if frameList.count() < 0:
		ind = frameList.count() - 1
	frameList.setCurrentIndex(ind)
	SelectionChanged()

def PrevFrame():
	global frameView, frameList, dataset
	ind = frameList.currentIndex() - 1
	if ind < 0:
		ind = 0
	frameList.setCurrentIndex(ind)
	SelectionChanged()

if __name__=="__main__":

	# Get entrypoint through which we control underlying Qt framework
	app = QtWidgets.QApplication([])

	dataset = dataset_helen.DatasetHelen()

	# Qt automatically creates top level application window if you
	# instruct it to show() any GUI element
	window = QtWidgets.QWidget()
	layout = QtWidgets.QVBoxLayout()
	window.setLayout(layout)

	toolbar = QtWidgets.QToolBar()
	layout.addWidget(toolbar, 0)
	actionSave = toolbar.addAction("Save")
	actionSave.triggered.connect(SaveAnnotation)

	frameList = imgframe.FrameList()
	frameList.selectionChanged.connect(SelectionChanged)
	frameList.SetFrameNames(dataset.GetFrameNames())
	layout.addWidget(frameList)

	frameView = imgframe.FrameView()
	frameView.controlPointsChanged.connect(ControlPointsChanged)
	frameView.nextFrame.connect(NextFrame)
	frameView.prevFrame.connect(PrevFrame)
	frameView.SetLinks(dataset.GetLinks())
	layout.addWidget(frameView)

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


