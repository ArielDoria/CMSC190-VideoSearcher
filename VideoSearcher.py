#Update May 13, 2016
#!/usr/bin/python
#install imutils
#pip install imutils
from VideoSum1 import *
from FeatureMatchingBRISK import *
from Tkinter import *
from PIL import *
from threading import Thread
import Tkinter as tk
import tkMessageBox
import Image, ImageDraw
import os
import numpy as np
import cv2
import glob
import imutils
import ttk
import time

#Creating the Graphical User Interface
class GUIGenerator:
    def __init__(self,parent,toolsArea,result,pb,statusLabel,posx,posy,*kwargs):
        self.pen="TRUE"
        self.parent = parent
        self.posx = posx
        self.posy = posy
        self.result = result
        self.sizex = 660
        self.sizey = 600
        self.b1 = "up"
        self.xold = None
        self.yold = None
        self.tool = "brush"
        self.pb = pb
        self.statusLabel = statusLabel
        self.drawing_area=tk.Canvas(self.parent,width=self.sizex,height=self.sizey,bg="white")
        self.drawing_area.place(x=self.posx,y=self.posy)
        self.drawing_area.bind("<Motion>", self.motion)
        self.drawing_area.bind("<ButtonPress-1>", self.b1down)
        self.drawing_area.bind("<ButtonRelease-1>", self.b1up)
        currdirectory = os.getcwd()
        button1=tk.Button(toolsArea,text="PEN",width=30,height=30,bg='white',command=self.write)
        button1.pack(side="left")
        button1.image=PhotoImage(file=currdirectory+"/images/pen2.png").subsample(2,2)
      	button1.config(image=button1.image)
      	
      	button6=tk.Button(toolsArea,text="LINE",width=30,height=30,bg='white', command=self.setLine)
        button6.pack(side="left")
        button6.image=PhotoImage(file=currdirectory+"/images/line2.png").subsample(2,2)
      	button6.config(image=button6.image)
        
        button4=tk.Button(toolsArea,text="SQUARE",width=30,height=30,bg='white',command=self.setRectangle)
        button4.pack(side="left")
        button4.image=PhotoImage(file=currdirectory+"/images/rectangle2.png").subsample(2,2)
      	button4.config(image=button4.image)
      	
        button5=tk.Button(toolsArea,text="CIRCLE",width=30,height=30,bg='white', command=self.setEllipse)
        button5.pack(side="left")
        button5.image=PhotoImage(file=currdirectory+"/images/circle2.png").subsample(2,2)
      	button5.config(image=button5.image)
      	
      	button2=tk.Button(toolsArea,text="ERASER",width=30,height=30,bg='white',command=self.clear)
        button2.pack(side="left")
        button2.image=PhotoImage(file=currdirectory+"/images/eraser2.png").subsample(2,2)
      	button2.config(image=button2.image)
      	
        button3=tk.Button(toolsArea,text="CLEAR ALL",width=30,height=30,bg='white',command=self.clearAll)
        button3.pack(side="left")
        button3.image=PhotoImage(file=currdirectory+"/images/refresh2.png").subsample(2,2)
      	button3.config(image=button3.image)
      	
        button=tk.Button(toolsArea,text="SEARCH",width=30,height=30,bg='white',command=self.save)
        button.pack(side="left")
        button.image=PhotoImage(file=currdirectory+"/images/search2.png").subsample(2,2)
      	button.config(image=button.image)
        self.image=Image.new("RGB",(670,605),(255,255,255))
        self.draw=ImageDraw.Draw(self.image)

    def save(self):
		self.result.delete("all")
		self.result.update_idletasks()
		filename = "temp.png"
		self.image.save(filename)
		i=1
		height=100;	
		searchResult = []

		img1=cv2.imread(filename,0) #Reading the base image 
		kp1,des1,brisk,bf=initialize_descriptor(img1)

		#Getting the current working directory of the program
		currdir = os.getcwd()
		directory=currdir+"/VideoSummarization"
		directory=os.path.abspath(directory)
		listOfFolder = os.listdir(directory)
		per_folder_step = 1/float(len(listOfFolder)) * 99
		self.pb.stop()
		
		start_time = time.time();
		#Analyze each folder and the pictures inside it.
		for folder in listOfFolder:
			folderPath = os.path.join(directory, folder)
			picture_files = os.listdir(folderPath)
			per_picture_step = per_folder_step/float(len(picture_files))
			self.statusLabel.config(text="Looking at "+str(folder)+"...")
			
			#sort files according to its time of appearance
			sorted_files = sorted(picture_files, key=lambda x: int(x.replace("-","").split('.')[0]))
			for fileName in sorted_files:
				filepath = os.path.join(folderPath, fileName)
				# Check if it's a normal file or directory
				# if os.path.isfile(filepath):
					# if filepath.endswith(".png"):
						# print('{0}'.format(filepath))
				img2 = cv2.imread(filepath,1)
				dst = cv2.Canny(img2, 50, 200, 3);
				cdst = cv2.cvtColor(dst,cv2.COLOR_GRAY2BGR);
				img2 = (255-cdst)
				result = compare_images(kp1,des1,img2,brisk,bf)
				if result is not None:
					name = os.path.basename(filepath)
					name = name.split(".")
					searchResult.append(result)
					videoName = os.path.basename(folder)
					temp = tk.Canvas(self.result, bg="white", height=200, width=300,)
					temp.img4 = PhotoImage(file=filepath)
					temp.img4 = temp.img4.subsample(3,3)
					temp.create_image(150,80,anchor=CENTER,image=temp.img4)
					temp.create_text(150,10,fill="darkblue",font="Times 10",text="Ratio of good matches: " + str(result))
					temp.create_text(150,160,fill="darkblue",font="Times 10",text="Video: " + videoName.replace("_","."))
					temp.create_text(150,180,fill="darkblue",font="Times 10",text="Time: " + name[0].replace("-",":"))
					temp.grid(row=i, column=1, sticky='news')

					#shows the feature matching of clicked result:
					def view_match(img1, img2):
						return lambda ev:viewMatch(img1, img2)
					temp.bind('<Button-1>',view_match(img1,img2))

					i=i+1
					self.result.create_window((150,height),window=temp) #update the canvass of the result
					self.result.config(scrollregion=self.result.bbox(ALL))
					height=height+200
					self.result.update_idletasks()
					#cv2.destroyAllWindows()
				self.pb.step(per_picture_step)
		print "Results: " + str(len(searchResult))
		print searchResult
		self.result.update_idletasks()
		cv2.destroyAllWindows()
		
		if(len(searchResult)==0):
			temp = tk.Canvas(self.result, bg="white", height=200, width=300,)
			temp.create_text(100,50,fill="darkblue",font="Times 12",text="No Results Found!")
			self.result.create_window((150,0),window=temp) #update the canvass of the result
			self.result.config(scrollregion=self.result.bbox(ALL))
		
		end_time = time.time();
		self.statusLabel.config(text="Done searching. (Time elapsed: %s sec)" % (end_time-start_time))
		print "Time Elapsed(Searching): %s seconds." % (end_time-start_time)
		

    def clear(self):
        self.tool="eraser"
    
    def clearAll(self):
        self.drawing_area.delete("all")
        self.image=Image.new("RGB",(670,605),(255,255,255))
        self.draw=ImageDraw.Draw(self.image)
        
    def write(self):
        self.tool = "brush"
        self.xold = None
        self.yold = None

    def setRectangle(self):
        self.tool = "rect"
        self.xold = None
        self.yold = None

    def setEllipse(self):
        self.tool = "ellip"
        self.xold = None
        self.yold = None

    def setLine(self):
    	self.tool = "line"
        self.xold = None
        self.yold = None
        
    def b1down(self,event):
        self.b1 = "down"
        if self.tool == "rect" or self.tool == "ellip" or self.tool == "line" :
            self.xold = event.x
            self.yold = event.y

    def b1up(self,event):
        self.b1 = "up"
        if self.tool == "rect":
            event.widget.create_rectangle(self.xold,self.yold,event.x,event.y,fill=None)
            self.draw.rectangle(((self.xold,self.yold),(event.x,event.y)),fill=None,outline='black')
        elif self.tool == "ellip":
            event.widget.create_oval(self.xold,self.yold,event.x,event.y,fill=None)
            self.draw.ellipse(((self.xold,self.yold),(event.x,event.y)),fill=None,outline='black')
        elif self.tool == "line":
            event.widget.create_line(self.xold,self.yold,event.x,event.y,fill=None)
            self.draw.line(((self.xold,self.yold),(event.x,event.y)),(0,00,255),width=1)
        self.xold = None
        self.yold = None

    def motion(self,event):
        if self.b1 == "down":
            if self.tool == "brush" and self.xold is not None and self.yold is not None:
                event.widget.create_line(self.xold,self.yold,event.x,event.y,smooth='true',width=1,fill='black')
                self.draw.line(((self.xold,self.yold),(event.x,event.y)),(0,0,0),width=1)
            if self.tool == "eraser" and self.xold is not None and self.yold is not None:
                event.widget.create_line(self.xold,self.yold,event.x,event.y,smooth='true',width=5,fill='white')
                self.draw.line(((self.xold,self.yold),(event.x,event.y)),(255,255,255),width=5)
        
        if self.tool == "brush" or self.tool == "eraser":
            self.xold = event.x
            self.yold = event.y
        elif self.tool == "rect" or self.tool == "ellip" or self.tool == "line":
            event.widget.delete("rect")
            event.widget.delete("ellip")
            event.widget.delete("line")
            if self.xold is not None and self.yold is not None:
                if self.tool == "rect":
	                event.widget.create_rectangle(self.xold,self.yold,event.x,event.y,tags="rect")
                elif self.tool == "ellip":
	                event.widget.create_oval(self.xold,self.yold,event.x,event.y,tags="ellip")
	        elif self.tool == "line":
	                event.widget.create_line(self.xold,self.yold,event.x,event.y,tags="line")

