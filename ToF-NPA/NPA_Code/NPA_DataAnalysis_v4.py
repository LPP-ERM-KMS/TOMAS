# -*- coding: utf-8 -*-
# TOMAS NPA data analysis 
# contact: sunwoo@kth.se

##### Library #################################################################
import os
import sys
from bcolors import bcolors
import numpy as np              
import tkinter as tk
from scipy import spatial
import matplotlib.pyplot as plt  
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from tkinter import StringVar, OptionMenu
from matplotlib.widgets import Button, Slider

##### Inputs ##################################################################
Program_type = 1 # 1 = CoMPASS, 2 = DPP-PSD
global number_densities
number_densities = {'B': 1.364744e29}

###########################
# Gui for selecting data: #
###########################
import tkinter as tk
from tkinter import filedialog

def open_Ch0_file_dialog():
    global ch0filepath
    ch0filepath = filedialog.askopenfilename(title="Select Ch0 file",initialdir=".." ,filetypes=[("CSV files", "*.CSV"),("csv files", "*.csv"), ("All files", "*.*")])
    if ch0filepath:
        selected_file_ch0_label.config(text=f"Selected File: {ch0filepath}")
def open_Ch1_file_dialog():
    global ch1filepath
    ch1filepath = filedialog.askopenfilename(title="Select Ch1 file", filetypes=[("csv files", "*.CSV"),("csv files", "*.csv"), ("All files", "*.*")])
    if ch1filepath:
        selected_file_ch1_label.config(text=f"Selected File: {ch1filepath}")

def CloseDialog():
    root.destroy()

root = tk.Tk()
root.title("File Dialog Example")

ExposureTime = tk.DoubleVar()
label = tk.Label(root, text="Exposure time (s):")
label.pack(padx=20, pady=20)
entry = tk.Entry(root, textvariable=ExposureTime)
entry.pack(padx=20, pady=20)

open_button = tk.Button(root, text="Ch0 file", command=open_Ch0_file_dialog)
open_button.pack(padx=20, pady=20)

selected_file_ch0_label = tk.Label(root, text="Selected File:")
selected_file_ch0_label.pack()

open_button = tk.Button(root, text="Ch1 file", command=open_Ch1_file_dialog)
open_button.pack(padx=20, pady=20)

selected_file_ch1_label = tk.Label(root, text="Gas type:")
selected_file_ch1_label.pack()

choices = ['H', 'He']
variable = StringVar(root)
variable.set('H')

w = OptionMenu(root, variable, *choices)
w.pack()

done_button = tk.Button(root, text="Done", command=CloseDialog)
done_button.pack(padx=20, pady=20)

root.mainloop()

Gas_type = variable.get()

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
    print(bcolors.FAIL + "Not enough filepaths specified" + bcolors.ENDC)
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
AT_Histogram_value_sec, ED_Histogram_value_sec = ATD_ED.Normalization(Ch, Ch0, Gas_type, Unit_coeff,ExposureTime.get())

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
plt.show()


##### Passing Probability and Detection Efficiency ############################
import Detection_Efficiency 
# ED_DF = Detection_Efficiency.main(ED_Histogram_value) # Differential Flux (DF)
global ED_DF_sec_cm2
ED_DF_sec_cm2 = Detection_Efficiency.main(ED_Histogram_value_sec, Gas_type) # DF / sec
global TOMAS_flux
TOMAS_flux = Detection_Efficiency.totalflux(ED_DF_sec_cm2)  #4pi times sum of ED_DF_cm2, i.e over full sphere and summed over
Diff_TOMAS_flux = 2*np.pi*np.array(Detection_Efficiency.main(ED_Histogram_value_sec, Gas_type)) # over half sphere flux (samples receive no flux from top)

globals()['ED_DF_sec_{}'.format(Data_name)] = ED_DF_sec_cm2 # Save differential flux /sec for comparison
globals()['TOMAS_flux_{}'.format(Data_name)] = TOMAS_flux # Save total flux for comparison
        

