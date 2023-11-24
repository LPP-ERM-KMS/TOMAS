# vxi11 is a Python package that supports the VXI-11 Ethernet instrument control protocol
# for controlling VXI11 and LXI compatible instruments.
import vxi11
import time
import sys
import math
import numpy as np


# Class for the function generator AFG 3252 (Tektronix) that is used to trigger the DAQ (TEMPORARILY)
# The AFG commands can be found in the programmer manual at
# https://mmrc.caltech.edu/Tektronics/AFG3021B/AFG3021B%20Programmer%20Manual.pdf
class DAQtrigger:

    # Initializer. Host contains the IP address of the AFG. Make a connection to the instrument. Set channel 2 as
    # IC system, with a sinusoid output signal in dBm. Set channel 1 as EC system, with a DC output signal in Volt.
    def __init__(self, host):
        try:
            # Make a connection to the instrument with the specified IP address
            self.conn = vxi11.Instrument(host)
            # Ask the instrument for identification and print the response
            self.dType = self.conn.ask('*IDN?')
            print(self.dType)

            print('Setting Channel 1 (DAQ) to [V]')
            # 2-34) Disable the function generator output for channel 1
            self.conn.write('OUTP1:STAT OFF')
            # 2-62) Set the shape of the output waveform to DC
            self.conn.write('SOURCE1:FUNCTION DC')
            # 2-91) set the units of output amplitude to Volt
            self.conn.write('SOUR1:VOLT:UNIT V')

            print('Setting Channel 2 (DAQ) to [V]')
            # 2-34) Disable the function generator output for channel 1
            self.conn.write('OUTP2:STAT ON')
            # 2-62) Set the shape of the output waveform to DC
            self.conn.write('SOURCE2:FUNCTION DC')
            # 2-91) set the units of output amplitude to Volt
            self.conn.write('SOUR2:VOLT:UNIT V')

            
            # In order to trigger DAQ by labview, set the voltage amplitude to Vout=5.
            self.setDAQPowerFeed(5)  # V

        except Exception as e:
            print(e)
    
    # The DAQ system is triggered by sending a signal of Vout from channel 1 to the system
    # Set the power of channel 1 to Vout (where Vout is not limited to 0.5 V), with an offset of Vout/2.
    def setDAQPowerFeed(self, Vout):
        # if Vout>0.5:
        #    print('!!! Too high power  !!! ')
        #    print('Setting limit: 15 dBm')
        # Vout=-0.5
        # 2-88) Set the voltage amplitude to Vout
        self.conn.write('SOUR1:VOLT:AMPL {0}'.format(Vout))
        # 2-87) Set the voltage ofsett to Vout/2
        self.conn.write('SOUR1:VOLT:OFFSET {0}'.format(Vout / 2))

    def setECPower(self, Power):
        
        if float(Power)<1000:
            print("Note that for small wattage the power is non-linear, a best fit was made but check the DAQ")
            Power = np.log((Power - 664.442)/4.41317)/0.00432413 #Best Fit
                
        #The opamp used is calibrated and gives y=1.9944x + 0.0031 so
        #if a signal of 1V is given, roughly 2V comes out, after
        #this voltage goes to the EC antenna, this was also calibrated
        # from which Power=598.38V + 1.128 came
        
        Vout = ((Power - 1.128)/(598.38) - 0.0031)/1.9944
        Vout = (1193.32/1202.35)*Vout - (8.803/1202.35)
        # 2-88) Set the voltage amplitude to Vout, idk why it has to be done this way
        self.conn.write('SOUR2:VOLT:AMPL {0}'.format(Vout))
        self.conn.write('SOUR2:VOLT:OFFSET {0}'.format(Vout/2))


    def trigger(self):
        # 2-34) Enable the function generator output for channel 1
        self.conn.write('OUTP1:STAT ON')
        time.sleep(0.1)
        # 2-34) Disable the function generator output for channel 1
        self.conn.write('OUTP1:STAT OFF')

    def disconnect(self):
        self.conn.close()
        print("disconnected")