if __name__ == "__main__":
	
	tempdir = None
	while not tempdir: #waiting for the user to choose the directory to be analyze
		tempdir=chooseDirectory()
	if tempdir != 1:
		#Creating the root
		root = tk.Toplevel()
		root.title("Video searcher")
		root.config(bg='white')
		frame = tk.Frame(root, height=700, width=1000, bg="white", colormap="new")
		frame.config(bg='white')
		
		#Drawing & Result panel
		drawResult = tk.Frame(frame, bg="white", height=670, width=1000)

		#draw box
		draw = tk.Canvas(drawResult, bg="white", height=670, width=690,bd=0, highlightthickness=0, relief='ridge')
		drawingTools = tk.Canvas(draw, bg="white", height=50, width=680,bd=0, highlightthickness=0, relief='ridge')
		drawingPad = tk.Canvas(draw, bg="sky blue", height=620, width=680,bd=0, highlightthickness=0, relief='ridge')
		resultbox = tk.Canvas(drawResult, bg="white", height=640, width=300,)
	
		#Making a scrollable result Box
		vscrollbar = Scrollbar(resultbox)
		vscrollbar.grid(row=1, column=1, sticky=N+S)

		result = Canvas(resultbox,
				yscrollcommand=vscrollbar.set,
				 height=640, width=280,bg="white",bd=0, highlightthickness=0, relief='ridge')
		result.grid(row=1, column=0, sticky=N+S+E+W)

		vscrollbar.config(command=result.yview)
	
		# make the canvas expandable
		resultbox.grid_rowconfigure(0, weight=1)
		resultbox.grid_columnconfigure(0, weight=1)
		label = tk.Canvas(resultbox, bg="white", height=30, width=300,bd=0, highlightthickness=0, relief='ridge')
		label.create_text(150,15,fill="darkblue",font="Times 14",
				        text="Search Result")
		label.grid(row=0, column=0, sticky=N)

		statusBar = tk.Canvas(root, bg="sky blue", height=100)
		#Progress bar
		statusLabel = Label(statusBar, text="Program started.", font="Times 12", justify=LEFT, width=92)
		pb = ttk.Progressbar(statusBar, orient="horizontal", length=250, mode="determinate")

		#Pack the canvas and labels use in the GUI
		drawResult.pack(fill=BOTH)
		draw.pack(side="left")
		resultbox.pack(side="left")
		drawingTools.pack()
		drawingPad.pack()
		frame.pack()
		statusBar.pack(side="left", fill=BOTH, expand=True)
		statusLabel.pack(side="left", expand=True)
		pb.pack(side="right", expand=True)
		path = str(''.join(tempdir))

		#Simultaneously run the GUI Generator and Video Summarization
		Thread(target = analyzeDirectory, args=(path,pb,statusLabel)).start()
		Thread(target = GUIGenerator, args=(drawingPad,drawingTools,result,pb,statusLabel,10,10)).start()
		def on_closing():
			path = os.path.dirname(os.path.realpath(__file__))
			path = path+'/VideoSummarization'
		
			if os.path.exists(path):
				shutil.rmtree(path)
			root.destroy()
			raise SystemExit()
		root.protocol("WM_DELETE_WINDOW", on_closing)
		root.mainloop()
