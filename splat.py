# Absolutely minimal example of PySide2 application with window

from PySide2 import QtGui, QtWidgets
import imgframe
import os
import sys
import tempfile
import subprocess

class AppCore:
	def __init__(self, pth):

		self.basePath = pth #'../projectvigil/projectvigil/Vigil'

		self.layout = QtWidgets.QHBoxLayout()
		
		self.videoList = []
		for (root,dirs,files) in os.walk(self.basePath): 
			for fi in files:
				#print (root, fi)
				self.videoList.append((root, fi))

		self.videoList.sort(key=lambda k: k[1])

		self.listWidget = QtWidgets.QListWidget()
		self.listWidget.addItems([v[1] for v in self.videoList])
		self.layout.addWidget(self.listWidget)

		self.frameView = imgframe.FrameView(None)
		self.layout.addWidget(self.frameView)

		self.listWidget.currentItemChanged.connect(self.index_changed)

	def index_changed(self, i): # Not an index, i is a QListWidgetItem
		r = self.listWidget.row(i)
		pth, vid = self.videoList[r]

		self.tmpDir = tempfile.TemporaryDirectory()
		
		print (pth, vid)

		vid_path = os.path.join(pth, vid)
		print (vid_path)

		if os.path.exists(vid_path):
			cmd = ['ffmpeg', '-i', (vid_path), (os.path.join(self.tmpDir.name, 'vid%05d.jpg'))]
		print (cmd)
		subprocess.run(cmd)

		self.frameView.SetPath(self.tmpDir.name)

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


