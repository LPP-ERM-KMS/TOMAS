# TOMAS DAQ data analysis 
# An AA inc. product
import os
import re
import sys
import numpy as np              
from pathlib import Path
from scipy import spatial
from scipy import optimize
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
        y = 10**((y*1.25) - 9.75)/1000
        if GasType == "H":
            y *= 2.4
        elif GasType == "He":
            y *= 5.9
        elif GasType == "Ar":
            y *= 0.8
        unit = "mbar"
    if key == "Baratron":
        y = (y-1)*0.125*0.1
        unit = "mbar"
    return unit,y 

def TemperatureFunction(T,Vd2,Vd3):
    top = 1 - np.exp(-Vd2/T) #T in eV
    bottom = 1 - np.exp(-Vd3/T) #T in eV
    return top/bottom - 0.5

def DensityFunction(T,R,TP1,TP2,GasType,Current,position,Orientation):
    if T < 0.01:
        return 0

    e = 1.602176634E-19 #Coulomb
    c = 2.99792E8 #m/s
    B = 5.7E-5*Current*78/(78-position+26) #Tesla

    if Orientation == 1: #Vertical
        A = 6.4*1E-6
    else:
        A = (-0.96*B+13.96)*1E-6 #Zie TLP calibration van Johan

    if GasType == 'H':
        m = 9.3895E8 #eV/c^2
    elif GasType == 'He':
        m = 3.7284E9 #eV/c^2
    elif GasType == 'D':
        m = 2*9.3895E8 #eV/c^2

    top = (TP2/R)*np.exp(-TP1/T)
    bottom = np.exp(-1/2)*c*e*A*np.sqrt(T/m)*(1-np.exp(-TP1/T))
    return top/bottom

