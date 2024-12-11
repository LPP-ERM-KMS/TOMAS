import numpy as np

def DirCoupler(V,Vf,Vr,GAmp,GPhase,FREQ,probeindexA=None,probeindexB=None,probeindexC=None):

    #phase shift
    c = 299792458
    rho = GAmp
    phi =  GPhase

    Gamma = rho*np.exp(1j*(phi)) 

    Beta = 2*np.pi*FREQ/(c)
    BetaL3 = Beta*(2.585+0.25)
    phi = -1*phi - 2*BetaL3 #phase transform from Dir coupler to load

    Gamma = rho*np.exp(1j*(phi))

    u = Gamma.real
    v = Gamma.imag
    
    EpsG = u**2 + v**2 + u
    EpsB = v

    return -1*EpsG,-1*EpsB 

def Algo3V(V,Vf,Vr,GAmp,GPhase,FREQ,probeindexA=0,probeindexB=1,probeindexC=3):

    Ai = probeindexA
    Bi = probeindexB
    Ci = probeindexC

    # Get voltages at positions in Measurepoints:
    MeasurePoints = np.array([0.235,0.895,1.69,2.35])

    #constants:
    c = 299792458
    Beta = 2*np.pi*FREQ/(c)
    S = np.sin(2*Beta*MeasurePoints) #array
    C = np.cos(2*Beta*MeasurePoints) #array
    SABBC = (S[Ai] - S[Bi])/(S[Bi] - S[Ci])
    CABBC = (C[Ai] - C[Bi])/(C[Bi] - C[Ci])

    Vs = (V/Vf)**2

    udenom = 2*(C[Bi]-C[Ci])*(CABBC - SABBC)
    vdenom = 2*(S[Bi]-S[Ci])*(CABBC - SABBC)

    u = ((Vs[Ai] - Vs[Bi]) - (Vs[Bi] - Vs[Ci])*SABBC)/udenom
    v = ((Vs[Ai] - Vs[Bi]) - (Vs[Bi] - Vs[Ci])*CABBC)/vdenom
    
    EpsG = u**2 + v**2 + u
    EpsB = v

    return -1*EpsG,-1*EpsB

def Algo4V(V,Vf,Vr,GAmp,GPhase,FREQ,probeindexA=None,probeindexB=None,probeindexC=None):
    ######################################
    # Calculate new values of Cs and Cp  #
    ######################################

    # Get voltages at positions in Measurepoints:
    MeasurePoints = np.array([0.235,0.895,1.69,2.35])

    #constants:
    c = 299792458
    lam = FREQ/(c)

    beta = 2*np.pi*lam
    S = np.sin(2*beta*MeasurePoints) #array
    C = np.cos(2*beta*MeasurePoints) #array

    BigS = (S[0] - S[1])/(S[2] - S[3])
    BigC = (C[0] - C[1])/(C[2] - C[3])

    Vs = (V**2)/(Vf**2)

    u = (1/2)*((Vs[0] - Vs[1]) - (Vs[2] - Vs[3])*BigS)/((C[2] - C[3])*(BigC - BigS))
    v = (1/2)*((Vs[0] - Vs[1]) - (Vs[2] - Vs[3])*BigC)/((S[2] - S[3])*(BigC - BigS))
    
    denom = (1+u**2) + v**2

    EpsG = (u**2 + v**2 + u)/denom
    EpsB = (v)/denom

    return -1*EpsG,-1*EpsB

def Algo2V(V,Vf,Vr,GAmp,GPhase,FREQ,probeindexA=0,probeindexB=2,probeindexC=None):
    ######################################
    # Calculate new values of Cs and Cp  #
    ######################################

    A = ProbeIndexA
    B = ProbeIndexB

    # Get voltages at positions in Measurepoints:
    MeasurePoints = np.array([0.235,0.895,1.69,2.35])

    #constants:
    c = 299792458
    beta = 2*np.pi*FREQ/c
    S = np.sin(2*beta*MeasurePoints) #array
    C = np.cos(2*beta*MeasurePoints) #array
    BigS = (S[0] - S[1])/(S[2] - S[3])
    BigC = (C[0] - C[1])/(C[2] - C[3])


    EpsB = (V[A] - Vf)*S[B] - (V[B] - Vf)*S[A]
    EpsG = (V[A] - Vf)*C[B] - (V[B] - Vf)*C[A]

    return -1*EpsG,EpsB
