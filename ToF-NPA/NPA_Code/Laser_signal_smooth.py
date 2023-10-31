# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 21:10:19 2021

@author: sunwoo
"""

import numpy as np

##### Laser timing selection 
def main(Ch1_timing):

    Laser_interval=[]
    Laser_timing=[]
    Laser_check=[]
    
    timing_interval = 0
    laser_position = 1
    laser_suitable = 0
    
    while laser_position < len(Ch1_timing):    
        timing_interval = 0
        laser_neighbors = 0
        laser_missing = 0

        while timing_interval < 150.5 or timing_interval > 153:
            if laser_position + laser_neighbors > len(Ch1_timing)-6: # stop the loop at the end of the loop
                laser_position += 5
                laser_suitable = 1 # not suitable
                break
            
            timing_interval += (Ch1_timing[laser_position + laser_neighbors] 
                                - Ch1_timing[laser_position + laser_neighbors - 1])/1e6
            laser_neighbors += 1

            if timing_interval > 153: 
                laser_missing = round(timing_interval / 151.8, 1)
                if np.mod(laser_missing, 1) < 0.1: 
                    Laser_interval.append(timing_interval)
                    Laser_timing.append(Ch1_timing[laser_position])
                    Laser_check.append(laser_neighbors)
                    laser_position += (laser_neighbors)
                
            if laser_neighbors > 6: # when the neighbors are too many the loop will be stoped
                laser_suitable = 1
                break

        if laser_suitable == 0: # Add laser time and interval to new and smoothed laser series
            Laser_interval.append(timing_interval)
            Laser_timing.append(Ch1_timing[laser_position])
            Laser_check.append(laser_neighbors)
            laser_position += laser_neighbors

        if laser_suitable == 1: # Countinue to next
            laser_position += 1
            laser_suitable = 0
   
    return (Laser_timing, Laser_interval, Laser_check)
