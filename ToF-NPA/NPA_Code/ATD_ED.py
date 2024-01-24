# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 01:54:04 2021

@author: sunwoo
"""

import matplotlib.pyplot as plt
import numpy as np
import ATD_ED

u = 1.66E-27 # [kg]
H_Mass = 1.008 * u
He_Mass = 4.002602 * u
ToF_D = 4.07 # [m]
eV = 1.60E-19 # [J]

##### Calculation of Neutral Particel (NP) Arrival Time (AT) with laser data 
def AT(Ch, Ch0, Unit_coeff):
    AT_data = [] 
    AT_energy = []
    AT_Position = []
    for i in range(len(Ch)):
        if Ch[i][1] != 0: # if there is NPA signal
            for j in range(1, 10):
                if Ch[i-j][1] == 0: # if the previous signal is laser 
                    AT_data.append((Ch[i][0] - Ch[i-j][0])/Unit_coeff) # NP arrival time from laser
                    AT_energy.append(Ch[i][1])
                    AT_Position.append(i)
                    break

    # Histogram of raw AT
    plt.figure(202)
    plt.title('Histogram of raw AT')
    AT_raw_hist = np.histogram(AT_data, 1001, range=(-0.5,999.5))
    AT_raw_hist_value = list(AT_raw_hist[0])
    AT_raw_hist_interval = list((AT_raw_hist[1][i]+AT_raw_hist[1][i+1])/2 for i in range(len(AT_raw_hist[1])-1))
    plt.plot(AT_raw_hist_interval, AT_raw_hist_value)
    plt.yscale('log')
    plt.show()

    # Histogram of AT
    AT_Histogram = np.histogram(AT_data, 145, range=(-0.5,144.5))
    AT_Histogram_value = list(AT_Histogram[0])
    AT_Histogram_interval = list((AT_Histogram[1][i]+AT_Histogram[1][i+1])/2 for i in range(len(AT_Histogram[1])-1))
    
    print ("AT reflection: Ch0({}), AT({}, {:.1f}%), AT_Hist({}, {:.1f}%):"
           .format(len(Ch0), len(AT_data), len(AT_data)/len(Ch0)*100, sum(AT_Histogram_value), sum(AT_Histogram_value)/len(Ch0)*100))

    # Why photon is broad: is it noise?
    AT_x = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 50, 100, 150, 155]
    AT_y = list(np.zeros(len(AT_x)))
    AT_z = list(np.zeros(len(AT_x)))
    for i in range(len(AT_data)):
        for j in range(len(AT_x)-1):
            if (AT_data[i] > AT_x[j] and AT_data[i] < AT_x[j+1]):
                AT_y[j] += AT_energy[i]
                AT_z[j] += 1
    AT_yz = list(AT_y[i]/AT_z[i] for i in range(len(AT_y)))
    
    plt.figure(201)
    plt.title('Check for broad photon peak')
    plt.plot(AT_x, AT_yz)
    plt.show()

    return (AT_data, AT_Histogram_value, AT_Histogram_interval)

##### Calculation of Energy distribution (ED) from AT 
def ED(AT_data, Gas_type):
    AT_nonzero = [i for i in AT_data if i != 0] # delete 0 
    if Gas_type == 'H': Mass = H_Mass
    if Gas_type == 'He': Mass = He_Mass
    ED_data = list(((1/2)*Mass*(ToF_D/(i*10**-6))**2)/eV for i in AT_nonzero)
    
    # Histogram of ED
    ED_Histogram = np.histogram(ED_data, 145, range=(5,730))
    ED_Histogram_value = list(ED_Histogram[0])
    ED_Histogram_interval = list((ED_Histogram[1][i]+ED_Histogram[1][i+1])/2 for i in range(len(ED_Histogram[1])-1))
    
    return (ED_data, ED_Histogram_value, ED_Histogram_interval)

##### Normalization of AT and ED / AT -> AT/sec, ED -> ED/sec
def Normalization(Ch, Ch0, Gas_type, Unit_coeff):
    Chx = list(Ch[i][1] for i in range(len(Ch)))
    Laser_first_NPA_position = min(np.where(np.array(Chx) > 0)[0])
    Laser_last_NPA_position = max(np.where(np.array(Chx) > 0)[0])

    Laser_counts = 0 
    for i in range(Laser_first_NPA_position, Laser_last_NPA_position):
        if Ch[i][1] == 0: # if there is no NPA signal, then it is laser signal
            Laser_counts += 1
   
    Laser_total_time_us = (Ch[Laser_last_NPA_position][0] - Ch[Laser_first_NPA_position][0]) / 1e6 # [µs]
    Laser_total_counts = Laser_total_time_us / 151.8
    Laser_normalization_coeff = 907.2 # 432 shots à 2.1s #perhaps norm for lost counts would be also good... 
    # Laser_counts / Laser_total_counts # % of laser signal in NPA signal period
    #the old one compensated by dividing of about 51% - but we want here the actual normalization (right?) 

    AT_data, AT_Histogram_value, AT_Histogram_interval = ATD_ED.AT(Ch, Ch0, Unit_coeff)
    ED_data, ED_Histogram_value, ED_Histogram_interval = ATD_ED.ED(AT_data, Gas_type)

    AT_Histogram_value_sec = list(i/Laser_normalization_coeff for i in AT_Histogram_value)
    ED_Histogram_value_sec = list(i/Laser_normalization_coeff for i in ED_Histogram_value)
    
    return (AT_Histogram_value_sec, ED_Histogram_value_sec)

