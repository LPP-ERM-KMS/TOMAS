import numpy as np

class Species:
    def __init__(self,labels,AtomicMasses,Charges,Concentrations):
        self.labels = labels
        self.A = AtomicMasses*931.4941e6*(299792458**2)  #in Dalton -> eV
        self.Q = Charges #in elementary charges (e = -1)
        self.C = Concentrations # relative, e.g (1,0.1,0.9) for e,H,D
        self.eps0 = 8.854e-12

class ColdPlasma:
    def __init__(self,omega,ne,ni,Te,Ti,B,species):
        self.omega = omega
        self.ne = ne
        self.ni = ni
        self.Te = Te
        self.Ti = Ti
        self.B = B
    def CyclotronFreq(q,B,m):
        return (q*B)/m
    def PlasmaFreq(label,q,n,m):
        index = self.labels.index("label")
        A = self.A[index]
        C = self.C[index]
        return np.sqrt((C*n)/(A*self.eps0)

