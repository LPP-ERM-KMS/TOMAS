The file AFG3252 is used to communicate with the function generator AFG 3252 (Tektronix). The AFG3252 class contains functions that handle the operation of the AFG through code-specific commands.

The file pulsedECIC.py uses the AFG3252 class to generate a number of consecutive EC and IC pulses.

The file ICfreqmatching.py uses the AFG3252 class to sweep an IC frequency range. This can be used to determine at which frequency the minimal reflection coefficient occurs. The capacitors of the ICRH matching system have to be manipulated such that the minimal reflection coefficient occurs at the desired frequency.
