# Absolutely minimal example of PySide2 application with window

from PySide2 import QtGui, QtWidgets
import imgframe
import os
import sys

if __name__=="__main__":

	pth = "/media/tim/D21AEC821AEC64C7/datasets/medical/vid1/"
	if len(sys.argv) > 1:
		pth = sys.argv[1]

	# Get entrypoint through which we control underlying Qt framework
	app = QtWidgets.QApplication([])
	
	# Qt automatically creates top level application window if you
	# instruct it to show() any GUI element
	window = QtWidgets.QWidget()
	layout = QtWidgets.QVBoxLayout()
	window.setLayout(layout)

	frameView = imgframe.FrameView(pth)
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


