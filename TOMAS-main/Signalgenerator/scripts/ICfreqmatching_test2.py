from AFG3252 import *
import time


# Determine the IC frequency at time t during the sweep
def what_freq_at_t(t):
    return (frq_stop - frq_start) / sweep_time * t + frq_start


# Determine the time during the sweep, when a specific frequency is reached
def what_t_at_freq(fMHz):
    return (fMHz * 1e6 - frq_start) * (sweep_time / (frq_stop - frq_start))


print('IC matching')

# Make a connection to the function generator AFG 3252 (Tektronix) at the specified IP address
dev = AFG3252('192.168.70.100')

# IC power (when the power is off and on?)
Poff = -20.0
Pon = 0  # -10  # max 17

# Set parameters to sweep through an IC frequency range
frq_start = 1  # 24e6  # 20e6  # Start of the IC frequency range
frq_stop = 50  # 26e6  # 30e6  # End of the IC frequency range
sweep_time = 2  # Time to perform sweep
tec = 0.1  # time period that EC is turned on at 5 V, to trigger LabView DAQ

# Disable the function generator output for IC and EC
dev.disableOutputs()

# Perform the IC frequency sweeps continuously, over the range [frq_start, frq_stop], where every sweep takes sweep_time
# dev.sweepFreqRepeatedly(frq_start, frq_stop, sweep_time)

# Perform the IC frequency sweeps once when a trigger occurs, over the range [frq_start, frq_stop], where every sweep
# takes sweep_time
dev.SweepFreqOnceAtTrig(frq_start, frq_stop, sweep_time)

# Set the IC voltage amplitude to Pon (in dBm) and the voltage ofsett to 0 V, limited at 10 dBm.
dev.setPowerIC(Pon)  # dBm
# Enable the IC function generator output
dev.IC_enable()

# TODO: this should be done differently
# In order to trigger DAQ by labview, set the EC voltage amplitude to Vout=5.
# dev.setTriggerEC(5)  # V

for i in range(1):
    # Print the step
    print("step: {}".format(i))

    # Force an immediate trigger event to occur, such that one IC frequency sweep occurs
    dev.trigger()

    # TODO: triggering DAQ should be done differently. If you want to use the function below,
    # make sure that the sleeptimes add up to sweep_time.
    # Enable the EC function generator output during tec to trigger Labview DAQ
    # dev.EC_enable()
    # time.sleep(tec)
    # dev.EC_disable()

    time.sleep(sweep_time)

# Disable the function generator output for IC and EC
dev.disableOutputs()
# Set the power of IC to Poff
dev.setPowerIC(Poff)  # dBm


