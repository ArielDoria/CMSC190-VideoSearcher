#Updayed May 13, 2016
import Tkinter
import tkFileDialog
import os
import numpy as np
import cv2
import shutil
import time
from threading import Thread

def compute_time(frame,framespersecond): #Computes the time equivalent of a frame number
    currentTimeInSeconds = int(frame/framespersecond)
    extraframe = int(frame%framespersecond)
    hour = int(float(currentTimeInSeconds)/3600)
    currentTimeInSeconds = currentTimeInSeconds % 3600
    minute = int(float(currentTimeInSeconds)/60)
    seconds = int(float(currentTimeInSeconds)%60)
    return "%02d-%02d-%02d-%02d" % (hour, minute, seconds,extraframe)

def compute_histogram(src, h_bins = 30, s_bins = 32): #Computes the histogram diffirence of two images
    #create images
    height, width, channels = src.shape
    hsv = np.zeros((height,width,3), np.uint8)
    cv2.cvtColor(src, cv2.COLOR_BGR2HSV, hsv)

    #compute histogram 
    hist = cv2.calcHist([hsv], [0], None, [30], [0, 180])
    cv2.normalize(hist,hist)    #normalize hist
    return hist

def summarize(path, start, frameCount, framespersecond, newFolder): #Collect 'significant' frames and removes repetition of frames
	cap = cv2.VideoCapture(path)
	cap.set(cv2.CAP_PROP_POS_FRAMES, start)
	frame_counter = start
	
	#get the first frame as the comparing picture
	ret,picture1= cap.read()
	cv2.imwrite(newFolder+"/"+str(compute_time(frame_counter, framespersecond))+".png", picture1)
	hist1 = compute_histogram(picture1)
	threshold = min(0.5,(0.25 + 0.05*(frameCount//1500))) #threshold ranges from 0.25 to 0.5, depending on video length

	for i in range(int(frameCount)):
		ret,picture2 = cap.read()
		frame_counter=frame_counter+1
		
		if picture2 is None:
			break

		#Compare the histogram of the new frame	
		hist2= compute_histogram(picture2)
		sc= cv2.compareHist(hist1, hist2, method=3) # 3 is for CV_COMP_BHATTACHARYYA

		#set a threshold for the comparison of the histogram
		if sc > threshold:
			#Save the images
			cv2.imwrite(newFolder+"/"+compute_time(frame_counter, framespersecond)+".png", picture2)

			#update the basis of comparison
			picture1 = picture2
			hist1 = compute_histogram(picture1)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	print "Summarization partly done."


def showvideo(path, pb=None, per_step=0, THREAD_COUNT=2): #Creates images in VideoSummarization folder
	frame_counter=0
	cap = cv2.VideoCapture(path)
	framespersecond = cap.get(cv2.CAP_PROP_FPS)
	#creating folders using the title of the video
	directory = os.path.dirname(os.path.realpath(__file__))
	filename = os.path.basename(path)
	newFolder = directory +'/VideoSummarization/'+filename.replace(".","_")
	if not os.path.exists(newFolder):
		os.makedirs(newFolder)
	totalFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
	framesPerThread = totalFrames // THREAD_COUNT
	cap.release()
	
	threads = []

	for i in range(0, THREAD_COUNT):
		threads.append(Thread(target=summarize, args=(path, framesPerThread*i, framesPerThread, framespersecond, newFolder)))
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
		pb.step(per_step/THREAD_COUNT)

	cv2.destroyAllWindows()
	return newFolder

def chooseDirectory(): #Shows a window for selecting video directory
	root = Tkinter.Tk()
	root.withdraw() #use to hide tkinter window

	currdir = os.getcwd()
	tempdir = tkFileDialog.askdirectory(parent=root, initialdir=currdir, title='Please select a directory')
	
	if len(tempdir) > 0:
		return tempdir
	else:
		return 1
	
def analyzeDirectory(tempdir,pb, label): #Analyzes the videos in a given directory
	movie_extensions=['avi', 'dat', 'mp4', 'mkv', 'vob']	
	if len(tempdir) > 0:
		print "You chose %s" % tempdir
		path = os.path.dirname(os.path.realpath(__file__))
		path = path+'/VideoSummarization'
		
		if not os.path.exists(path):
			os.makedirs(path)
		else:
			shutil.rmtree(path)
			
		# Get the absolute path of the movie_directory parameter
		movie_directory = os.path.abspath(tempdir)

		# Get a list of files in movie_directory
		movie_directory_files = os.listdir(movie_directory)
		filtered_files = []
		for file in movie_directory_files:
			filepath = os.path.join(movie_directory, file)
			if(os.path.isfile(filepath) and filepath.endswith(tuple(movie_extensions))):
				filtered_files.append(file)

		per_step = (1 / float(len(filtered_files))) * 99
		pb.stop()
		
		start_time = time.time();
		# Traverse through all files
		for filename in filtered_files:
			filepath = os.path.join(movie_directory, filename)
			label.config(text="Summarizing video - "+filename[:30]+"...")
			showvideo(filepath, pb, per_step)
		
		end_time = time.time();
		label.config(text="Done reading videos. (Time elapsed: %s sec)" % (end_time-start_time))
		print "Time Elapsed(Summarization): %s seconds." % (end_time-start_time)