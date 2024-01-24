# -*- coding: utf-8 -*-
"""
Created on Fri Jul 16 09:38:28 2021

@author: sunwoo
"""
# Histogram of Laser signal

import matplotlib.pyplot as plt
import numpy as np

def main(Laser_interval, Ch1_timing, Data_series):
    Laser_interval_histogram = np.histogram(Laser_interval, 501, range=(0,1200))
    Laser_interval_histogram_value = Laser_interval_histogram[0]
    Laser_interval_histogram_interval = list([(Laser_interval_histogram[1][i]+Laser_interval_histogram[1][i-1])/2] for i in range(1, len(Laser_interval_histogram[1])))

    Laser_interval_narrow_histogram = np.histogram(Laser_interval, 41, range=(130, 170))
    Laser_interval_narrow_histogram_value = Laser_interval_narrow_histogram[0]
    Laser_interval_narrow_histogram_interval = list([(Laser_interval_narrow_histogram[1][i]+Laser_interval_narrow_histogram[1][i-1])/2] for i in range(1, len(Laser_interval_narrow_histogram[1])))

    Laser_raw_interval=[]
    for i in range(1, len(Ch1_timing)):
        Laser_raw_interval.append((Ch1_timing[i]-Ch1_timing[i-1])/1e6)

    Laser_raw_histogram = np.histogram(Laser_raw_interval, 501, range=(0,1200))
    Laser_raw_histogram_value = Laser_raw_histogram[0]
    Laser_raw_histogram_interval = list([(Laser_raw_histogram[1][i]+Laser_raw_histogram[1][i-1])/2] for i in range(1, len(Laser_raw_histogram[1])))

    plt.figure(101)
    plt.title('Histogram of laser signal applied to ATD calculation')
    plt.ylabel('Counts')
    plt.xlabel('Time (µs)')
    plt.yscale('log')
    plt.plot(Laser_interval_narrow_histogram_interval, Laser_interval_narrow_histogram_value)
    plt.savefig('Laser_hist_{}.png'.format(Data_series), dpi=600)

    plt.figure(102)
    plt.title('Histogram of laser signal applied to ATD calculation')
    plt.ylabel('Counts')
    plt.xlabel('Time (µs)')
    plt.yscale('log')
    plt.xlim(left=0, right=1200)
    plt.plot(Laser_interval_histogram_interval, Laser_interval_histogram_value)
    plt.savefig('Laser_hist_{}.png'.format(Data_series), dpi=600)

    plt.figure(103)
    plt.title('Histogram of raw laser signal')
    plt.ylabel('Counts')
    plt.xlabel('Time (µs)')
    plt.yscale('log')
    plt.xticks(np.arange(0, int(Laser_raw_histogram_interval[len(Laser_raw_histogram_interval)-1][0]), 150))
    plt.plot(Laser_raw_histogram_interval, Laser_raw_histogram_value)
    plt.savefig('Laser_raw_hist_{}.png'.format(Data_series), dpi=600)

    return ()
