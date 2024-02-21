# TOMAS DAQ data analysis 
# An AA inc. product
import os
import sys
import numpy as np              
from pathlib import Path
from scipy import spatial
from lvm_read import read
import matplotlib.pyplot as plt  
from tkinter import filedialog as fd
from tkinter import *
from tkinter import StringVar, OptionMenu
from tkinter.messagebox import showinfo

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def PlotFile(selection):
    ToRead = ch0filepath
    if not ToRead:
        print("Error, no file selected")
        sys.exit(0)
    if selection == 1:
        #header
        data = read(ToRead)
        keys = data[0]['Channel names']
        for i,key in enumerate(keys):
            x = data[0]['data'][:,0]
            y = data[0]['data'][:,i]
            plt.plot(x,y,label=key)
            plt.xlabel("time (s)")
            plt.ylabel("Voltage")
            plt.legend()
        plt.show()
    
def SelectSignals(ToRead,convert,GasType):
    win = tk.Toplevel()
    win.wm_title("Select Signals")
    # Create a listbox
    listbox = Listbox(win, width=40, height=10, selectmode=MULTIPLE)
     
    # Inserting the listbox items
    if not ToRead:
        print("Error, no file selected")
        sys.exit(0)
    data = read(ToRead)
    keys = data[0]['Channel names']
    for i,key in enumerate(keys):
        if key=="X_Value" or key=="Comment":
                continue
        listbox.insert(i, key)
     
    # Function for printing the
    # selected listbox value(s)
    def selected_item():
        # Traverse the tuple returned by
        # curselection method and print
        # corresponding value(s) in the listbox
        ToPlot = []
        unit = "Volts"
        for i in listbox.curselection():
            ToPlot.append(listbox.get(i))
        lookuptable = np.array(data[0]['Channel names'][:-1])
        plt.clf()
        for key in ToPlot:
            i = np.where(key == lookuptable)[0]
            x = data[0]['data'][:,0]
            y = data[0]['data'][:,i]
            if convert:
                unit,y = Convert(key,y,GasType)
            plt.plot(x,y,label=key)
            plt.xlabel("time (s)")
            plt.ylabel(unit)
            plt.legend()
        plt.show()

     
    # Create a button widget and
    # map the command parameter to
    # selected_item function
    btn = Button(win, text='Plot Selected', command=selected_item)
     
    # Placing the button and listbox
    btn.pack(side='bottom')
    listbox.pack()

def Convert(key,y,GasType):
    unit = "Not known"
    if key == "ECF" or key == "ECR":
        y *= 600
        unit = "Watts"
    if key == "ICF":
        y = 10**(((y/0.02485 - 91.29577) + 70)/10 - 3)
        unit = "Watts"
    if key == "ICR":
        y = 10**(((y/0.0241 - 96.43154) + 70)/10 - 3)
        unit = "Watts"
    if key == "Penning":
        y = 10**((y*1.25) - 9.75)/100
        if GasType == "H":
            y *= 2.4
        elif GasType == "He":
            y *= 5.9
        elif GasType == "Ar":
            y *= 0.8
        unit = "mbar"
    if key == "Baratron":
        y = (y-1)*0.125
        unit = "mbar"
    return unit,y 
    
