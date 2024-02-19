# TOMAS DAQ data analysis 
# An AA inc. product
import os
import sys
import numpy as np              
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

def PlotVoltages():
    PlotFile(1)

def PlotFile(selection):
    ToRead = ch0filepath
    if not ToRead:
        print("Error, no file selected")
        sys.exit(0)
    if selection == 1:
        #header
        data = read(ToRead)
        keys = data[0]['Channel names'][:-1]
        for i,key in enumerate(keys):
            if i == 0:
                continue
            x = data[0]['data'][:,0]
            y = data[0]['data'][:,i]
            plt.plot(x,y,label=key)
            plt.xlabel("time (s)")
            plt.ylabel("Voltage")
            plt.legend()
        plt.show()
    
def SelectSignals(ToRead):
    win = tk.Toplevel()
    win.wm_title("Select Signals")
    # Create a listbox
    listbox = Listbox(win, width=40, height=10, selectmode=MULTIPLE)
     
    # Inserting the listbox items
    if not ToRead:
        print("Error, no file selected")
        sys.exit(0)
    data = read(ToRead)
    keys = data[0]['Channel names'][:-1]
    for i,key in enumerate(keys):
        listbox.insert(i, key)
     
    # Function for printing the
    # selected listbox value(s)
    def selected_item():
        # Traverse the tuple returned by
        # curselection method and print
        # corresponding value(s) in the listbox
        ToPlot = []
        for i in listbox.curselection():
            ToPlot.append(listbox.get(i))
        lookuptable = np.array(data[0]['Channel names'][:-1])
        plt.clf()
        for key in ToPlot:
            i = np.where(key == lookuptable)[0]
            x = data[0]['data'][:,0]
            y = data[0]['data'][:,i]
            plt.plot(x,y,label=key)
            plt.xlabel("time (s)")
            plt.ylabel("Voltage")
            plt.legend()
        plt.show()

     
    # Create a button widget and
    # map the command parameter to
    # selected_item function
    btn = Button(win, text='Plot Selected', command=selected_item)
     
    # Placing the button and listbox
    btn.pack(side='bottom')
    listbox.pack()

    
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
root.title("File Dialog Example")

selected_file_ch1_label = tk.Label(root, text="Gas type:")
selected_file_ch1_label.pack()

choices = ['H','D', 'He','Ar']
variable = StringVar(root)
variable.set('H')
w = OptionMenu(root, variable, *choices)
w.pack()

open_button = tk.Button(root, text="DAQ file", command=open_Ch0_file_dialog)
open_button.pack(padx=20, pady=20)

selected_file_ch0_label = tk.Label(root, text="Selected File:")
selected_file_ch0_label.pack()
    
PlotSignals_button = tk.Button(root, text="Plot voltages", command= lambda: SelectSignals(ch0filepath))
PlotSignals_button.pack(padx=20, pady=20)

open_button = tk.Button(root, text="folder containing DAQ files", command=open_Ch1_file_dialog)
open_button.pack(padx=20, pady=20)

done_button = tk.Button(root, text="Done", command=CloseDialog)
done_button.pack(padx=20, pady=20)

root.mainloop()


