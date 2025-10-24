# Absolutely minimal example of PySide2 application with window

from PySide2 import QtGui, QtWidgets
import imgframe
import os
import sys
import tempfile
import subprocess

class AppCore:
	def __init__(self, pth):

		self.basePath = pth

		self.layout = QtWidgets.QHBoxLayout()
		
		self.videoList = []
		for (root,dirs,files) in os.walk(self.basePath): 
			for fi in files:
				print (root, fi)
				self.videoList.append((root, fi))

		self.videoList.sort(key=lambda k: k[1])

		self.listWidget = QtWidgets.QListWidget()
		self.listWidget.addItems([v[1] for v in self.videoList])
		self.listWidget.setFixedWidth(165)
		self.layout.addWidget(self.listWidget)

		self.frameView = imgframe.FrameView()
		self.layout.addWidget(self.frameView)

		self.listWidget.currentItemChanged.connect(self.index_changed)

	def index_changed(self, i): # Not an index, i is a QListWidgetItem
		r = self.listWidget.row(i)
		pth, vid = self.videoList[r]

		self.frameView.SetPath(os.path.join(pth, vid))

if __name__=="__main__":

	pth = "frames/"
	if len(sys.argv) > 1:
		pth = sys.argv[1]

	# Get entrypoint through which we control underlying Qt framework
	app = QtWidgets.QApplication([])
	
	# Qt automatically creates top level application window if you
	# instruct it to show() any GUI element
	window = QtWidgets.QWidget()

	appCore = AppCore(pth)
	window.setLayout(appCore.layout)

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


