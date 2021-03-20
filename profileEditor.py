from tkinter import *
from tkinter import messagebox
import csv

class profileEditor():
    def __init__(self):
        # Tkinter Variables #
        self.parent = Tk()
        self.parent.geometry("420x260")
        self.parent.resizable(width=False, height=False)
        self.parent.title("Draguino Uno Profile Editor")

        # Input Entries Variables #
        self.inputValues = []
        self.fields = ["Manufacturer", "Model", "Weight", "Gear", "Ratios", 
                       "Final Drive", "Drag Coefficient", "Frontal Area", "Air Density"]
        self.labels = []
        self.entries = []
        self.inputs = []
        self.profiles = []

        self.getProfiles() # Fet all profiles
        self.variable = StringVar(self.parent) # Create dropdown menu variable
        self.variable.trace_add("write", self.saveCurrentProfile)

        # Set Default Value For Dropdown Variable #
        with open("./profiles/profile.csv", "r") as f:
            lines = f.readlines()
            if (len(lines) > 0):
                self.variable.set(lines[0])

        # Create Tk Widgets #
        self.createEntries()
        self.createProfileButton()
        self.profileDropDownMenu()
        self.deleteSelectedProfile()
        self.refreshProfiles()

        # Run Tkinter App #
        self.parent.mainloop()

    # Create All Labels And Entries #
    def createEntries(self):
        for i in range(len(self.fields)):
            label = Label(self.parent, text=self.fields[i])
            self.labels.append(label)
            self.labels[i].grid(column=0, row=i)

            entry = Entry(self.parent, )
            self.entries.append(entry)
            self.entries[i].grid(column=1, row=i)

        self.entries[0].focus()

    # Create New Profile Button #
    def createProfileButton(self):
        self.getButton = Button(self.parent, text="Create New Profile", command=self.createNewProfile)
        self.getButton.grid(column=0, row=9)

    # Select Current Profile Dropdown Button #
    def profileDropDownMenu(self):
        self.opt = OptionMenu(self.parent, self.variable, self.profiles)
        self.opt.grid(column=1, row=10)

    def deleteSelectedProfile(self):
        self.deleteProfileButton = Button(self.parent, text="Delete Selected Profile", command=self.deleteProfile)
        self.deleteProfileButton.grid(column=0,row=10)

    # Refresh Available Profiles Options #
    def refreshProfiles(self):
        self.getProfiles()
        menu = self.opt["menu"]
        menu.delete(0, "end")
        # print(self.profiles)
        for string in self.profiles:
            menu.add_command(label=string, command=lambda value=string: self.variable.set(value))   

    # Get Inputs From Entries #
    def getEntries(self): # Ok
        self.inputs = []
        for i in range(len(self.entries)):
            text = self.entries[i].get()
            num = self.isNumber(text)
            if (text):
                if (i in {2, 3, 5, 6, 7, 8}):
                    if (self.isNumber(text)):
                        self.inputs.append(text)
                    else:
                        return -1
            else:
                return 0

        for i in self.inputs:
            print(i)    
        return 1        

    # Create New Vehicle Profile #
    def createNewProfile(self):
        res = self.getEntries()
        if (res == 1):
            with open("./profiles/profiles.csv", "a") as f:
                line = ",".join(self.inputs)
                print(line)
                f.write(line + "\n")
            f.close()
            self.refreshProfiles()
        else:
            msg = ""
            if (res == 0):
                msg = "Please Enter All Details"
            elif (res == -1):
                msg = "Invalid Input"
            messagebox.showinfo("Error", msg)
            
    # Fetch All Available Profiles #
    def getProfiles(self):
        self.profiles = []
        f = open("./profiles/profiles.csv", "r")
        lines = f.readlines()
        for line in lines:
            values = line.split(",")
            newline = ",".join(values).rstrip()
            self.profiles.append(newline)

    # Delete Current Profile #
    def deleteProfile(self):
        profile = self.variable.get()
        print(profile)
        with open("./profiles/profiles.csv", "r") as f:
            lines = f.readlines()
        with open("./profiles/profiles.csv", "w") as f:
            for line in lines:
                if (line.rstrip() != profile):
                    print(line)
                    f.write(line)
        self.refreshProfiles()
        self.variable.set(self.profiles[0])

    # Save Current Profile When Dropdown Option Changes #
    def saveCurrentProfile(self, var, indx, mode):
        profile = self.variable.get()
        with open("./profiles/profile.csv", "w") as f:
            f.write(profile)

    # Check If A String Is Number #
    def isNumber(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

profileEditor()