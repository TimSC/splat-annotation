# Absolutely minimal example of PySide2 application with window

from PySide2 import QtGui, QtWidgets
import imgframe
import os

if __name__=="__main__":

	# Get entrypoint through which we control underlying Qt framework
	app = QtWidgets.QApplication([])

	#dataset = dataset_helen.DatasetHelen()
	

	# Qt automatically creates top level application window if you
	# instruct it to show() any GUI element
	window = QtWidgets.QWidget()
	layout = QtWidgets.QVBoxLayout()
	window.setLayout(layout)

	#toolbar = QtWidgets.QToolBar()
	#layout.addWidget(toolbar, 0)
	#actionSave = toolbar.addAction("Save")
	#actionSave.triggered.connect(SaveAnnotation)

	frameView = imgframe.FrameView()
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


