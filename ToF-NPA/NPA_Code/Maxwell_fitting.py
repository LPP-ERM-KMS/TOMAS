# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 02:08:57 2021

@author: sunwoo
"""

import math
import numpy as np
from scipy.optimize import minimize 

##### constans ################################################################
e = 1.602E-19 # [C = A s]
k_B_eV = 8.617E-5 # [eV K^(-1)]
k_B_J = 1.381E-23 # [J K^(-1)]
R = 8.31446261815324 # gas constant [J K-1 mol-1 = kg m2 K−1 mol−1 s−2]
m_e = 9.109E-31 # [kg]
c = 2.998E8 # [m s^(-1)]

eV_to_J = 1.60217646E-19 # [J] = [kg m^2 s^-2]
K_to_eV = 0.00008617328149741 # [eV K-1]

###############################################################################

epsilon_0 = 8.854E-12 # [F m^(-1) = s^2 C^2 m^-2 kg^-1 = s^4 A^2 m^-2 kg^-1]

a_H0 = 1.008
a_H2 = 2*a_H0
a_He = 4.002602

amu = 1.66E-27 # [kg]
m_He = 4.002602 * amu # [kg]
m_H0 = a_H0 * amu # [kg]
m_H2 = 2*1.008 * amu # [kg]

mole = 6.02214076E23 # [particles]
M_H0 = a_H0 * 0.99999999965E-3 # [kg⋅mol^−1]
M_H2 = a_H2 * 0.99999999965E-3 # [kg⋅mol^−1]


def main(TOMAS_flux, T_eV, T_eV_hot, Hot_ratio,FluxAdjust=1,EnergyOffset=0):
    N_i = FluxAdjust*TOMAS_flux/(4*math.pi)
    
    # MBF = Maxwell Boltzmann distribution Fitting (or fitting Function)
    E = np.linspace(0, 725, 726) + EnergyOffset # [eV]
    MBF = MBFFunc(N_i,Hot_ratio,T_eV,E)
    MBF_hot = MBFFunc_hot(N_i,Hot_ratio,T_eV_hot,E)
    
    return (T_eV, T_eV_hot, MBF, MBF_hot)

def Fit(ED_DF_sec_cm2,TOMAS_flux, T_eV, T_eV_hot, Hot_ratio):
    res = minimize(FunctionToFit,x0 = [T_eV, T_eV_hot, Hot_ratio],args=(ED_DF_sec_cm2,TOMAS_flux))
    xf = res.x
    T_eV = xf[0]
    T_eV_hot = xf[1]
    Hot_ratio = xf[2]
    return T_eV,T_eV_hot,Hot_ratio

def MBFFunc(N_i,Hot_ratio,T_eV,e):
    T_K = T_eV / K_to_eV # [K]
    return N_i*(1-(Hot_ratio)*0.01)*2*np.sqrt(1/math.pi)*(1/(k_B_eV*T_K))**(3/2) * np.sqrt(e) * np.exp(-e/(k_B_eV*T_K))

def MBFFunc_hot(N_i,Hot_ratio,T_eV_hot,e):
    T_K_hot = T_eV_hot / K_to_eV # [K]
    return N_i*(Hot_ratio*0.01)*2*np.sqrt(1/math.pi)*(1/(k_B_eV*T_K_hot))**(3/2) * np.sqrt(e) * np.exp(-e/(k_B_eV*T_K_hot))

def FunctionToFit(x,ED_DF_sec_cm2,TOMAS_flux,startoffset=2,midpoint=20):
    T_eV, T_eV_hot, Hot_ratio = x
    E = np.linspace(0, 725, len(ED_DF_sec_cm2)) # [eV]
    x_axis = [i for i in range(5, 730,  5)]
    N_i = TOMAS_flux/(4*math.pi)
    MBF = MBFFunc(N_i,Hot_ratio,T_eV,E)
    MBF_hot = MBFFunc_hot(N_i,Hot_ratio,T_eV_hot,E)
    MBF_total = MBF + MBF_hot

    #R^2
    Mean = 1/len(ED_DF_sec_cm2)*np.sum(ED_DF_sec_cm2)
    SSres = 0
    SStot = 0
    for x_axis_index,energy in enumerate(x_axis):
        if energy in E:
            SSres += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(MBF_total[np.where(np.isclose(E,energy))]))**2
            SStot += (np.log(ED_DF_sec_cm2[x_axis_index]) - np.log(Mean))**2

    return abs(SSres/SStot)