def ConvertFolder(FolderLocation,convert,GasType):
    pathlist = Path(FolderLocation).rglob('*.LVM')
    Foldername=FolderLocation.split('/')[-1]
    if convert == 'csv':
        import csv
        CSVFolderLocation = FolderLocation+f'/../{Foldername}-CSV'
        Path(CSVFolderLocation).mkdir(exist_ok=True)
    elif convert == 'mat':
        from scipy.io import savemat
        MATFolderLocation = FolderLocation+f'/../{Foldername}-MAT'
        Path(MATFolderLocation).mkdir(exist_ok=True)
    for path in pathlist:
        # because path is object not string
        path_in_str = str(path)   
        filename = path_in_str.split('/')[-1][:-4]
        data = read(path)
        fieldnames = data[0]['Channel names']
        FieldnameList =[str(fieldname) for fieldname in fieldnames]

        if convert == 'csv':
            with open(f'{CSVFolderLocation}/{filename}.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(FieldnameList)
                datalength=len(data[0]['data'][:,0])    
                writer.writerows(data[0]['data'][:])
                
        if convert == 'mat':
            mdic = {}
            for key in FieldnameList:
                if key == 'Comment':
                    continue
                i = np.where(key == np.array(FieldnameList))
                y = data[0]['data'][:,i]
                mdic[key] = y
            savemat(f'{MATFolderLocation}/{filename}.mat',mdic)
                
###########################
# Gui for selecting data: #
###########################
import tkinter as tk
from tkinter import filedialog

def open_Ch0_file_dialog():
    global ch0filepath
    ch0filepath = filedialog.askopenfilename(title="Select one DAQ file",initialdir=".." ,filetypes=[("labview files", "*.LVM"), ("All files", "*.*")])
    if ch0filepath:
        selected_file_ch0_label.config(text=f"Selected File: {ch0filepath}")

def open_Ch1_file_dialog():
    global ch1filepath
    ch1filepath = filedialog.askdirectory(title="select a folder containing multiple DAQ files")
    if ch1filepath:
        selected_file_ch1_label.config(text=f"Selected folder: {ch1filepath}")

def CloseDialog():
    root.destroy()

root = tk.Tk()
root.title("DAQ file explorer")

top = Frame(root)
bottom = Frame(root)
south = Frame(root)
top.pack(anchor=N)
bottom.pack(anchor=CENTER)
south.pack(anchor=S)

selected_file_ch1_label = tk.Label(root, text="Gas type:")
selected_file_ch1_label.pack(in_=top)

choices = ['H','D', 'He','Ar']
variable = StringVar(root)
variable.set('H')
w = OptionMenu(root, variable, *choices)
w.pack(in_=top)

open_button = tk.Button(root, text="DAQ file", command=open_Ch0_file_dialog)
open_button.pack(padx=20, pady=20,in_=top)

open_button.pack(in_=top)

selected_file_ch0_label = tk.Label(root, text="Selected File:")
selected_file_ch0_label.pack(in_=top)
    
PlotVoltages_button = tk.Button(root, text="Plot voltages", command= lambda: SelectSignals(ch0filepath,False,variable.get()))

PlotSignals_button = tk.Button(root, text="Plot Signals", command= lambda: SelectSignals(ch0filepath,True,variable.get()))

PlotVoltages_button.pack(pady=10,in_=top, side=LEFT,fill="none",expand=True)
PlotSignals_button.pack(pady=10,in_=top, side=LEFT,fill="none",expand=True)

open_button = tk.Button(root, text="folder containing DAQ files", command=open_Ch1_file_dialog)
open_button.pack(pady=20,in_=bottom)

selected_file_ch1_label = tk.Label(root, text="Selected Folder:")
selected_file_ch1_label.pack(in_=bottom)

select_export = tk.Label(root, text="Export to format")
select_export.pack(in_=bottom)

exportchoices = ['csv','mat']
exportvariable = StringVar(root)
exportvariable.set('csv')
exportw = OptionMenu(root, exportvariable, *exportchoices)
exportw.pack(pady=10,in_=bottom)

select_export = tk.Label(root, text="In the form of:")
select_export.pack(in_=bottom)

export_V_button = tk.Button(root, text="Voltages", command= lambda: ConvertFolder(ch1filepath,exportvariable.get(),variable.get()))
export_V_button.pack(pady=10,in_=bottom,side=LEFT,fill="none",expand=True)

export_S_button = tk.Button(root, text="Signals", command= lambda: ConvertFolder(ch1filepath,exportvariable.get(),variable.get()))
export_S_button.pack(pady=10,in_=bottom,side=LEFT,fill="none",expand=True)

done_button = tk.Button(root, text="Done", command=CloseDialog)
done_button.pack(in_=south)

root.mainloop()