def PScan(FolderLocation,probecount):
    pathlist = Path(FolderLocation).rglob('*.LVM')
    Foldername=FolderLocation.split('/')[-1]
    win = tk.Toplevel()
    if probecount == 2 or probecount == 3:
        win.wm_title("Triple probe scan evaluation")
    if probecount == 4:
        win.wm_title("Quadruple probe scan evaluation")

    if not FolderLocation:
        print("Error, no folder selected")
        sys.exit(0)

    OrientationLabel = tk.Label(win, text="Current for Magnetic field:")
    Orientation = tk.IntVar()
    Vertical_btn = tk.Radiobutton(win, variable=Orientation, value=1,text="Vertical")
    Horizontal_btn = tk.Radiobutton(win, variable=Orientation, value=2,text="Horizontal")
    Vertical_btn.pack()
    Horizontal_btn.pack()

    Current = tk.StringVar()
    CurrentLabel = tk.Label(win, text="Current for Magnetic field:")
    CurrentEntry = tk.Entry(win, textvariable=Current)
    CurrentLabel.pack()
    CurrentEntry.pack()

    Voltage = tk.StringVar()
    VoltageLabel = tk.Label(win, text="Supply Voltage:")
    VoltageEntry = tk.Entry(win, textvariable=Voltage)
    VoltageLabel.pack()
    VoltageEntry.pack()

    TimeInterest = tk.StringVar()
    TimeLabel = tk.Label(win, text="Time of interest (-1 for the end)")
    TimeEntry = tk.Entry(win, textvariable=TimeInterest)
    TimeLabel.pack()
    TimeEntry.pack()

    Start = tk.StringVar()
    StartLabel = tk.Label(win, text="Start position (cm)")
    StartEntry = tk.Entry(win, textvariable=Start)
    StartLabel.pack()
    StartEntry.pack()

    StepSize = tk.StringVar()
    StepSizeLabel = tk.Label(win, text="Step size (cm)")
    StepSizeEntry = tk.Entry(win, textvariable=StepSize)
    StepSizeLabel.pack()
    StepSizeEntry.pack()

    Stop = tk.StringVar()
    StopLabel = tk.Label(win, text="Stop position (cm)")
    StopEntry = tk.Entry(win, textvariable=Stop)
    StopLabel.pack()
    StopEntry.pack()

    VoltageLabel = tk.Label(win, text="Circuit structure:")
    VoltageLabel.pack()

    Resistor= tk.IntVar()
    Up_btn = tk.Radiobutton(win, variable=Resistor, value=0,text="Up3-Up2-U2")
    R5_btn = tk.Radiobutton(win, variable=Resistor, value=158,text="R5")
    R6_btn = tk.Radiobutton(win, variable=Resistor, value=750, text="R6")
    R7_btn = tk.Radiobutton(win, variable=Resistor, value=3300, text="R7")
    R8_btn = tk.Radiobutton(win, variable=Resistor, value=9200, text="R8")

    RC_btn = tk.Radiobutton(win, variable=Resistor, value=909, text="900")

    Up_btn.pack()
    R5_btn.pack()
    R6_btn.pack()
    R7_btn.pack()
    R8_btn.pack()
    RC_btn.pack()

    Plot_button = tk.Button(win, text="Plot", command=lambda: PlotProbes(GasType.get(),float(Current.get()),probecount,Resistor.get(),pathlist,float(TimeInterest.get()),float(Voltage.get()),np.arange(float(Start.get()),float(Stop.get())+float(StepSize.get()),float(StepSize.get())),Orientation.get()))
    Plot_button.pack(pady=10)
    
    def GetProbeNames(ListboxSelection,probecount):
        Pselection = []
        for i in ListboxSelection:
            if probecount == 2:
                if re.findall(r'\d+',listbox.get(i)) == ['1']:
                    tp1 = probelistbox.get(i)
                else:
                    tp2 = probelistbox.get(i)
            elif probecount == 3:
                if re.findall(r'\d+',listbox.get(i)) == ['1']:
                    tp1 = probelistbox.get(i)
                elif re.findall(r'\d+',listbox.get(i)) == ['2']:
                    tp2 = probelistbox.get(i)
                else:
                    tp3 = probelistbox.get(i)
            elif probecount == 4:
                if re.findall(r'\d+',listbox.get(i)) == ['1']:
                    tp1 = probelistbox.get(i)
                elif re.findall(r'\d+',listbox.get(i)) == ['2']:
                    tp2 = probelistbox.get(i)
                elif re.findall(r'\d+',listbox.get(i)) == ['3']:
                    tp3 = probelistbox.get(i)
                else:
                    tp4 = probelistbox.get(i)
        if probecount == 2:
            return tp1,tp2
        elif probecount == 3:
            return tp1,tp2,tp3
        elif probecount == 4:
            return tp1,tp2,tp3,tp4


    def PlotProbes(GasType,Current,probecount,Resistor,pathlist,TimeInterest,SupplyVoltage,X,Orientation):
        if probecount == 2:
            T = []
            n = []
            numbers = []
            for l,path in enumerate(pathlist):
                path_in_str = str(path)   
                filename = path_in_str.split('/')[-1][:-4]
                number = filename.split('_')[-1]
                numbers.append(int(number))

                data = read(path)
                try: 
                    i = int(np.where('TP2' == np.array(data[0]['Channel names']))[0][0])
                except:
                    i = int(np.where('TP_1' == np.array(data[0]['Channel names']))[0][0])

                x = data[0]['data'][:,0]
                k = np.abs(TimeInterest - x).argmin()
                kBeginAvg = np.abs(TimeInterest - 0.1 - x).argmin()
                if TimeInterest == -1:
                    Tp1V = 5*float(data[0]['data'][-1,i][0]) #5 because otherwise saturation
                else:
                    kEndAvg = np.abs(TimeInterest + 0.1 - x).argmin()
                    Tp1V = 5*float(np.sum(data[0]['data'][kBeginAvg:kEndAvg,i])/(kEndAvg-kBeginAvg)) 
                    

                try: 
                    j = int(np.where('TP2' == np.array(data[0]['Channel names']))[0][0])
                except: 
                    j = int(np.where('TP_1' == np.array(data[0]['Channel names']))[0][0])

                x_ = data[0]['data'][:,0]
                k = np.abs(TimeInterest - x_).argmin()
                kBeginAvg = np.abs(TimeInterest - 0.1 - x_).argmin() 
                if TimeInterest == -1:
                    Tp2V = data[0]['data'][-1,j]
                else:
                    kEndAvg = np.abs(TimeInterest + 0.1 - x_).argmin()#average over 0.2s
                    Tp2V = float(np.sum(data[0]['data'][kBeginAvg:kEndAvg,j])/(kEndAvg-kBeginAvg))
                TGuess = Tp1V/np.log(2)
                if TGuess > 0:
                    Tfinal = 0
                else:
                    Tfinal = optimize.newton(TemperatureFunction,x0=abs(TGuess),args=(abs(Tp1V),SupplyVoltage))
                T.append(Tfinal)
                position = X[l]
                n.append(DensityFunction(Tfinal,Resistor,Tp1V,Tp2V,GasType,Current,position,Orientation))

            T = np.array(T)
            n = np.array(n)
            #Check if mostly negative or positive
            if len(np.where(T < 0)[0]) > len(np.where(T > 0)[0]):
                T = -1*T
            T[np.where(T<0)[0]] = 0 #set others to zero
            sortednumbers = sorted(numbers)
            CorrectedT = np.zeros(len(T))
            for i,number in enumerate(sortednumbers):
                #index of old list
                j = np.where(number == np.array(numbers))[0][0]
                CorrectedT[i] = T[j]
            Correctedn = np.zeros(len(n))
            for i,number in enumerate(sortednumbers):
                #index of old list
                j = np.where(number == np.array(numbers))[0][0]
                Correctedn[i] = n[j]


            plt.plot(X,CorrectedT)
            plt.xlabel("position (cm)")
            plt.ylabel("Temperature (eV)")
            plt.show()

            plt.plot(X,Correctedn)
            plt.xlabel("position (cm)")
            plt.ylabel(r"Density ($\frac{particles}{m^3}$)")
            plt.show()


    
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
GasType = StringVar(root)
GasType.set('H')
w = OptionMenu(root, GasType, *choices)
w.pack(in_=top)

