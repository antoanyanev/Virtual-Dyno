from tkinter import *
from tkinter import messagebox
import csv

class profileEditor():
    def __init__(self):
        self.parent = Tk()
        self.parent.geometry("1125x600")
        self.parent.title("Draguino Uno Profile Editor")

        self.inputValues = []
        self.fields = ["Manufacturer", "Model", "Weight", "Gear", "Ratios", 
                       "Final Drive", "Drag Coefficient", "Frontal Area", "Air Density"]
        self.labels = []
        self.entries = []
        self.inputs = []
        self.profiles = []

        self.getProfiles()
        self.variable = StringVar(self.parent)
        if (len(self.profiles) > 0):
            self.variable.set(self.profiles[0])

        self.createEntries()
        self.createProfileButton()
        self.profileDropDownMenu()
        self.refreshProfiles()

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
        self.opt.grid(column=2,row=2)

    # Refresh Available Profiles Options #
    def refreshProfiles(self):
        self.getProfiles()
        menu = self.opt["menu"]
        menu.delete(0, "end")
        print(self.profiles)
        for string in self.profiles:
            menu.add_command(label=string, command=lambda value=string: self.variable.set(value))   

    # Get Inputs From Entries #
    def getEntries(self): # Ok
        self.inputs = []
        for i in range(len(self.entries)):
            text = self.entries[i].get()
            if (text):
                self.inputs.append(text)
            else:
                return 0

        for i in self.inputs:
            print(i)    
        return 1        

    # Create New Vehicle Profile #
    def createNewProfile(self):
        res = self.getEntries()
        if (not res):
            messagebox.showinfo("Error", "Please Enter All Details!")
        else:
            with open("./profiles/profiles.csv", "a") as f:
                line = ",".join(self.inputs)
                print(line)
                f.write(line + "\n")
            f.close()
            self.refreshProfiles()

    # Fetch All Available Profiles #
    def getProfiles(self):
        self.profiles = []
        f = open("./profiles/profiles.csv", "r")
        lines = f.readlines()
        for line in lines:
            values = line.split(",")
            newline = ", ".join(values).rstrip()
            self.profiles.append(newline)

profileEditor()