import dataset_helen
import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg

def Dist(pt1, pt2):
	return ((pt1[0]-pt2[0])**2.0 + (pt1[1]-pt2[1])**2.0) ** 0.5

if __name__=="__main__":

	dataset = dataset_helen.DatasetHelen()
	count = 0
	xpts = []
	ypts = []
	hairXpts, hairYpts = [], []

	#Centre the features
	for frameName in dataset.GetFrameNames():
		pts = dataset.GetAnnotations(frameName)

		if Dist(pts[194], (10.0, 10.0)) > 1e-4:
			count += 1
			#print frameName, pts[194:200]
			xpts.append([pt[0] for pt in pts[:194]])
			ypts.append([pt[1] for pt in pts[:194]])

			hairXpts.append([pt[0] for pt in pts[194:]])
			hairYpts.append([pt[1] for pt in pts[194:]])

			
	print "Hair frames marked", count

	xpts = np.array(xpts)
	ypts = np.array(ypts)

	hairXpts = np.array(hairXpts)
	hairYpts = np.array(hairYpts)

	xCentrePos = np.array([np.mean(xpts, axis=1)] * xpts.shape[1]).transpose()
	yCentrePos = np.array([np.mean(ypts, axis=1)] * ypts.shape[1]).transpose()

	xptsCentred = xpts - xCentrePos
	yptsCentred = ypts - yCentrePos

	hairxCentrePos = np.array([np.mean(xpts, axis=1)] * hairXpts.shape[1]).transpose()
	hairyCentrePos = np.array([np.mean(ypts, axis=1)] * hairYpts.shape[1]).transpose()

	hairXptsCentred = hairXpts - hairxCentrePos
	hairYptsCentred = hairYpts - hairyCentrePos

	#plt.plot(xptsCentred[0,:], yptsCentred[0,:])
	#plt.show()

	centred = np.hstack((xptsCentred, yptsCentred))
	hairCentred = np.hstack((hairXptsCentred, hairYptsCentred))

	#plt.plot(centred[0,:194], centred[0,194:])
	#plt.show()

	U, s, Vh = linalg.svd(centred)

	print U.shape, s.shape, Vh.shape


	if 1:
		sigma = np.zeros(centred.shape)
		for i in range(min(centred.shape)):
			sigma[i, i] = s[i]
		#a1 = np.dot(U, np.dot(sigma, Vh))
		#print np.allclose(centred, a1)

	shp = np.dot(U[15,:], np.dot(sigma, Vh))
	print U[15,:][:20]

	if 0:
		plt.plot(shp[:194], shp[194:])
		plt.show()

	eigenVals = (np.dot(Vh, shp)[:332] / s)[:20]

	if 1:
		plt.plot(centred[15,:][:194], centred[15,:][194:])
		plt.plot(hairCentred[15,:][:7], hairCentred[15,:][7:])
		plt.show()

