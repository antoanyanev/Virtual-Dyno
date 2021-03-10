import math
import geopy.distance
import Vehicle

class dataParser():
    def __init__(self, fileName):
        self.file = open("%s.csv" % fileName, "r")
        self.dates = []
        self.times = []
        self.latitudes = []
        self.longitudes = []
        self.altitudes = []
        self.hdops = []
        self.speeds = []

        self.elapsedSeconds = 0
        self.elapsedCentiseconds = 0

        self.timeList = []
        self.distances = []
        self.accelerations = []
        self.forces = []
        self.works = []
        self.powerList = []

        self.times_x = []

    def readFile(self):
        self.lines = self.file.readlines()
        for line in self.lines:
            self.extractData(line)
            # print(line)

    def extractData(self, line):
        items = line.split(",")
        self.dates.append(items[0])
        self.times.append(items[1])
        self.latitudes.append(float(items[2]))
        self.longitudes.append(float(items[3]))
        self.altitudes.append(float(items[4]))
        self.hdops.append(int(items[5]))
        self.speeds.append(float(items[6]))

    def createTimeList(self):
        for time in self.times:
            values = time.split(":")
            sec = values[2].split(".")
            centiseconds = int(sec[1])

            if (self.elapsedCentiseconds < 90):
                self.elapsedCentiseconds += (centiseconds - self.elapsedCentiseconds)
            else:
                self.elapsedCentiseconds = 0
                self.elapsedSeconds += 1        

            self.timeList.append(str(self.elapsedSeconds) + "." + str(self.elapsedCentiseconds))
            self.times_x.append(str(self.elapsedSeconds))

    def calculateDistance(self):
        for i in range(len(self.latitudes) - 1):
            coords1 = (self.latitudes[i], self.longitudes[i])
            coords2 = (self.latitudes[i+1], self.longitudes[i+1])
            d = geopy.distance.distance(coords1, coords2).km / 1000
            self.distances.append(d)

    def calculateAcceleration(self):
        for i in range(len(self.speeds) - 1):
            v1 = self.speeds[i]
            v2 = self.speeds[i+1]
            dt = self.calculateTime(self.timeList[i], self.timeList[i+1])
            a = round(((abs(v2 - v1)) / dt), 2)
            self.accelerations.append(a)

    def calculateTime(self, t1, t2):
        time1 = float(t1)
        time2 = float(t2)
        dt = round((time2 - time1), 2)
        return dt

    def calculateForce(self, mass):
        for acc in self.accelerations:
            f = round((mass * acc), 2)
            self.forces.append(f)

    def calculateWork(self):
        for i in range(len(self.forces)):
            dA = self.forces[i] * self.distances[i]
            self.works.append(dA)

    def calculatePower(self):
        for i in range(len(self.works)):
            if (float(self.timeList[i]) != 0):
                p = self.works[i] / float(self.timeList[i])
                self.powerList.append(p)

car = Vehicle.Vehicle("VW", "GOLF MkIV 1.6SR", 1150, 3, [], 1, 0.34, 1.905)