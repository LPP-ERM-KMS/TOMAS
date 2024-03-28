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


def main(TOMAS_flux, T_eV, T_eV_hot, Hot_ratio):

    # T_eV = T_eV # [eV]
    # T_eV_hot = T_eV_hot
    T_K = T_eV / K_to_eV # [K]
    T_K_hot = T_eV_hot / K_to_eV # [K]
    # Hot_ratio = Hot_ratio # [%]
    N_i = TOMAS_flux/(4*math.pi)
    
    # MBF = Maxwell Boltzmann distribution Fitting (or fitting Function)
    E = np.linspace(0, 725, 726) # [eV]
    MBF = list(N_i*(1-(Hot_ratio)*0.01)*2*math.sqrt(1/math.pi)*(1/(k_B_eV*T_K))**(3/2) * math.sqrt(i) * math.exp(-i/(k_B_eV*T_K)) for i in E)
    MBF_hot = list(N_i*(Hot_ratio*0.01)*2*math.sqrt(1/math.pi)*(1/(k_B_eV*T_K_hot))**(3/2) * math.sqrt(i) * math.exp(-i/(k_B_eV*T_K_hot)) for i in E)
    
    return (T_eV, T_eV_hot, MBF, MBF_hot)

def Fit(ED_DF_sec_cm2,TOMAS_flux, T_eV, T_eV_hot, Hot_ratio):
    res = minimize(FunctionToFit,x0 = [T_eV, T_eV_hot, Hot_ratio],args=(ED_DF_sec_cm2,TOMAS_flux))
    xf = res.x
    T_eV = xf[0]
    T_eV_hot = xf[1]
    Hot_ratio = xf[2]
    return T_eV, T_eV_hot , Hot_ratio

def FunctionToFit(x,ED_DF_sec_cm2,TOMAS_flux):
    T_eV = x[0]
    T_eV_hot = x[1]
    Hot_ratio = x[2]
    # T_eV = T_eV # [eV]
    # T_eV_hot = T_eV_hot
    T_K = T_eV / K_to_eV # [K]
    T_K_hot = T_eV_hot / K_to_eV # [K]
    # Hot_ratio = Hot_ratio # [%]
    N_i = TOMAS_flux/(4*math.pi)
    
    # MBF = Maxwell Boltzmann distribution Fitting (or fitting Function)
    E = np.linspace(0, 725, len(ED_DF_sec_cm2)) # [eV]
    MBF = list(N_i*(1-(Hot_ratio)*0.01)*2*math.sqrt(1/math.pi)*(1/(k_B_eV*T_K))**(3/2) * math.sqrt(i) * math.exp(-i/(k_B_eV*T_K)) for i in E)
    MBF_hot = list(N_i*(Hot_ratio*0.01)*2*math.sqrt(1/math.pi)*(1/(k_B_eV*T_K_hot))**(3/2) * math.sqrt(i) * math.exp(-i/(k_B_eV*T_K_hot)) for i in E)

    MBF_total = list(MBF[i] + MBF_hot[i] for i in range(len(MBF)))

    return np.sum(np.abs(np.array(ED_DF_sec_cm2[10:])-np.array(MBF_total[10:])))
