import dataset_helen
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy import linalg
from scipy import optimize 

def Dist(pt1, pt2):
	return ((pt1[0]-pt2[0])**2.0 + (pt1[1]-pt2[1])**2.0) ** 0.5

def func(x, centred, hairCentred, Vh, s):
	#print (centred.shape, hairCentred.shape)
	x1 = x.reshape((14, 24))
	totalErr = []

	for i in range(centred.shape[0]):
		eigenVals = (np.dot(Vh, centred[i,:])[:len(s)] / s)
		#print "evals3", eigenVals
		pred = np.dot(x1, eigenVals)
		err = np.abs(hairCentred[i,:] - pred)
		totalErr.extend(err)

	totalErr = np.array(totalErr)
	return totalErr

if __name__=="__main__":

	dataset = dataset_helen.DatasetHelen()
	count = 0
	xpts = []
	ypts = []
	hairXpts, hairYpts = [], []
	filteredFrameNames = []

	#Centre the features
	for frameName in dataset.GetFrameNames():
		pts = dataset.GetAnnotations(frameName)

		pts2 = [pts[0], pts[20], pts[40], pts[41], pts[49], pts[57], pts[58], pts[72],
			pts[145], pts[153], pts[125], pts[133]]

		if Dist(pts[194], (10.0, 10.0)) > 1e-4:
			count += 1
			#print frameName, pts[194:200]
			xpts.append([pt[0] for pt in pts2])
			ypts.append([pt[1] for pt in pts2])

			hairXpts.append([pt[0] for pt in pts[194:]])
			hairYpts.append([pt[1] for pt in pts[194:]])

			filteredFrameNames.append(frameName)

			
	print "Hair frames marked", count

	xpts = np.array(xpts)
	ypts = np.array(ypts)

	hairXpts = np.array(hairXpts)
	hairYpts = np.array(hairYpts)

	xCentrePos = np.mean(xpts, axis=1)
	yCentrePos = np.mean(ypts, axis=1)

	xCentrePos2 = np.array([xCentrePos] * xpts.shape[1]).transpose()
	yCentrePos2 = np.array([yCentrePos] * ypts.shape[1]).transpose()

	xptsCentred = xpts - xCentrePos2
	yptsCentred = ypts - yCentrePos2

	hairxCentrePos2 = np.array([xCentrePos] * hairXpts.shape[1]).transpose()
	hairyCentrePos2 = np.array([yCentrePos] * hairYpts.shape[1]).transpose()

	hairXptsCentred = hairXpts - hairxCentrePos2
	hairYptsCentred = hairYpts - hairyCentrePos2

	#plt.plot(xptsCentred[0,:], yptsCentred[0,:])
	#plt.show()

	centred = np.hstack((xptsCentred, yptsCentred))
	hairCentred = np.hstack((hairXptsCentred, hairYptsCentred))

	#plt.plot(centred[0,:194], centred[0,194:])
	#plt.show()

	print centred.shape

	U, s, Vh = linalg.svd(centred)

	print U.shape, s.shape, Vh.shape


	if 1:
		sigma = np.zeros(centred.shape)
		for i in range(min(centred.shape)):
			sigma[i, i] = s[i]
		#a1 = np.dot(U, np.dot(sigma, Vh))
		#print np.allclose(centred, a1)

	faceIndex = 22
	centrePos = (xCentrePos[faceIndex], yCentrePos[faceIndex])
	print "centrePos", centrePos
	shp = np.dot(U[faceIndex,:], np.dot(sigma, Vh))
	print "evals1", U[faceIndex,:][:len(s)]

	if 0:
		plt.plot(shp[:194], shp[194:])
		plt.show()

	eigenVals = (np.dot(Vh, shp)[:len(s)] / s)
	print "evals2", eigenVals

	eigenVals = (np.dot(Vh, centred[faceIndex,:])[:len(s)] / s)
	print "evals3", eigenVals

	print centred.shape, hairCentred.shape, U.shape

	x0 = np.ones((24*14))
	x, ier = optimize.leastsq(func, x0, args=(centred, hairCentred, Vh, s))
	x1 = x.reshape((14, 24))

	eigenVals = (np.dot(Vh, centred[faceIndex,:])[:len(s)] / s)
	pred = np.dot(x1, eigenVals)

	print pred
	print hairCentred[faceIndex,:]

	if 1:
		img=mpimg.imread("/home/tim/Desktop/Helen/imgs/{}.jpg".format(dataset.nameToImgFina[filteredFrameNames[faceIndex]]))

		fig = plt.figure()
		ax = fig.add_subplot(111)
		ax.set_aspect('equal')
		ax.imshow(img)
		ax.plot(centred[faceIndex,:][:12]+centrePos[0], centred[faceIndex,:][12:]+centrePos[1], 'x')
		ax.plot(pred[:7]+centrePos[0], pred[7:]+centrePos[1])
		plt.show()


	#Estimated hair shape = hair model * face eigenvals
	#

	#hairModel = np.linalg.pinv(np.dot(U, hairCentred))
	
	#hairShp = np.dot(hairModel, U[faceIndex,:]).transpose()
	#print hairShp
	#print hairCentred[faceIndex,:]