##### Maxwell-Boltzmann Distribution Fitting (MBF) ############################
import Maxwell_fitting
T_eV = 20.266 # [eV] 26 guess
T_eV_hot = 103.15 # [eV] 100 guess
Hot_ratio = 30 # [%] 8 guess
T_eV, T_eV_hot, Hot_ratio = Maxwell_fitting.Fit(ED_DF_sec_cm2,TOMAS_flux, T_eV, T_eV_hot, Hot_ratio)
T_eV, T_eV_hot, MBF, MBF_hot = Maxwell_fitting.main(TOMAS_flux, T_eV, T_eV_hot, Hot_ratio)
MBF_total = MBF + MBF_hot


##### Plot Final distribution and Maxwell fitting #############################
fig, ax = plt.subplots()
global x_axis
x_axis = [i for i in range(5, 730,  5)]
global E
E = np.linspace(0, 725, num=726) # [eV]
ax.set_ylabel('Differential flux (H0 / cm2 eV s sr)')
ax.set_xlabel('Energy (eV)')
ax.plot(x_axis, ED_DF_sec_cm2, label='Experimental data')


#R^2
Mean = 1/len(ED_DF_sec_cm2)*np.sum(ED_DF_sec_cm2)
SSres = 0
SStot = 0
for x_axis_index,energy in enumerate(x_axis):
    if energy in E:
        SSres += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(MBF_total[np.where(np.isclose(E,energy))]))**2
        SStot += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(Mean))**2
Rsquared = 1 - SSres/SStot

