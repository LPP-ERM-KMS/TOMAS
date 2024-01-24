# -*- coding: utf-8 -*-
# TOMAS NPA data analysis 
# contact: sunwoo@kth.se


##### Library #################################################################
import os
import sys
import numpy as np              
import tkinter as tk
from scipy import spatial
import matplotlib.pyplot as plt  
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo

##### Inputs ##################################################################
Program_type = 1 # 1 = CoMPASS, 2 = DPP-PSD
Gas_type = 'H' # input H or He
number_densities = {'B': 1.364744e29}

###########################
# Gui for selecting data: #
###########################
import tkinter as tk
from tkinter import filedialog

def open_Ch0_file_dialog():
    global ch0filepath
    ch0filepath = filedialog.askopenfilename(title="Select Ch0 file",initialdir=".." ,filetypes=[("csv files", "*.csv"), ("All files", "*.*")])
    if ch0filepath:
        selected_file_ch0_label.config(text=f"Selected File: {ch0filepath}")
def open_Ch1_file_dialog():
    global ch1filepath
    ch1filepath = filedialog.askopenfilename(title="Select Ch1 file", filetypes=[("csv files", "*.csv"), ("All files", "*.*")])
    if ch1filepath:
        selected_file_ch1_label.config(text=f"Selected File: {ch1filepath}")

def CloseDialog():
    root.destroy()

root = tk.Tk()
root.title("File Dialog Example")

open_button = tk.Button(root, text="Ch0 file", command=open_Ch0_file_dialog)
open_button.pack(padx=20, pady=20)

selected_file_ch0_label = tk.Label(root, text="Selected File:")
selected_file_ch0_label.pack()

open_button = tk.Button(root, text="Ch1 file", command=open_Ch1_file_dialog)
open_button.pack(padx=20, pady=20)

selected_file_ch1_label = tk.Label(root, text="Selected File:")
selected_file_ch1_label.pack()

done_button = tk.Button(root, text="Done", command=CloseDialog)
done_button.pack(padx=20, pady=20)

root.mainloop()

# If data was recorded in DPP-PSD
#NPA_file    = 'radialscan_from323_011_ls_0.dat' 
#Laser_file  = 'radialscan_from323_011_ls_1.dat'

##### Data load from data file ################################################
import Dataload_CoMPASS
import Dataload_DPPPSD
    
if ch0filepath and ch1filepath: # CoMPASS data
    Ch, Ch0, Laser_timing, Laser_interval, Ch1_timing = Dataload_CoMPASS.main(ch0filepath,ch1filepath) 
    Data_name = ch1filepath.split('_')[-2] + ch1filepath.split('_')[-1][:-4]

else:
    print("Not enough filepaths specified")
    sys.exit(1)

#if Program_type == 2: # DPP-PSD data
#    Data_name = NPA_file[:-4]
#    Ch, Ch0, Ch1 = Dataload_DPPPSD.main(NPA_file, Laser_file) # Mix, NPA, Laser
    

##### Arrival Time Distribution (ATD) and Energy Distribution (ED) of Neutral Particle (NP) 
import ATD_ED

if Program_type == 1: Unit_coeff = 1e6 # Conversion coefficient of laser timing unit to µs
if Program_type == 2: Unit_coeff = 250

AT_data, AT_Histogram_value, AT_Histogram_interval = ATD_ED.AT(Ch, Ch0, Unit_coeff)
ED_data, ED_Histogram_value, ED_Histogram_interval = ATD_ED.ED(AT_data, Gas_type)
AT_Histogram_value_sec, ED_Histogram_value_sec = ATD_ED.Normalization(Ch, Ch0, Gas_type, Unit_coeff)

if not os.path.exists("figures"):
    os.mkdir("figures")

##### Plot Arrival Time Distribution (ATD) #################################### 
plt.figure(1, figsize=(12, 8), dpi=80) 
plt.rcParams['lines.linewidth'] = 5
plt.rcParams.update({'font.size': 24})
plt.plot(AT_Histogram_interval, AT_Histogram_value, label='Arrival Time Distribution')
plt.yscale('log')
plt.xlim(left=0)
plt.legend()
plt.savefig('figures/ATD_{}.png'.format(Data_name), dpi=600)
plt.show()

##### Plot Energy Distribution (ED) ###########################################
plt.figure(2, figsize=(12, 8), dpi=80) 
plt.plot(ED_Histogram_interval, ED_Histogram_value_sec, label='Energy distribution / sec')
plt.yscale('log')
plt.xlim(left=0)
plt.legend()
plt.xlabel("E")
plt.ylabel("counts/s") #I assume this to be the case
plt.title("Energy Distribution")
plt.savefig('figures/ED_{}.png'.format(Data_name), dpi=600)
plt.show()


