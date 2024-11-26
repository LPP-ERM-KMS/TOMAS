# This code allows manipulating three stepper motors (that are connected to the three capacitors of the TOMAS
# ICRH matching system).
# Connect the Arduino via USB and upload the program Steppermotors/scripts/TOMASstepper/TOMASsteppers.ino.
# The user can enter a string of the form A a P p S s to move capacitor A to positions a, etcetera. It is allowed to
# specify not all capacitors, and to specify the capacitors in a different order.
# The positions of the capacitors are stored in a file, in order to retrieve the positions when closing the program.
# Code to be used together with Arduino code.
# import sys
import argparse
import serial
import time
from Signalgenerator.scripts.AFG3252 import *
from DAQ.scripts.DAQtrigger import *
from GUI.GUI import *

parser = argparse.ArgumentParser() #Allow for local debugging
parser.add_argument("-d", "--debug", help="Debug flag if not running on TOMAS control PC")
args = parser.parse_args()

if not args.debug:
    # INITIALIZE THE ARDUINO

    Motors = ["A", "P", "S", "X", "Y", "Z"]

    # Create a serial object and specify the serial port that the Arduino is connected to, in this case COM5 on usb 
    # splitter python and Arduino communicate through this serial port.
    ArduinoUnoSerial = serial.Serial('COM4', 9600)



    # Check if the Arduino is connected
    print("Wait for message from Arduino:")

    print(ArduinoUnoSerial.readline().decode())

    # Read the positions of the capacitors from a file
    f = open("./Steppermotors/scripts/lastPosition.txt", "r+")
    pos = f.readlines()[-1]  # Read last line of file
    print("The Python starting positions are:")
    print(pos)

    # Communicate the last position to Arduino
    ArduinoUnoSerial.write(pos.encode())
    time.sleep(1)

    # Retrieve the position from Arduino as a cross-check

    ArdPos = ArduinoUnoSerial.readline()
    if "Error" in ArdPos.decode():
        f.close()
        # sys.exit(ArdPosPos.decode())
    print("The Arduino starting positions are:")
    print(ArdPos.decode())

    # Read the limits of the capacitors from a file and store them
    minPos = [0, 0, 0, 0, 0, 0]
    maxPos = [0, 0, 0, 0, 0, 0]
    fLim = open("./Steppermotors/scripts/limits.txt", "r+")
    limPos = fLim.readlines()[-1]
    print("The motor limits are:")
    print(limPos)
    limitStrs = limPos.split(" ")
    for i in range(0, len(limitStrs)):
        if limitStrs[i] in Motors:

            k = Motors.index(limitStrs[i])
            minPos[k] = limitStrs[i + 1]
            maxPos[k] = limitStrs[i + 2]
        
    print(minPos)
    # INITIALIZE THE SIGNAL GENERATOR

    # Make a connection to the function generator AFG 3252 (Tektronix) at the specified IP address
    dev = AFG3252('192.168.70.100')


    # INITIALIZE THE DAQ TRIGGER

    # Make a connection to the function generator AFG 3252 (Tektronix) at the specified IP address
    DAQtrig = DAQtrigger('192.168.70.200')
    # THE GUI

else:
    minPos=None
    maxPos=None
    pos=None
    ArduinoUnoSerial=None
    f=None
    fLim=None
    dev=None
    DAQtrig = None

TOMASGUI = GUI(minPos, maxPos, pos, ArduinoUnoSerial, f, fLim, dev, DAQtrig)
