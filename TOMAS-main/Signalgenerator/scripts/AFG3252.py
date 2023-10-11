# This script contains the class for the function generator AFG3252.

# vxi11 is a Python package that supports the VXI-11 Ethernet instrument control protocol
# for controlling VXI11 and LXI compatible instruments.
import vxi11
import time
import sys


# Class for the function generator AFG 3252 (Tektronix)
# The AFG commands can be found in the programmer manual at
# https://mmrc.caltech.edu/Tektronics/AFG3021B/AFG3021B%20Programmer%20Manual.pdf
class AFG3252:

    # Initializer. Host contains the IP address of the AFG. Make a connection to the instrument. Set channel 2 as
    # IC system, with a sinusoid output signal in dBm. Set channel 1 as EC system, with a DC output signal in Volt.
    def __init__(self, host):
        try:
            # Make a connection to the instrument with the specified IP address
            self.conn = vxi11.Instrument(host)
            # Ask the instrument for identification and print the response
            self.dType = self.conn.ask('*IDN?')
            print(self.dType)

            print('Setting Channel 1 (EC) to [V]')
            # 2-62) Set the shape of the output waveform to DC (Direct Current?)
            self.conn.write('SOURCE1:FUNCTION DC')
            # 2-91) set the units of output amplitude to Volt
            self.conn.write('SOUR1:VOLT:UNIT V')

            print('Setting Channel 2 (IC) to [dBm]')
            # 2-62) Set the shape of the output waveform to SINusoid
            self.conn.write('SOURCE2:FUNCTION SIN')
            # 2-91) set the units of output amplitude to dBm, i.e. decibels relative to one milliwatt
            self.conn.write('SOUR2:VOLT:UNIT DBM')
            
            # In order operate the EC generator a power of Vout=5 is fed to the EC generator
            self.setECPowerFeed(5)  # V

        except Exception as e:
            print(e)

# All Outputs
    
    def enableOutputs(self):
        # 2-34) Enable the function generator output for channel 1
        self.conn.write('OUTP1:STAT ON')
        # 2-34) Enable the function generator output for channel 2
        self.conn.write('OUTP2:STAT ON')
        
    def disableOutputs(self):
        # 2-34) Disable the function generator output for channel 1 and 2
        self.conn.write('OUTP1:STAT OFF')
        self.conn.write('OUTP2:STAT OFF')
           
# IC

    def IC_enable(self):
        # 2-34) Enable the function generator output for channel 2
        self.conn.write('OUTP2:STAT ON')

    def IC_disable(self):
        # 2-34) Disable the function generator output for channel 2
        self.conn.write('OUTP2:STAT OFF')
        
    # For the given channel, disable the frequency sweep and set the given frequency as fixed.
    def setICFixedFrequency(self, frequency):
        # 2-55) Set the frequency sweep state of channel ch to FIXed, which means
        # that the frequency is controlled by the FREQ:FIX command and the sweep is invalid.
        self.conn.write('SOUR2:FREQ:MODE FIX')
        print('Setting fixed frequency to {0}'.format(frequency))
        # 2-54) Set the output frequency of channel ch to the given frequency, when the Mode is set to other than Sweep
        self.conn.write('SOUR2:FREQ:FIX {0} Hz'.format(frequency))

    # Set the power of the IC system (channel 2) to Pout, where Pout is limited to 10 dBm and with an offset of 0 dBm.
    def setICPower(self, Pout):
        if Pout > 20:  # dBm
            print('!!! Too high power  !!! ')
            print('Setting limit: 10 dBm without 3rd attenuator')
            Pout = 10
        # 2-88) Set the voltage amplitude to Pout
        self.conn.write('SOUR2:VOLT:AMPL {0}'.format(Pout))
        # 2-87) Set the voltage ofsett to 0 V
        self.conn.write('SOUR2:VOLT:OFFSET {0}'.format(0))

    # For channel 2 (IC), sweep the frequency range [fstart, fstop] in n steps. (Not used))
    def sweepICFreqStepsOnce(self, fstart, fstop, nsteps, wait):
        deltaf = round((float(fstop) - fstart) / nsteps)
        f = fstart
        for i in range(0, nsteps+1):
            self.setFixedFrequency(f)
            time.sleep(wait)
            f += deltaf

    def setICSweep(self, fstart, fstop, time):
        # 2-57) Set the start frequency of sweep
        self.conn.write('SOUR2:FREQ:STAR {}'.format(float(fstart)))
        # 2-52) Set the center frequency of sweep
        # self.conn.write('SOUR2:FREQ:CENT {}'.format((float(fstart)+float(fstop))/2.))
        # 2-58) Set the stop frequency of sweep
        self.conn.write('SOUR2:FREQ:STOP {}'.format(float(fstop)))
        # 2-82) Select linear or logarithmic spacing for the sweep.
        self.conn.write('SOUR2:SWE:SPAC LIN')

        # 2-83) Set the sweep time (this does not include hold time and return time).
        self.conn.write('SOUR2:SWE:TIME {}s'.format(float(time)))
        # 2-80) Set the sweep hold time, which is the time that the frequency must remain stable after stop frequency
        self.conn.write('SOUR2:SWE:HTIMe MIN')
        # 2-82) Set the sweep return time, which is the amount of time to go from stop frequency to start frequency.
        self.conn.write('SOUR2:SWE:RTIM MIN')

    # For channel 2 (IC), sweep the frequency range [fstart, fstop] in a continuous way and repeatedly.
    def sweepICFreqRepeatedly(self, fstart, fstop, time):
        # 2-15) Resets the trigger system
        # self.conn.write('ABORT')
        # Set the sweep settings
        self.setICSweep(fstart, fstop, time)
        # 2-55) Set the frequency sweep state to Sweep. By default, the sweep is repeatedly (i.e. auto mode)
        self.conn.write('SOUR2:FREQ:MODE SWE')
        # 2-81) Set the sweep mode to auto, such that the instrument outputs a sweep repeatedly.
        # (For manual, the instrument outputs one sweep when a trigger input is received.)
        self.conn.write('SOUR2:SWE:MODE AUTO')

    # For channel 2 (IC), sweep the frequency range [fstart, fstop] once, when a trigger is received
    def SweepICFreqOnceAtTrig(self, fstart, fstop, time):
        print("dev SweepICFreqOnceAtTrig")
        # Set the sweep settings
        self.setICSweep(fstart, fstop, time)
        # 2-55) Set the frequency sweep state to Sweep. By default, the sweep is repeatedly (i.e. auto)
        self.conn.write('SOUR2:FREQ:MODE SWE')
        # 2-81) Set the sweep mode to MANual, such that the instrument outputs 1 sweep when a trigger input is received
        # (For auto, the instrument outputs a sweep repeatedly)
        self.conn.write('SOUR2:SWE:MODE MAN')
        # self.conn.write('TRIG:SEQ IMM')
        self.conn.write('TRIG:SEQ:SOUR EXT')

    # Trigger, after doing SweepFreqOnceAtTrig() such that a frequency sweep will be performed
    def trigger(self):
        # 2-111) This command forces an immediate trigger event to occur. (Unclear why this did not trigger a frequncy sweep)
        # self.conn.write('TRIG:SEQ IMM')
        # 2-109) This command generates a trigger evemt
        self.conn.write('*TRG')

    def GetICOutputStatus(self):        
        # 2-34) Query the function generator output status for channel 2
        Status = self.conn.ask('OUTP2:STAT?')
        return Status

    def GetICPower(self):        
        # 2-88) Query the voltage amplitude
        Power = self.conn.ask('SOUR2:VOLT:AMPL?')
        return Power

    def GetICFreqMode(self):
        # 2-55) Query the frequency sweep state {CW|FIXed|SWEep}
        FreqMode = self.conn.ask('SOUR2:FREQ:MODE?')
        return FreqMode

    def GetICFreq(self):
        # 2-54) Query the output frequency
        Freq = self.conn.ask('SOUR2:FREQ:FIX?')
        return Freq
    
    def GetICSweepMode(self):
        # 2-81) Query the sweep mode {AUTO|MANual} i.e. repeatedly or upon trigger
        SweepMode = self.conn.ask('SOUR2:SWE:MODE?')
        return SweepMode

    def GetICSweepTime(self):
        # 2-83) Query the sweep time (this does not include hold time and return time).
        SweepTime = self.conn.ask('SOUR2:SWE:TIME?')
        return SweepTime
    
    def GetICSweepFreqStart(self):
        # 2-57) Query the start frequency of sweep
        FreqStart = self.conn.ask('SOUR2:FREQ:STAR?')
        return FreqStart
    
    def GetICSweepFreqStop(self):
        # 2-52) Query the stop frequency of sweep
        FreqStop = self.conn.ask('SOUR2:FREQ:STOP?')
        return FreqStop
        
