# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 19:47:15 2021

@author: sunwoo
"""

def main(NPA_file, Laser_file):
    
    ##### Data load from data file         
    with open(NPA_file) as data:
        Ch0 = [i for i in data.readlines()]
        del Ch0[0:6]
        Ch0 = [[int(i) for i in Ch0[j].split()] for j in range(len(Ch0))]
    with open(Laser_file) as data:
        Ch1 = [i for i in data.readlines()]
        del Ch1[0:6]
        Ch1 = [[int(i) for i in Ch1[j].split()] for j in range(len(Ch1))]

    ###########################################################################
    ##### making one line for periodic time line 
    time_period_number_ch0 = 0
    time_period_number_ch1 = 0

    Ch0_raw = list(Ch0[i][0] for i in range(len(Ch0)))
    Ch1_raw = list(Ch1[i][0] for i in range(len(Ch1)))

    for i in range(1, len(Ch0)):
        if Ch0_raw[i] - Ch0_raw[i-1] < 0: time_period_number_ch0 += 1
        Ch0[i][0] += 2**32*time_period_number_ch0
    for i in range(1, len(Ch1)):
        if Ch1_raw[i] - Ch1_raw[i-1] < 0: time_period_number_ch1 += 1
        Ch1[i][0] += 2**32*time_period_number_ch1

    print(time_period_number_ch0, time_period_number_ch1)
    ###########################################################################

    """ delete useless (32-bit time) column """
    for i in range(len(Ch0)): del Ch0[i][2]
    for i in range(len(Ch1)): del Ch1[i][2]

    ##### Laser_signal smoothing
    import Laser_signal2
    Laser_timing = Laser_signal2.main(Ch1)
    
    ##### Mix of Ch0 (NPA) and Ch1 (Laser) 
    Ch = list([0,0,0] for i in range(len(Laser_timing)))
    for i in range(len(Laser_timing)):
        Ch[i][0] = Laser_timing[i]
        
    Ch.extend(Ch0)
        
    ##### sort by timing
    Ch.sort(key=lambda Ch:Ch[0])
    
    return(Ch, Ch0, Ch1)