open_button = tk.Button(root, text="DAQ file", command=open_Ch0_file_dialog)
open_button.pack(padx=20, pady=20,in_=top)

open_button.pack(in_=top)

selected_file_ch0_label = tk.Label(root, text="Selected File:")
selected_file_ch0_label.pack(in_=top)
    
PlotVoltages_button = tk.Button(root, text="Plot voltages", command= lambda: SelectSignals(ch0filepath,False,GasType.get()))

PlotSignals_button = tk.Button(root, text="Plot Signals", command= lambda: SelectSignals(ch0filepath,True,GasType.get()))

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

export_V_button = tk.Button(root, text="Voltages", command= lambda: ConvertFolder(ch1filepath,exportvariable.get(),GasType.get()))
export_V_button.pack(pady=10,in_=bottom,side=LEFT,fill="none",expand=True)

export_S_button = tk.Button(root, text="Signals 🚧", command= lambda: ConvertFolder(ch1filepath,exportvariable.get(),GasType.get()))
export_S_button.pack(pady=10,in_=bottom,side=LEFT,fill="none",expand=True)

select_export = tk.Label(root, text="Probe scan analysis")
select_export.pack(in_=south)

P_scan = tk.Button(root, text="TP1&TP2", command= lambda: PScan(ch1filepath,2))
P_scan.pack(in_=south,side=LEFT,fill="none",expand=True)

P_scan2 = tk.Button(root, text="TP1-3", command= lambda: PScan(ch1filepath,3))
P_scan2.pack(in_=south,side=LEFT,fill="none",expand=True)

P_scan3 = tk.Button(root, text="QP", command= lambda: PScan(ch1filepath,4))
P_scan3.pack(in_=south,side=LEFT,fill="none",expand=True)

done_button = tk.Button(root, text="Done", command=CloseDialog)
done_button.pack(pady=10)

root.mainloop()
