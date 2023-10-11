# we removed a 10 dB attenuator, the signal is now twice as strong

from AFG3252 import *
import time

print('Pulsed ECRH')
# Icoils=1450
# H2flow=15sccm

# IC power (when the power is off?)
PICoff = -30.0

# Set the power (for phase 1 of the experiment?)
# !! old MAX 7.9 dBm !!!
# Pphase1=13.9#  7.9dBm increase slowly from 0dBm in steps of 0.5bBm, few pulses per step
# Pphase1=15.9# MAXIMUM 7.9dBm increase slowly from 0dBm in steps of 0.5bBm, few pulses per step
Pphase1 = 4  # MAXIMUM 7.9 dBm (= 4.7 kW) increase slowly from 0dBm in steps of 0.5bBm, few pulses per step

# %% Make a connection to the function generator AFG 3252 (Tektronix) at the specified IP address
dev = AFG3252('192.168.70.100')
# Disable the function generator output for IC and EC
dev.disableOutputs()
# Set the power of IC to Poff
dev.setPowerIC(PICoff)  # dBm
# Set the IC frequency to a fixed frequency. The sweep is invalid
dev.setFixedFrequency(25e6)  # IC #
# Set the EC voltage amplitude to Vout=5 and the voltage ofsett to Vout/2
# Maja: What does this have to do with trigger? => Trigger labview for DAQ
dev.setTriggerEC(5)  # V

# tsettle=0.5  # pulse length
# sleep time during ...
tec = 0.5  # pulse length EC
# sleep time during ...
ticec = 3  # pulse length IC
# toff=ton*1*3 # wait time.
# sleep time during ...
toff = 2

# number of pulses
Npulses = 1

# wait one second to start the sequence
time.sleep(1)

# Index of first pulse
start = 1

for x in range(start, start + Npulses):
    # Set the IC voltage amplitude to Pphase1 (in dBm) and the voltage offset to 0 V, limited at 10 dBm.
    dev.setPowerIC(Pphase1)  # set requested power level
    print("pulse ", x, " of ", Npulses)  # Maja: Dependent on the value of start, this will give a confusing message.

    # Enable the EC function generator output
    dev.EC_enable()
    # Wait during tec seconds
    time.sleep(tec)
    # Enable the IC function generator output
    dev.IC_enable()  # Maja: Why not later?
    # Set requested power level
    # dev.setPowerIC(Pphase2)
    print("    ... EC")
    # Wait during tec seconds
    # time.sleep(tec)
    # Disable the EC function generator output
    dev.EC_disable()

    print("    ... IC")
    # Wait during ticec seconds
    time.sleep(ticec)
    # Disable the IC function generator output
    dev.IC_disable()  # IC off
    # Disable the IC and EC function generator output
    dev.disableOutputs()
    # Set the power of IC to Poff
    dev.setPowerIC(PICoff)  # set requested power level
    # Wait during toff seconds
    time.sleep(toff)  # pumping time / RF cooling time

dev.disableOutputs()
