def MinimizeableFunction(CVals):
    CpVal = CVals[0]
    CsVal = CVals[1]
    CaVal = CVals[2]

    print("Move capacitors to:")
    print("Cs: {CaVal}")
    print("Cp: {CpVal}")
    print("Ca: {CaVal}")

    Gamma = input("Enter Gamma after moving capacitors:")

    return Gamma


CRanges = input("Give Step ranges capacitors (seperated by commas)")
CVals = input("Give initial capacitor values in steps, seperated by commas:")
