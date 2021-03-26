import os
import threading
import serial
import dataParser
import Vehicle
import profileEditor

from tkinter import *
from tkinter import messagebox
from datetime import date
import time

import serial.tools.list_ports as port_list
import matplotlib.ticker as ticker
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk) 
import numpy as np

# Get Initial Ports List #
ports = list(port_list.comports())
ports.append("PORT")

class App():
    def __init__(self, parent):
        # Tk Variables #
        self.parent = parent
        self.options = list(port_list.comports())
        self.variable = StringVar(self.parent)
        self.variable.set(ports[0])

        # FLags #
        self.dataStreamState = False
        self.updateConsoleFlag = True
        self.logFlag = False
        self.profileFlag = True

        # Global Class Variables #
        self.baudrate = 38400
        self.hdopMin = 300
        self.hdop = 9999
        self.speed = 0
        self.serialString = ""
        self.fileName = ""
        self.p_max = 0

        self.profile = []

        # Vehicle Instance For Calculations #
        self.car = Vehicle.Vehicle("VW", "Golf Mk IV 1.6SR", 1150, 3, [], 1, 0.34, 1.905, 1.18)

        # Plot Data #
        self.xarr = []
        self.yarr = []

        # Current Run Timer Variables #
        self.timerState = False
        self.startTime = 0
        self.endTime = 0
        self.timeCurrentRun = 0

        # Serial Port Object #
        self.serialPort = serial.Serial(port=self.options[0].device, baudrate=self.baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)        

        # Create TKinter Objects #
        self.portDropdownMenu() # Port Dropdown Menu 
        self.refreshPortsButton() # Refresh Ports List Button
        self.startDataLoggingButton() # Start Data Logging Button
        self.toggleRealTimeData() # Start/Stop Real Time Data Parsing Button
        self.editCarProfile()
        self.serialDataLabel() # Serial Data Label
        self.fixStatusLabel() # Fix Status Label
        self.initPlot() # Create Plot
        
        # Start Serial Data Reading #
        self.startReadDataThread() 

    # ------ TK Objects ------ #

    # Create Plot #
    def initPlot(self):
        self.plot(self.xarr, self.yarr, "Draguino Uno Virtual Dyno")

    # Fix Status Label #
    def fixStatusLabel(self):
        self.fixText = StringVar()
        self.fixText.set("No Fix")
        self.fixLabel = Label(self.parent, textvariable=self.fixText, relief=FLAT, font=("Arial", 12))
        self.fixLabel.pack(side=TOP)

    # Serial Data Label #
    def serialDataLabel(self):
        self.consoleText = StringVar()
        self.consoleText.set("")
        self.consoleLabel = Label(self.parent, textvariable=self.consoleText, relief=FLAT, font=("Arial", 12))
        self.consoleLabel.pack(side=TOP)

    def editCarProfile(self):
        self.editCarProfileButton = Button(self.parent, text="Open Profile Editor", command=self.openProfileEditor)
        self.editCarProfileButton.pack(side=TOP)

    # Start/Stop Real Time Data Parsing Button #
    def toggleRealTimeData(self):
        self.dataStartStopText = StringVar()
        self.dataStartStopText.set("Pause Data Stream")
        self.dataStartStop = Button(self.parent, textvariable = self.dataStartStopText, command=self.dataStartStop_)
        self.dataStartStop.pack(side=TOP)

    # Start Data Logging Button #
    def startDataLoggingButton(self):
        self.logText = StringVar()
        self.logText.set("Start Data Log")
        self.startLogging = Button(self.parent, textvariable = self.logText, command=self.dataLog)
        self.startLogging.pack(side=TOP)

    # Refresh Ports List Button #
    def refreshPortsButton(self):
        self.refreshButton = Button(self.parent, text = "Refresh Ports", command=self.refreshPorts)
        self.refreshButton.pack(side=TOP)

    # Port Dropdown Menu #
    def portDropdownMenu(self):
        self.opt = OptionMenu(self.parent, self.variable, self.options)
        self.opt.pack(side=TOP)

    # ------ Main Logic Functions ------ #

    # Update Serial Ports Dropdown Menu #
    def refreshPorts(self):
        self.options = list(port_list.comports()) # Retrieve all COM ports
        # Update Dropdown Menu #
        menu = self.opt["menu"]
        menu.delete(0, "end")
        for string in self.options:
            menu.add_command(label=string, command=lambda value=string: self.variable.set(value))

    # Create Filename For Logs & Plots #
    def createFileName(self):
        self.fileName = f'{self.car.manufac} {self.car.model} {self.date} {self.time}' # Create filename
        # Reformat Filename #
        self.fileName = self.fileName.replace("/", ".")
        self.fileName = self.fileName.replace(":", "-")

    #Start/Stop Data Log Button Handler #
    def dataLog(self):
        if (self.profileFlag):
            messagebox.showinfo("Error", "Profile Not Set")
        else:
            self.timer() # Begin curent run timer
            self.logFlag = not self.logFlag # Invert logging state flag
            if (self.logFlag): # Start of log
                self.createFileName() # Create new filename based on date and time
                self.logText.set("Stop Data Log") # Change data log button to stop
            else:
                xy = self.handleParser() # Retrieve plot data lists from data parser object
                self.logText.set("Start Data Log") # End of log
                name = f'Draguino Uno Virtual Dyno\n {self.car.manufac} {self.car.model}\n Total time: {str(self.timeCurrentRun)}s\n Max Power: {round(self.p_max, 5)}kW' # Create plot title  
                self.updatePlot(xy[0], xy[1], name) # Update plot with new data

    # Open Profile Editor Window #
    def openProfileEditor(self):
        self.profileFlag = False
        editor = profileEditor.profileEditor(self.parent)
        self.getProfile()
        values = self.profile
        self.car = Vehicle.Vehicle(values[0], values[1], int(values[2]), int(values[3]), values[4], float(values[5]), float(values[6]), float(values[7]), float(values[8]))

    # Start/Pause Serial Data Button Handler #
    def dataStartStop_(self):
        if (self.dataStreamState): # Running
            self.dataStartStopText.set("Pause Data Stream")
        else: # Paused
            self.dataStartStopText.set("Start Data Stream")
        self.dataStreamState = not self.dataStreamState # Invert data strean flag 
        self.updateConsoleFlag = not self.updateConsoleFlag # Invert update console flag

    # Extract Data From Serial String Input #
    def extractData(self):
        parameters = self.serialString.split(",") # Split serial string by ',' delimiter
        # Extract all variables from serial string #
        self.time = parameters[0]
        self.latitude = parameters[1]
        self.longitude = parameters[2]
        self.altitude = parameters[3]
        self.hdop = parameters[4]
        self.speed = parameters[5]

    # Write Data To File #
    def writeToFile(self):
        if (self.logFlag): # Log flag is True
            with open("./logs/%s.csv" % self.fileName, "a") as f: # Open file with already created filename
                myList = [self.date, self.serialString] # Create list of items to be written on a single line and append current date
                lst = map(str, myList) # Cast all list objects to string type
                line = ",".join(lst) # Create a string for each line with ',' delimiter
                f.write(line + "\n") # Write line to file

    # GPS Fix Status Label Handler #
    def setFixStatus(self):
        if (float(self.hdop) <= self.hdopMin): # Check if current hdop value is less than the predefined minimum for "OK Fix"
            self.fixText.set("Ok")
        else:
            self.fixText.set("No Fix")

    # Read Serial Data From Serial Port #
    def readData(self):
        self.serialPort.write(bytes.fromhex("A555FA"))
        while True:
            try: # Will throw an exception if program is ran while receiving serial string
                self.serialString = self.serialPort.readline().decode("UTF-8").replace('\n', '').rstrip() # Decode to UTF-8 and remove whitespaces and new lines
                self.updateConsole(self.serialString) # Update console label
                self.extractData() # Extract all data from serial string into variables
                self.writeToFile() # Write reformatted serial string as a new line
                self.setFixStatus() # Update Fix Status Label
            except:
                print("Invalid GPS Data")
        self.serialPort.close() # Close Serial Port

    # Start Read Data Daemon Thread #
    def startReadDataThread(self):
        self.threadingTask = threading.Thread(target=self.readData, name="Read Data Thread", daemon=True) # Create new task with readData function
        self.threadingTask.start() # Start new thread

    # Serial Data Label Handler #
    def updateConsole(self, text):
        if (self.updateConsoleFlag): # Update console flag is True
            self.date = date.today().strftime("%d/%m/%Y") # Get current date in d/m/y format
            items = text.split(",") # Split input string into variables
            try:
                # Extract All List Items Into Separate Variables #
                time = items[0]
                latitude = items[1]
                longitude = items[2]
                altitude = items[3]
                hdop = items[4]
                speed = items[5]

                # Create Console String #
                profileFlagText = ""
                if (self.profileFlag):
                    profileFlagText = " Profile Not Set"
                else:
                    profileFlagText = ""
                msg = f'Date: {self.date}, Time: {time}, Latitude: {latitude}, Longitude: {longitude}, Altitude: {altitude}, hdop: {hdop}, Speed: {speed}m/s   Current run: {str(self.timeCurrentRun)}s {profileFlagText}'
                self.consoleText.set(msg) # Set console string
            except:
                self.consoleText.set("Invalid GPS Data")

    # Create Plot #
    def plot(self, x, y, name):
        self.fig = Figure(figsize = (19, 8), dpi = 100) # Create plot figure
        self.plot1 = self.fig.add_subplot(111) # Create subplot
        self.plot1.plot(x, y) # Plot data from dataParser
        self.plot1.set(xlabel="Time (s)", ylabel="Power (kW)", title=name) # Set x and y labels and title
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.parent) # Create canvas for Tkinter integration
        self.canvas.draw() # Display canvas
        self.canvas.get_tk_widget().pack() # Show plot
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent) # Create plot toolbar 
        self.toolbar.update()
        self.canvas.get_tk_widget().pack() # Show toolbar

    # Create Plot Data Lists #
    def handleParser(self):
        parser = dataParser.dataParser("./logs/%s" % self.fileName)
        parser.readFile()
        parser.createTimeList()
        parser.calculateDistance()
        parser.calculateAcceleration()
        parser.calculateForce(self.car.weight)
        parser.calculateWork()
        parser.calculatePower()

        if (len(parser.timeList) > len(parser.powerList)):
            x = len(parser.timeList) - len(parser.powerList)
            parser.timeList = parser.timeList[x-1:-1]
        elif (len(parser.timeList) < len(parser.powerList)):
            x = len(parser.powerList) - len(parser.timeList)
            parser.powerList = parser.powerList[x-1:-1]
        self.p_max = max(parser.powerList)

        return (parser.timeList, parser.powerList)

    # Update Plot Data #
    def updatePlot(self, x, y, name):
        self.plot1.clear() # Clear currently plotted data
        self.plot1.plot(x, y) # Plot new data
        self.plot1.set(xlabel="Time (s)", ylabel="Power (kW)", title=name) # Update title
        self.plot1.set_xticks(self.plot1.get_xticks()[::5]) # Show only some values on x axis
        self.canvas.draw() # Show canvas
        self.canvas.get_tk_widget().pack() # Show plot
        self.fig.savefig("./plots/%s.png" % self.fileName) # Save plot to /plots directory

    # Get Current Run Time #
    def timer(self):
        if (self.timerState):
            self.endTime = time.time() * 1000 # End
            self.timeCurrentRun = round(((self.endTime - self.startTime) / 1000), 2)
        else:
            self.startTime = time.time() * 1000 # Start
        self.timerState = not self.timerState

    def getProfile(self):
        with open("./profiles/profile.csv", "r") as f:
            lines = f.readlines()
            print(lines[0])
            if (len(lines) > 0):
                print("tuk")
                self.profile = lines[0].split(",")
                self.profileFlag = False
            else:
                self.profileFlag = True
        f.close()

def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        master.destroy()

master = Tk()
master.geometry("1920x1080")
master.title("Draguino Uno")
master.wm_state('zoomed')
master.protocol("WM_DELETE_WINDOW", onClosing)
App(master)
mainloop()
