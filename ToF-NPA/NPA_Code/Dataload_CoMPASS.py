# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 19:47:15 2021

@author: sunwoo
"""
import pandas as pd
import os
import matplotlib.pyplot as plt

def main(Ch0FilePath,Ch1FilePath):
    ##### Data load from data file         
    Ch0 = pd.read_csv(f'{Ch0FilePath}', sep = ';') # Ch0 (NPA)
    Ch1 = pd.read_csv(f'{Ch1FilePath}', sep = ';') # Ch1 (Laser)
    
    Ch0_timing = Ch0.TIMETAG.to_list()
    Ch0_signal = Ch0.ENERGY.to_list()
    Ch0_mix = list([Ch0_timing[i],Ch0_signal[i],0] for i in range(len(Ch0_timing)))
    Ch1_timing = Ch1.TIMETAG.to_list()

    ##### Laser_signal smoothing
    import Laser_signal_smooth
    Laser_timing, Laser_interval, Laser_check = Laser_signal_smooth.main(Ch1_timing)
    # Laser_timing = laser signal position
    # Laser_interval = interval between lasers in µs
    # Laser_check = (temporary variables) to check laser smoothing
    
    ##### Mix of Ch0 (NPA) and Ch1 (Laser) 
    Ch = list([0, 0, 0] for i in range(len(Laser_timing)))
    for i in range(len(Laser_timing)): # Laser data into Ch
        Ch[i][0] = Laser_timing[i]
        Ch[i][2] = Laser_check[i]
        
    Ch.extend(Ch0_mix) # Add NPA data to Ch
    Ch.sort(key=lambda Ch:Ch[0]) # Sort Ch by timing

    ##### (Temporary section)
    import numpy as np
    Ch_tmp = list(Ch)
    Unit_coeff = 1e6
    Ch_tmp_data = []
    Ch_tmp_energy = []
    Ch_tmp_Position = []
    Ch_tmp_check = []
    
    for i in range(len(Ch_tmp)):
        if Ch_tmp[i][1] != 0: # if there is NPA signal
            for j in range(1, 10):
                if Ch_tmp[i-j][1] == 0:
                    Ch_tmp_data.append((Ch_tmp[i][0] - Ch_tmp[i-j][0])/Unit_coeff) # NP arrival time from laser
                    Ch_tmp_energy.append(Ch_tmp[i][1])
                    Ch_tmp_check.append(Ch_tmp[i-j][2])
                    Ch_tmp_Position.append(i)
                    # print(i, Ch_tmp[i][0], Ch_tmp[i][1], Ch_tmp[i][2], Ch[i][2])
                    break

    Ch_tmp_Histogram = np.histogram(Ch_tmp_data, 1450, range=(-0.5,1440.5))
    Ch_tmp_Histogram_value = list(Ch_tmp_Histogram[0])
    Ch_tmp_Histogram_interval = list((Ch_tmp_Histogram[1][i]+Ch_tmp_Histogram[1][i+1])/2 for i in range(len(Ch_tmp_Histogram[1])-1))

    # Why photon is broad: is it noise?
    Ch_tmp_x = list(np.linspace(0, 200, 201))
    Ch_tmp_y = list(np.zeros(len(Ch_tmp_x)))
    Ch_tmp_yy = list(np.zeros(len(Ch_tmp_x)))
    Ch_tmp_z = list(np.zeros(len(Ch_tmp_x)))
    for i in range(len(Ch_tmp_data)):
        for j in range(len(Ch_tmp_x)-1):
            if (Ch_tmp_data[i] > Ch_tmp_x[j] and Ch_tmp_data[i] < Ch_tmp_x[j+1]):
                Ch_tmp_y[j] += Ch_tmp_energy[i]
                Ch_tmp_yy[j] += Ch_tmp_check[i]
                Ch_tmp_z[j] += 1
    Ch_tmp_yz = list(Ch_tmp_y[i]/Ch_tmp_z[i] for i in range(len(Ch_tmp_y)))
    Ch_tmp_yyz = list(Ch_tmp_yy[i]/Ch_tmp_z[i] for i in range(len(Ch_tmp_yy)))
    
    plt.figure(201)
    plt.title('For broad photon peak, average intensity')
    plt.plot(Ch_tmp_x, Ch_tmp_yz)
    plt.show()

    plt.figure(202)
    plt.title('For broad photon peak, type of laser timing')
    plt.plot(Ch_tmp_x, Ch_tmp_yyz)
    plt.show()
    
    plt.figure(203)
    plt.title('ATD')
    plt.plot(Ch_tmp_Histogram_interval[0:200], Ch_tmp_Histogram_value[0:200])
    plt.yscale('log')
    plt.show()

    return(Ch, Ch0_mix, Laser_timing, Laser_interval, Ch1_timing)