ax.plot(E, MBF, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell with T={:#.5g} eV ({:#.4g} %)'.format(T_eV, (100 - Hot_ratio)))
ax.plot(E, MBF_hot, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell with T={:#.5g} eV ({:#.4g} %)'.format(T_eV_hot, Hot_ratio))
ax.plot(E, MBF_total, linestyle='-', linewidth=5, color='#1f77b4', alpha=0.5, label='Bi-maxwellian fitting with $R^2$={:#.4g}'.format(Rsquared[0]))


# adjust the main plot to make room for the sliders
fig.subplots_adjust(left=0.30, bottom=0.30)

# Sliders
## Make a horizontal slider to control the T_eV_cold
axcold = fig.add_axes([0.25, 0.07, 0.65, 0.03]) #left bottom width height
ColdSlider = Slider(
    ax=axcold,
    label='T_eV of the cold neutrals',
    valmin=0.1,
    valmax=30,
    valinit=T_eV,
)
## Make a horizontal slider to control the T_eV_hot
axhot = fig.add_axes([0.25, 0.15, 0.65, 0.03])
HotSlider = Slider(
    ax=axhot,
    label='T_eV of the hot neutrals',
    valmin=30,
    valmax=150,
    valinit=T_eV_hot,
)
## Make a vertical slider to control the ratio
axratio = fig.add_axes([0.07, 0.25, 0.0225, 0.63])
RatioSlider = Slider(
    ax=axratio,
    label='Ratio (%)',
    valmin=0,
    valmax=100,
    valinit=Hot_ratio,
    orientation="vertical"
)
## Make a vertical slider to create an offset
energyoffset = fig.add_axes([0.21, 0.25, 0.0225, 0.63])
OffsetSlider = Slider(
    ax=energyoffset,
    label='E offset',
    valmin=0,
    valmax=100,
    valinit=0,
    orientation="vertical"
)
## Make a vertical slider to control the Flux
axflux = fig.add_axes([0.14, 0.25, 0.0225, 0.63])
FluxSlider = Slider(
    ax=axflux,
    label='Flux adjustment',
    valmin=0,
    valmax=10,
    valinit=1,
    orientation="vertical"
)
## The function to be called anytime a slider's value changes
global CurrentSliderVals
CurrentSliderVals = np.array([T_eV,T_eV_hot,Hot_ratio,1,0])
def update(val):
    # update plot
    ax.cla()
    ax.set_ylabel('Differential flux (H0 / cm2 eV s sr)')
    ax.set_xlabel('Energy (eV)')
    ax.plot(x_axis, ED_DF_sec_cm2, label='Experimental data')
    T_eV, T_eV_hot, MBF, MBF_hot = Maxwell_fitting.main(TOMAS_flux, ColdSlider.val, HotSlider.val, RatioSlider.val,FluxSlider.val,OffsetSlider.val)
    CurrentSliderVals[0] = ColdSlider.val
    CurrentSliderVals[1] = HotSlider.val
    CurrentSliderVals[2] = RatioSlider.val
    CurrentSliderVals[3] = FluxSlider.val
    CurrentSliderVals[4] = OffsetSlider.val
    MBF_total = MBF + MBF_hot
    
    #R^2
    Mean = 1/len(ED_DF_sec_cm2)*np.sum(ED_DF_sec_cm2)
    SSres = 0
    SStot = 0
    for x_axis_index,energy in enumerate(x_axis):
        if energy in E:
            SSres += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(MBF_total[np.where(np.isclose(E,energy))]))**2
            SStot += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(Mean))**2
    Rsquared = 1 - SSres/SStot

    ax.plot(E, MBF, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell with T={:#.5g} eV ({:#.4g} %)'.format(T_eV, (100 - RatioSlider.val)))
    ax.plot(E, MBF_hot, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell with T={:#.5g} eV ({:#.4g} %)'.format(T_eV_hot, RatioSlider.val))
    ax.plot(E, MBF_total, linestyle='-', linewidth=5, color='#1f77b4', alpha=0.5, label='Bi-maxwellian fitting with $R^2$={:#.4g}'.format(Rsquared[0]))
    ax.set_yscale('log')
    ax.set_xlim(left = 0, right = 750)
    ax.set_ylim(bottom = 1e7)#, top = 1e14)
    ax.legend()

# register the update function with each slider
ColdSlider.on_changed(update)
HotSlider.on_changed(update)
RatioSlider.on_changed(update)
FluxSlider.on_changed(update)
OffsetSlider.on_changed(update)

## Create a `matplotlib.widgets.Button` to reset the sliders to initial values.
resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
resetbutton = Button(resetax, 'Reset', hovercolor='0.975')

def reset(event):
    ColdSlider.reset()
    HotSlider.reset()
    RatioSlider.reset()
    FluxSlider.reset()
    OffsetSlider.reset()
resetbutton.on_clicked(reset)

## Create a `matplotlib.widgets.Button` to save the figure
locktax = fig.add_axes([0.5, 0.025, 0.1, 0.04])
lockbutton = Button(locktax, 'Lock values', hovercolor='0.975')

def lock(event):
    # update plot
    if CurrentSliderVals[3] != 1 or CurrentSliderVals[4] != 0:
        print(bcolors.WARNING + "Warning: adjusting the flux or energy offset might be unphysical and needs to be explained" + bcolors.ENDC)
    plt.close()
    plt.ylabel('Differential flux (H0 / cm2 eV s sr)')
    plt.xlabel('Energy (eV)')
    plt.plot(x_axis, ED_DF_sec_cm2, label='Experimental data')
    T_eV, T_eV_hot, MBF, MBF_hot = Maxwell_fitting.main(TOMAS_flux, CurrentSliderVals[0],CurrentSliderVals[1],CurrentSliderVals[2],CurrentSliderVals[3],CurrentSliderVals[4])
    MBF_total = MBF + MBF_hot

    #R^2
    Mean = 1/len(ED_DF_sec_cm2)*np.sum(ED_DF_sec_cm2)
    SSres = 0
    SStot = 0
    for x_axis_index,energy in enumerate(x_axis):
        if energy in E:
            SSres += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(MBF_total[np.where(np.isclose(E,energy))]))**2
            SStot += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(Mean))**2
    Rsquared = 1 - SSres/SStot

    plt.plot(E, MBF, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell with T={:#.5g} eV ({:#.4g} %)'.format(T_eV, (100 - RatioSlider.val)))
    plt.plot(E, MBF_hot, linestyle='-', linewidth=1, color='#1f77b4', alpha=0.5, label='Maxwell with T={:#.5g} eV ({:#.4g} %)'.format(T_eV_hot, RatioSlider.val))
    plt.plot(E, MBF_total, linestyle='-', linewidth=5, color='#1f77b4', alpha=0.5, label='Bi-maxwellian fitting with $R^2$={:#.4g}'.format(Rsquared[0]))
    plt.yscale('log')
    plt.xlim(left = 0, right = 750)
    plt.ylim(bottom = 1e7)#, top = 1e14)
    plt.legend()
    plt.show()

lockbutton.on_clicked(lock)


# Further figure adjustmens
ax.set_yscale('log')
ax.set_xlim(left = 0, right = 750)
ax.set_ylim(bottom = 1e7)#, top = 1e14)
ax.legend()
plt.show()

def SputteringCalc(target,Gas_type,x_axis,Diff_TOMAS_flux):
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
    for i,e in enumerate(x_axis):
        IndexOfClosest = tree.query(np.array([e,0]))[1] #get index of closest lying computed yield
        Yield = YieldMap[IndexOfClosest][2]
        fluxpersec = Diff_TOMAS_flux[i]*dE #Diff_TOMAS_flux is the flux/(cm^2 eV s),
                                 #multiplied by the energy bin we get the flux/(s cm^2)
        Sr += Yield*fluxpersec*10e6/(number_densities[target]) #devided by number density (in cm^3) we get the erosion rate in cm/s
    for i,e in enumerate(x_axis):
        E_avg += Diff_TOMAS_flux[i]*e
    E_avg = E_avg/(np.sum(Diff_TOMAS_flux))
    Sr = Sr*(10**7)*3600 #convert to nm/h
    return Sr

sputteringquestion = input('Do you want to calculate the sputtering rate based off these measurements? [y/n]')
if sputteringquestion == 'n':
    exit()
elif sputteringquestion == 'y':
        target = input(f"What is the target material? (e.g B, we're assuming the flux to be {Gas_type} as it has been troughout the analysis):")
        Sr = SputteringCalc(target,Gas_type,x_axis,Diff_TOMAS_flux)
        print("Neutral erosion rate: {} nm/h".format(Sr))
        SahaQuestion = input('Do you want a sputtering estimate for the ions, following the SAHA equations? (Not needed if RFEA measurements are available) this doesnt work yet [y/n]')
        if SahaQuestion == 'n':
            exit()
        elif SahaQuestion == 'y':
            def FluxRatio(P,E,species):
                
                Chi_H = 13.6 #eV
                c = 299792458 #m / s
                m_p = 938.27208943e6*c*c #eV
                m_e = 0.51099895069 #MeV/c^2
                h = 4.135667696e-15 #eV s
                k_b = 8.617333262e-5 #eV/K
                eV = 11604.525 #K
                mbar = 0.0009869232667160128 #atm 
                R = 8.20573660809596e-5 #m^3 atm (K mol)^-1
                V = 2*(np.pi**2)*0.78*(0.26**2) #m^3
                N_A = 6.02214076e23
                T = np.array(E)

                #ideal gas law P -> n:
                n = (P*mbar*V)/(R*T*eV)*N_A #/m^3

                Lambda_th = h/np.sqrt(2*np.pi*m_e*k_b*T*eV)

                if species == 'H':
                    A = (1/n)*((1/Lambda_th)**3)*np.exp(-1*Chi_H/(k_b*T*eV))
                return (-1*A + np.sqrt(A**2+4*A))/2
            #####################################################################
            #       Estimate ion flux from neutral flux using Saha equations    #
            #####################################################################
            P = float(input('Pressure before exposure (mbar): '))
            Diff_TOMAS_ion_flux = Diff_TOMAS_flux*FluxRatio(P,x_axis,Gas_type)
            IonSr = SputteringCalc(target,Gas_type,x_axis,Diff_TOMAS_ion_flux)
            print("Estimated erosion rate due to ions: {} nm/h".format(IonSr))
            print("Estimated total erosion rate: {} nm/h".format(IonSr+Sr))
            exit()
else:
    sys.exit(1)
