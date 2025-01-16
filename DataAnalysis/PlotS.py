from pyRFtk import rfObject
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np

def InOutToDb(x):
    return 10*np.log(x)

SMatrix = rfObject(touchstone='/home/arthur/PhD/Projects/TOMAS_ICRH_Auto_Matching/Simulations/Ansys/TOMAS_plasma_box_HFSSDesign9_test.s2p')

Freqs = np.linspace(1E6,55E6,400)

plt.plot(Freqs/1e6,InOutToDb(np.abs(SMatrix.getS(Freqs))[:,0,0]),label='S11')
plt.plot(Freqs/1e6,InOutToDb(np.abs(SMatrix.getS(Freqs))[:,0,1]),label='S12')
plt.ylabel('Loss (dB)')
plt.xlabel('MHz')
plt.xlim([10,50])
plt.legend()
plt.title("TOMAS ICRF antenna scattering matrix simulated using HFSS")
plt.show()
