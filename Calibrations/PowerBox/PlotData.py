from lvm_read import read
import numpy as np
import matplotlib.pyplot as plt

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

folder = 'meas6'
filename = 'logging_data_09_11_2023_16_46_33_1.LVM'
ToRead = folder + '/' + filename

data = read(ToRead)
X_Value = data[0]['data'][:,0]
Power = data[0]['data'][:,1]
LeftCutOff = find_nearest(X_Value,0.3544)
RightCutOff = find_nearest(X_Value,0.77)
Power = Power[LeftCutOff:RightCutOff]
X_Value = X_Value[LeftCutOff:RightCutOff]
plt.plot(X_Value,Power,label="Power")
plt.title(filename)
plt.xlabel("time (s)")
plt.ylabel("Voltage")
plt.legend()
plt.show()
