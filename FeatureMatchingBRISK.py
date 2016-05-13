#Update May 13, 2016
import numpy as np
import cv2
from matplotlib import pyplot as plt

def initialize_descriptor(img1):
	# Initialize BRISK detector
	brisk = cv2.BRISK_create(thresh=0,octaves=1,patternScale=1.0)
	# find the keypoints and descriptors with BRISK
	kp1, des1 = brisk.detectAndCompute(img1,None)
	# Initialize BFMatcher
	bf = cv2.BFMatcher(normType=cv2.NORM_HAMMING2)
	
	return (kp1,des1,brisk,bf)

def compare_images(kp1, des1, img2, brisk, bf):
	# find the keypoints and descriptors with BRISK
	kp2, des2 = brisk.detectAndCompute(img2,None)

	try:
		matches = bf.knnMatch(des1,des2, k=2)
		ratio = float((len(matches))) / max(len(des1),len(des2))
		if len(matches) > 0 and ratio > 0.4 and ratio < 1.0:
			return ratio
	except:
		print "Error"


def viewMatch(img1, img2):
	brisk = cv2.BRISK_create(thresh=0,octaves=0,patternScale=1.0)
	# find the keypoints and descriptors with BRISK
	kp1, des1 = brisk.detectAndCompute(img1,None)
	kp2, des2 = brisk.detectAndCompute(img2,None)	
	
	# initialize BFMatcher
	bf = cv2.BFMatcher(normType=cv2.NORM_HAMMING2)
	try:
		matches = bf.knnMatch(des1,des2, k=2)
		img3 = np.zeros((1000,1000,3), np.uint8)
		img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,matches,img3, flags=2)
		plt.imshow(img3),plt.show()
	except:
		print "Error"
		
