from pyRFtk import rfObject
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import numpy as np

def InOutToDb(x):
    return 10*np.log(x)

SMatrix = rfObject(touchstone='/home/arthur/PhD/Data/PhaseCalibration/TouchStoneFiles/3600.s3p')

Freqs = np.linspace(1E6,60E6)

plt.plot(Freqs/1e6,InOutToDb(np.abs(SMatrix.getS(Freqs))[:,0,0]),label='S11')
plt.plot(Freqs/1e6,InOutToDb(np.abs(SMatrix.getS(Freqs))[:,0,1]),label='S12')
plt.plot(Freqs/1e6,InOutToDb(np.abs(SMatrix.getS(Freqs))[:,0,2]),label='S13')
plt.ylabel('Loss (dB)')
plt.xlabel('MHz')
plt.legend()
plt.show()
