# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 19:42:58 2021

@author: sunwoo
"""

import math
##### Units and Coefficients 
e = 1.60217733 * 10**-19 # electron charge
u = 1.66E-27 # [kg]
H_Mass = 1.008 * u
He_Mass = 4.002602 * u
d = (5250-260)*10**-3 # flight distance
eV = 1.60E-19 # [J]
# d = (105 + 812.76 + 300 + 107)*10**-3 # [m] first tube from chamber + senconde tube to chopper + ToF tube + to detector 
# ToF_D = 3.82 # [m]

##### Geometry 
x_axis = [i for i in range(5, 730, 5)]
tau_totalopeningratio = (0.15*35.6*20) / (math.pi*(240/2-2.2)**2-math.pi*(160/2+2.2)**2) # opening time ratio [0]
tau_totalclosingratio = ((math.pi*(240/2)**2-math.pi*(160/2)**2)-0.15*35.6*20) / (math.pi*(240/2)**2-math.pi*(160/2)**2) # opening time ratio [0]
tau = tau_totalopeningratio*(1) # opening interval
dE = 5 # [eV] energy range corresponding to time resolution
Ad = 12*10*10**(-6) # Detector area m**2
As = 0.15*35.6*10**(-6) # Slit area m**2 (port CF35 diameter = 22 mm)
TOMAS_SolidAngle_vc = As/d**2 # Solid angle
SolidAngle_cd = Ad/d**2 # Solid angle

##### Quantum efficiency of Detector for Hydrogen 
Eta_Voss = list(9.69*10**(-4)*(x_axis[i]-14) for i in range(len(x_axis))) # Secondary emission cofficient (Voss)
Eta_Voss_fc = list(Eta_Voss[i]*0.745 for i in range(len(Eta_Voss))) # (Collection efficiency fc=0.745)
Eta = Eta_Voss_fc 
Eta[0] = 0.001
Eta[1] = (1-math.exp(-0.007))*0.25 # Secondary emission cofficient (Verbeek) for 10 eV
Eta[2] = (1-math.exp(-0.012))*0.25 


def main(ED_Histogram_value, Gas_type):
    ### Passing Probablity (PP) for Hydrogen ##################################
    if Gas_type == 'H':
        A1 = 1.0354 # 4.6366 # (14.332 for 1-4 mbar case)
        B1 = 0.496659 # 0.3657 # (0.2455 for 1-4 mbar case)
        C1 = 2.79
    if Gas_type == 'He':
        A1 = 10.3904 # (14.332 for 1-4 mbar case)
        B1 = 0.2785 # (0.2455 for 1-4 mbar case)
        C1 = -18.8149

    PP = [0 for i in range(145)]
    ED_PP = [0 for i in range(145)]

    for i in range(145):
        PP[i] = A1*(x_axis[i])**B1 + C1 # Power series fitting equation of PP results 
        ED_PP[i] = ED_Histogram_value[i] * 100 / PP[i] # Energy Distribution which has applied passing probability 

    ### Differential Flux (DF) ################################################ 
    ED_DF = list(ED_PP[i]/(Eta[i]*As*SolidAngle_cd*dE*tau_totalopeningratio) for i in range(len(ED_PP)))
    ED_DF_cm2 = list(ED_DF[i]/1e4 for i in range(len(ED_DF))) # DF / cm2
    return (ED_DF_cm2)

def totalflux(ED_DF_cm2):
    # ED_DF_cm2 = list(ED_DF[i]/1e4 for i in range(len(ED_DF))) # DF / cm2
    TOMAS_flux = 4*math.pi*sum(ED_DF_cm2 [1:145]*5)
    
    return (TOMAS_flux)
