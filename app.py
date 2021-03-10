import os
import threading
import serial
import dataParser

from tkinter import *
from datetime import date

import serial.tools.list_ports as port_list
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

        # Global Class Variables #
        self.baudrate = 38400
        self.hdopMin = 300
        self.hdop = 9999
        self.speed = 0
        self.serialString = ""
        self.fileName = ""

        self.xarr = []
        self.yarr = []

        # Serial Port Object #
        self.serialPort = serial.Serial(port=self.options[0].device, baudrate=self.baudrate, bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)        

        # Port Dropdown Menu #
        self.opt = OptionMenu(self.parent, self.variable, self.options)
        self.opt.pack(side=TOP)

        # Refresh Ports List Button #
        self.refreshButton = Button(self.parent, text = "Refresh Ports", command=self.refreshPorts)
        self.refreshButton.pack(side=TOP)

        # Start Data Logging Button #
        self.logText = StringVar()
        self.logText.set("Start Data Log")
        self.startLogging = Button(self.parent, textvariable = self.logText, command=self.dataLog)
        self.startLogging.pack(side=TOP)

        # Start/Stop Real Time Data Parsing Button #
        self.dataStartStopText = StringVar()
        self.dataStartStopText.set("Pause Data Stream")
        self.dataStartStop = Button(self.parent, textvariable = self.dataStartStopText, command=self.dataStartStop)
        self.dataStartStop.pack(side=TOP)

        # Serial Data Label #
        self.consoleText = StringVar()
        self.consoleText.set("")
        self.consoleLabel = Label(self.parent, textvariable=self.consoleText, relief=FLAT, font=("Arial", 12))
        self.consoleLabel.pack(side=TOP)

        # Fix Status Label #
        self.fixText = StringVar()
        self.fixText.set("No Fix")
        self.fixLabel = Label(self.parent, textvariable=self.fixText, relief=FLAT, font=("Arial", 12))
        self.fixLabel.pack(side=TOP)

        # Create Plot #
        self.plot(self.xarr, self.yarr, "Draguino Uno Virtual Dyno")

        #Start Serial Data Reading
        self.startReadDataThread()

    # Update Serial Ports Dropdown Menu #
    def refreshPorts(self):
        self.options = list(port_list.comports())
        menu = self.opt["menu"]
        menu.delete(0, "end")
        for string in self.options:
            menu.add_command(label=string, command=lambda value=string: self.variable.set(value))

    # Create Filename For Logs & Plots #
    def createFileName(self):
        self.fileName = self.date + " " + self.time
        self.fileName = self.fileName.replace("/", ".")
        self.fileName = self.fileName.replace(":", "-")

    #Start/Stop Data Log Button Handler #
    def dataLog(self):
        self.logFlag = not self.logFlag
        if (self.logFlag):
            self.createFileName()
            self.logText.set("Stop Data Log")
        else:
            self.logText.set("Start Data Log")
            self.xarr = np.arange(0.0, 2.0, 0.01)
            self.yarr = 1 + np.sin(2 * np.pi * self.xarr)
            self.updatePlot(self.xarr, self.yarr, "Draguino Uno Virtual Dyno", self.fileName)

    # Start/Pause Serial Data Button Handler #
    def dataStartStop(self):
        if (self.dataStreamState):
            self.dataStartStopText.set("Pause Data Stream")
        else: 
            self.dataStartStopText.set("Start Data Stream")
        self.dataStreamState = not self.dataStreamState
        self.updateConsoleFlag = not self.updateConsoleFlag

    # Extract Data From Serial String Input #
    def extractData(self):
        parameters = self.serialString.split(",")
        self.time = parameters[0]
        self.latitude = parameters[1]
        self.longitude = parameters[2]
        self.altitude = parameters[3]
        self.hdop = parameters[4]
        self.speed = parameters[5]

    # Write Data To File #
    def writeToFile(self):
        if (self.logFlag):
            with open("./logs/%s.csv" % self.fileName, "a") as f:
                myList = [self.date, self.serialString]
                lst = map(str, myList)
                line = ",".join(lst)
                f.write(line + "\n")

    # GPS Fix Status Label Handler #
    def setFixStatus(self):
        if (float(self.hdop) <= self.hdopMin):
            self.fixText.set("Ok")
        else:
            self.fixText.set("No Fix")

    # Read Serial Data From Serial Port #
    def readData(self):
        self.serialPort.write(bytes.fromhex("A555FA"))
        while True:
            self.serialString = self.serialPort.readline().decode("UTF-8").replace('\n', '').rstrip()
            self.updateConsole(self.serialString)
            try:
                self.extractData()
                self.writeToFile()
                self.setFixStatus()
            except:
                print("Invalid GPS Data")
            print(self.serialString)
        self.serialPort.close()

    # Start Read Data Daemon Thread #
    def startReadDataThread(self):
        self.threadingTask = threading.Thread(target=self.readData, name="Read Data Thread", daemon=True)
        self.threadingTask.start()

    # Serial Data Label Handler #
    def updateConsole(self, text):
        if (self.updateConsoleFlag):
            self.date = date.today().strftime("%d/%m/%Y")
            items = text.split(",")
            try:
                self.consoleText.set("Date: " + self.date + ", Time: " + items[0] + ", Latitude: " + items[1] + ", Longitude: " + items[2] + ", Altitude: " + items[3] + ", hdop: " + items[4] + ", Speed: " + items[5] + "m/s")
            except:
                self.consoleText.set("Invalid GPS Data")

    # Create Plot #
    def plot(self, x, y, name):
        self.fig = Figure(figsize = (14, 6), dpi = 100) 
        self.plot1 = self.fig.add_subplot(111)
        self.plot1.plot(x, y) 
        self.plot1.set(xlabel="Time (s)", ylabel="Power (kW)", title=name)
        self.canvas = FigureCanvasTkAgg(self.fig, master = self.parent)   
        self.canvas.draw()
        self.canvas.get_tk_widget().pack() 
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.parent) 
        self.toolbar.update()
        self.canvas.get_tk_widget().pack()

    # Update Plot Data #
    def updatePlot(self, x, y, name, filename):
        parser = dataParser.dataParser("./logs/%s" % filename)
        parser.readFile()
        parser.createTimeList()
        parser.calculateDistance()
        parser.calculateAcceleration()
        parser.calculateForce(dataParser.car.weight)
        parser.calculateWork()
        parser.calculatePower()

        self.plot1.clear()
        self.plot1.plot(parser.timeList[0:-1], parser.powerList)
        self.plot1.set(xlabel="Time (s)", ylabel="Power (kW)", title=name)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        self.fig.savefig("./plots/%s.png" % filename)

master = Tk()
master.geometry("1400x800")
master.title("Draguino Uno")
App(master)
mainloop()