##### Passing Probability and Detection Efficiency ############################
import Detection_Efficiency 
# ED_DF = Detection_Efficiency.main(ED_Histogram_value) # Differential Flux (DF)
ED_DF_sec_cm2 = Detection_Efficiency.main(ED_Histogram_value_sec, Gas_type) # DF / sec
TOMAS_flux = Detection_Efficiency.totalflux(ED_DF_sec_cm2)  #4pi times sum of ED_DF_cm2, i.e over full sphere and summed over
Diff_TOMAS_flux = 2*np.pi*np.array(Detection_Efficiency.main(ED_Histogram_value_sec, Gas_type)) # over half sphere flux (samples receive no flux from top)

globals()['ED_DF_sec_{}'.format(Data_name)] = ED_DF_sec_cm2 # Save differential flux /sec for comparison
globals()['TOMAS_flux_{}'.format(Data_name)] = TOMAS_flux # Save total flux for comparison
        

##### Maxwell-Boltzmann Distribution Fitting (MBF) ############################
import Maxwell_fitting
T_eV = 13 # [eV]13
T_eV_hot = 55 # [eV] 55
Hot_ratio = 8 # [%] 8
T_eV, T_eV_hot, MBF, MBF_hot = Maxwell_fitting.main(TOMAS_flux, T_eV, T_eV_hot, Hot_ratio)
MBF_total = list(MBF[i] + MBF_hot[i] for i in range(len(MBF)))


##### Plot Final distribution and Maxwell fitting #############################
plt.figure(3, figsize=(12, 8), dpi=80) 
x_axis = [i for i in range(5, 730,  5)]
E = np.linspace(0, 725, num=726) # [eV]
plt.ylabel('Differential flux (H0 / cm2 eV s sr)')
plt.xlabel('Energy (eV)')
plt.plot(x_axis, ED_DF_sec_cm2, label='Experimental data')
plt.plot(E, MBF, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell {} eV ({} %)'.format(T_eV, (100 - Hot_ratio)))
plt.plot(E, MBF_hot, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell {} eV ({} %)'.format(T_eV_hot, Hot_ratio))
plt.plot(E, MBF_total, linestyle='-', linewidth=5, color='#1f77b4', alpha=0.5, label='Maxwell fitting')
plt.yscale('log')
plt.xlim(left = 0, right = 750)
plt.ylim(bottom = 1e7)#, top = 1e14)
plt.legend()
plt.savefig('figures/ED_DF_{}.png'.format(Data_name), dpi=600)
plt.show()

sputteringquestion = input('Do you want to calculate the sputtering rate based off these measurements? [y/n]')
if sputteringquestion == 'n':
    sys.exit(0)
elif sputteringquestion == 'y':
    target = input(f"What is the target material? (e.g B, we're assuming the flux to be {Gas_type} as it has been troughout the analysis):")
    yieldmapfilename = Gas_type + "On" + target + '.csv'
    YieldMapPath = 'YieldMaps/' + yieldmapfilename
    YieldMap = np.genfromtxt(YieldMapPath, delimiter=",")

    SearchFile = YieldMap[:,:2]
    #tree search algorithm
    tree = spatial.KDTree(SearchFile) 

    #-------------#
    #  Algorithm  #
    #-------------#
    Sr = 0
    E_avg = 0
    dE = 5
    print('diff tomasflux:')
    print(Diff_TOMAS_flux)
    print('len tomasflux:')
    print(len(Diff_TOMAS_flux))
    for i,e in enumerate(x_axis):
        IndexOfClosest = tree.query(np.array([e,0]))[1] #get index of closest lying computed yield
        Yield = YieldMap[IndexOfClosest][2]
        fluxpersec = Diff_TOMAS_flux[i]*dE #Diff_TOMAS_flux is the flux/(cm^2 eV s),
                                 #multiplied by the energy bin we get the flux/(s cm^2)
        Sr += fluxpersec*10e6/(number_densities[target]) #devided by number density (in cm^3) we get the erosion rate in cm/s
    for i,e in enumerate(x_axis):
        E_avg += Diff_TOMAS_flux[i]*e
    E_avg = E_avg/(np.sum(Diff_TOMAS_flux))
    Sr = Sr*(10**7) #convert to nm/s
    print("Vertical erosion rate: {} nm/s".format(Sr))
else:
    sys.exit(1)