# EC
    
    def EC_enable(self):
        # 2-34) Enable the function generator output for channel 1
        self.conn.write('OUTP1:STAT ON')

    def EC_disable(self):
        # 2-34) Disable the function generator output for channel 1
        self.conn.write('OUTP1:STAT OFF')
        
    # The EC system is turned on by sending a signal of Vout from channel 1 to the system
    # Set the power of channel 1 to Vout (where Vout is not limited to 0.5 V), with an offset of Vout/2.
    def setECPowerFeed(self, Vout):
        # if Vout>0.5:
        #    print('!!! Too high power  !!! ')
        #    print('Setting limit: 15 dBm')
        # Vout=-0.5
        # 2-88) Set the voltage amplitude to Vout
        self.conn.write('SOUR1:VOLT:AMPL {0}'.format(Vout))
        # 2-87) Set the voltage ofsett to Vout/2
        self.conn.write('SOUR1:VOLT:OFFSET {0}'.format(Vout / 2))
        
    def GetECOutputStatus(self):        
        # 2-34) Query the function generator output status for channel 2
        Status = self.conn.ask('OUTP1:STAT?')
        return Status
    
    def GetECPower(self):        
        # 2-88) Query the voltage amplitude
        Power = self.conn.ask('SOUR1:VOLT:AMPL?')
        return Power

    # Maja: The EC system is on source 1 !?
    # Was the intention to use this function to trigger DAQ??
    # Function not used
    # def setECramp(self, Voff, Vrip):
    #     # 2-91) set the unit of the output amplitude to Vpp (instead of dBm).
    #     self.conn.write('SOUR2:VOLT:UNIT VPP')
    #     # 2-62) Set the shape of the output waveform to RAMP
    #     self.conn.write('SOURCE2:FUNCTION RAMP')
    #     # 2-61) Set the symmetry of the ramp waveform from 0 to 100 percent
    #     self.conn.write('SOURCE2:FUNC:RAMP:SYM 90')
    #     # 2-88) Set the voltage amplitude to Vrip
    #     self.conn.write('SOUR2:VOLT:AMPL {0}'.format(Vrip))
    #     # 2-87) Set the voltage ofsett to Voff/2
    #     self.conn.write('SOUR2:VOLT:OFFSET {0}'.format(Voff / 2))
    #     # 2-63) Set the phase of the output waveform.
    #     self.conn.write('SOURCE2:PHAS:ADJ -135 deg')

