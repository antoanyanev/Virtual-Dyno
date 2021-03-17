import math
import geopy.distance
import Vehicle

class dataParser():
    def __init__(self, fileName):
        self.file = open("%s.csv" % fileName, "r") # Open log file
        
        # Data from all lines #
        self.dates = []
        self.times = []
        self.latitudes = []
        self.longitudes = []
        self.altitudes = []
        self.hdops = []
        self.speeds = []

        # Time variables from timeList #
        self.elapsedSeconds = 0
        self.elapsedCentiseconds = 0

        # Lists used for calculating output power #
        self.timeList = []
        self.distances = []
        self.accelerations = []
        self.forces = []
        self.works = []
        self.powerList = []
        self.altitudeChanges = []

        self.applyDenivelationCompensationFlag = False
        self.applyAirDragCompensationFlag = False

        self.g = 9.81

        # List used for plot x_ticks #
        self.times_x = []

    # Read Input File Line By Line #
    def readFile(self):
        self.lines = self.file.readlines() # Fetch a list of lines
        for line in self.lines: # Extract data from each line
            self.extractData(line)
            # print(line)

    # Append Data From Each Line Into Separate List #
    def extractData(self, line):
        # Append Data From EacH Line Into The Appropriate List #
        items = line.split(",")
        self.dates.append(items[0])
        self.times.append(items[1])
        self.latitudes.append(float(items[2]))
        self.longitudes.append(float(items[3]))
        self.altitudes.append(float(items[4]))
        self.hdops.append(int(items[5]))
        self.speeds.append(float(items[6]))

    # Create List For X Axis #
    def createTimeList(self):
        for time in self.times:
            # Extract Seconds And Centiseconds #
            values = time.split(":")
            sec = values[2].split(".")
            centiseconds = int(sec[1])

            if (self.elapsedCentiseconds < 90): 
                self.elapsedCentiseconds += (centiseconds - self.elapsedCentiseconds)
            else: # A Full seconds has passed
                self.elapsedCentiseconds = 0
                self.elapsedSeconds += 1        

            # Create X Axis List And X_ticks List #
            self.timeList.append(str(self.elapsedSeconds) + "." + str(self.elapsedCentiseconds))
            self.times_x.append(self.elapsedSeconds)

    # Calculate Distance Between Two Geographical Coordinates #
    def calculateDistance(self):
        for i in range(len(self.latitudes) - 1):
            coords1 = (self.latitudes[i], self.longitudes[i]) # Create first lat long tuple
            coords2 = (self.latitudes[i+1], self.longitudes[i+1]) # Create secibds lat long tuple
            d = geopy.distance.distance(coords1, coords2).km / 1000 # Calculate distanse between two points using geopy
            self.distances.append(d) # Add distance to list

    # Calculate Acceleration Based On Velocity Change And Time #
    def calculateAcceleration(self):
        for i in range(len(self.speeds) - 1):
            v1 = self.speeds[i] # Get first speed
            v2 = self.speeds[i+1] # Get second speed
            dt = self.calculateTime(self.timeList[i], self.timeList[i+1]) # Retrieve time difference
            a = round(((abs(v2 - v1)) / dt), 2) # Calculate acceleration
            self.accelerations.append(a) # Append acceleration to list

    # Calculate Time Difference #
    def calculateTime(self, t1, t2):
        time1 = float(t1) # Time 1
        time2 = float(t2) # Time 2
        dt = round((time2 - time1), 2) # Calculate time difference
        return dt 

    # Calculate Force Based On Acceleration And Vehicle Mass #
    def calculateForce(self, mass):
        for acc in self.accelerations:
            f = round((mass * acc), 2) # Calculate force
            self.forces.append(f) # Append force to list

    def applyDenivelationCompensation(self):
        self.applyDenivelationCompensationFlag = True

    def applyAirDragCompensation(self):
        self.applyAirDragCompensationFlag = True

    def calclateAltitudeDifference(self):
        for i in range(self.altitudes - 1):
            dalt = self.altitudes[i] - self.altitudes[i+1]
            self.altitudeChanges.append(dalt)

    def applyCompensations(mass, cd, fa, ro):
        if (self.applyDenivelationCompensationFlag):
            for i in range(len(self.altitudeChanges)):
                faltch = mass * self.g * self.altitudeChanges[i] / self.distances[i]
                self.forces[i] += faltch

        if (self.applyAirDragCompensationFlag):
            for i in range(len(self.speeds)):
                fad = 1/2 * ro * (maself.speeds[s] ** 2) * cd * fa
                self.forces[i] += fad
        

    # Calculate Work Needed To Move Vehicle Over A Certain Distance #
    def calculateWork(self):
        for i in range(len(self.forces)):
            dA = self.forces[i] * self.distances[i] # Calculate work
            self.works.append(dA) # Append work to list

    # Calculate Power Based On Change Of Work Over A Time Period #
    def calculatePower(self):
        for i in range(len(self.works)):
            if (float(self.timeList[i]) != 0):
                p = self.works[i] / float(self.timeList[i]) # Calculate power
                self.powerList.append(p) # Appends power to list

# Vehicle Instance For Calculations #
car = Vehicle.Vehicle("VW", "GOLF MkIV 1.6SR", 1150, 3, [], 1, 0.34, 1.905, 1.18)