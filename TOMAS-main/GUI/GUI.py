import tkinter as tk
import threading #making tk not freeze when moving probe
from pyRFtk import rfObject
from .MatchingAlgos import ModAlgo3V
import socket
import time
import numpy as np
from os.path import exists
from datetime import date
import os

class GUI(tk.Tk):
    def __init__(self, myminPos, mymaxPos, myPos, myArduino, myfile, myfileLim, myAFG, myDAQtrig):
        global Debug
        if not myDAQtrig: 
            Debug = True
            print("Debug Mode")
        else:
            Debug = False

        self.SuggestedCsVal = None
        self.SuggestedCpVal = None
        self.SuggestedCaVal = None

        self.minPos = myminPos
        self.maxPos = mymaxPos
        self.Pos = myPos
        self.arduino = myArduino
        self.f = myfile
        self.fLim = myfileLim
        
        self.dev = myAFG
        self.DAQtrig = myDAQtrig

        # Member variables for the IC output settings
        self.ICout = 1  # continuous
        self.ICoutPulsedOnTime = 0
        self.ICoutPulsedOffTime = 0
        self.ICoutPulsedNumber = 0
        self.ICoutPulsedStartTime = 0

        # Member variables for the EC output settings
        self.ECout = 1  # eiter 1 or 2, continuous or pulsed
        self.ECPower = 0 # indication of wattage
        self.ECoutPulsedOnTime = 0
        self.ECoutPulsedOffTime = 0
        self.ECoutPulsedNumber = 0
        self.ECoutPulsedStartTime = 0

        # Member variables for the routine       
       	self.ICvec = []
        self.ECvec = []
        self.timeStep = 0.1

        super().__init__()

        # MATCHING SYSTEM
        self.matching_frm = tk.Frame(self, borderwidth=15, bg="LightSteelBlue3")
        self.matching_lbl = tk.Label(self.matching_frm, text="Matching system", bg="LightSteelBlue3", font='helvetica 15 bold')

        self.lim_frm = tk.Frame(self.matching_frm, borderwidth=5, bg="LightSteelBlue3")
        self.lim_lbl = tk.Label(self.lim_frm, text="The capacitor limits are", bg="LightSteelBlue3")
        if not Debug:
            self.limA_lbl = tk.Label(self.lim_frm, text="A: [" + str(self.minPos[0]) + ", " + str(self.maxPos[0]) + "]",
                                 bg="LightSteelBlue3")
            self.limP_lbl = tk.Label(self.lim_frm, text="P: [" + str(self.minPos[1]) + ", " + str(self.maxPos[1]) + "]",
                                 bg="LightSteelBlue3")
            self.limS_lbl = tk.Label(self.lim_frm,
                                 text="S: [" + str(self.minPos[2]) + ", " + str(self.maxPos[2]).strip() + "]",
                                 bg="LightSteelBlue3")
        else:
            self.limA_lbl = tk.Label(self.lim_frm, text="A: DEBUG",
                                 bg="LightSteelBlue3")
            self.limP_lbl = tk.Label(self.lim_frm, text="P: DEBUG",
                                 bg="LightSteelBlue3")
            self.limS_lbl = tk.Label(self.lim_frm,text="S: DEBUG",
                                bg="LightSteelBlue3")

        self.findlim_frm = tk.Frame(self.matching_frm, borderwidth=5, bg="LightSteelBlue")
        self.findlim_lbl = tk.Label(self.findlim_frm, text="Find limits of capacitor:", bg="LightSteelBlue")
        self.findLimA = tk.IntVar()
        self.limA_chk = tk.Checkbutton(self.findlim_frm, variable=self.findLimA, text="A", bg="LightSteelBlue")
        self.findLimP = tk.IntVar()
        self.limP_chk = tk.Checkbutton(self.findlim_frm, variable=self.findLimP, text="P", bg="LightSteelBlue")
        self.findLimS = tk.IntVar()
        self.limS_chk = tk.Checkbutton(self.findlim_frm, variable=self.findLimS, text="S", bg="LightSteelBlue")
        self.findlim_btn = tk.Button(self.findlim_frm, text="Go!", bg="DarkSeaGreen4", command=self.findLimCap)

        self.pos_frm = tk.Frame(self.matching_frm, borderwidth=5, bg="LightSteelBlue3")
        self.pos_lbl = tk.Label(self.pos_frm, text="The capacitor positions are", bg="LightSteelBlue3")
        self.posA_lbl = tk.Label(self.pos_frm, bg="LightSteelBlue3")
        self.posP_lbl = tk.Label(self.pos_frm, bg="LightSteelBlue3")
        self.posS_lbl = tk.Label(self.pos_frm, bg="LightSteelBlue3")

        if not Debug:
            posStrs = self.Pos.split(" ")
            for i in range(0, len(posStrs)):
                if posStrs[i] == "A":
                    self.posA_lbl.config(text="A: " + posStrs[i + 1].strip())
                elif posStrs[i] == "P":
                    self.posP_lbl.config(text="P: " + posStrs[i + 1].strip())
                elif posStrs[i] == "S":
                    self.posS_lbl.config(text="S: " + posStrs[i + 1].strip())

        self.move_frm = tk.Frame(self.matching_frm, borderwidth=5, bg="LightSteelBlue")
        self.moveA_lbl = tk.Label(self.move_frm, text="Move capacitor A to:", bg="LightSteelBlue")
        self.moveA_entr = tk.Entry(self.move_frm, width=5)
        self.moveP_lbl = tk.Label(self.move_frm, text="Move capacitor P to:", bg="LightSteelBlue")
        self.moveP_entr = tk.Entry(self.move_frm, width=5)
        self.moveS_lbl = tk.Label(self.move_frm, text="Move capacitor S to:", bg="LightSteelBlue")
        self.moveS_entr = tk.Entry(self.move_frm, width=5)
        self.move_btn = tk.Button(self.move_frm, text="Go!", bg="DarkSeaGreen4", command=lambda: self.moveCap(None,None))

        self.scan_frm = tk.Frame(self.matching_frm, borderwidth=5, bg="LightSteelBlue")
        self.ICMatch_lbl = tk.Label(self.scan_frm, text="IC Matching System", bg="LightSteelBlue")

        self.ContinuousOrPulsed = tk.IntVar()
        self.MatchContinuous_btn = tk.Radiobutton(self.scan_frm, variable=self.ContinuousOrPulsed, value=1,text="Continuous EC",
                                       bg="LightSteelBlue")
        self.MatchPulsed_btn = tk.Radiobutton(self.scan_frm, variable=self.ContinuousOrPulsed, value=2, text="Pulsed EC",
                                       bg="LightSteelBlue")

        self.Steps_lbl = tk.Label(self.scan_frm, text="Steps:", bg="LightSteelBlue")
        self.Steps_entr = tk.Entry(self.scan_frm, width=5)
        self.ICMatchAut_btn = tk.Button(self.scan_frm, text="Go!", bg="DarkSeaGreen4", command=self.AutoMatching)

        self.exit_frm = tk.Frame(self.matching_frm, borderwidth=5, bg="LightSteelBlue3", pady=40)
        self.exit_btn = tk.Button(self.exit_frm, text="Exit", bg="LightPink3", command=self.escape)

        # GRID MATCHING SYSTEM
        self.matching_frm.grid(column=0, row=0, sticky="nsew")
        self.matching_lbl.grid(column=0, row=0, pady=10)

        self.lim_frm.grid(column=0, row=1, sticky="nsew")
        self.lim_lbl.grid(column=0, row=0, columnspan=4, rowspan=1, sticky="w")
        self.limA_lbl.grid(column=0, row=1, columnspan=4, sticky="w", padx=5)
        self.limP_lbl.grid(column=0, row=2, columnspan=4, sticky="w", padx=5)
        self.limS_lbl.grid(column=0, row=3, columnspan=4, sticky="w", padx=5)

        self.findlim_frm.grid(column=0, row=2, sticky="nsew")
        self.findlim_lbl.grid(column=0, row=0, columnspan=3, sticky="w", pady=5, padx=5)
        self.limA_chk.grid(column=0, row=1, padx=9)
        self.limP_chk.grid(column=1, row=1, padx=9)
        self.limS_chk.grid(column=2, row=1, padx=9)
        self.findlim_btn.grid(column=0, row=2, sticky="w")

        self.pos_frm.grid(column=0, row=3, sticky="nsew")
        self.pos_lbl.grid(column=0, row=0, columnspan=4, rowspan=1, sticky="w")
        self.posA_lbl.grid(column=0, row=1, columnspan=4, sticky="w", padx=5)
        self.posP_lbl.grid(column=0, row=2, columnspan=4, sticky="w", padx=5)
        self.posS_lbl.grid(column=0, row=3, columnspan=4, sticky="w", padx=5)

        self.move_frm.grid(column=0, row=4, sticky="nsew")
        self.moveA_lbl.grid(column=0, row=0, columnspan=2, sticky="w", pady=5, padx=5)
        self.moveA_entr.grid(column=2, row=0, padx=10)
        self.moveP_lbl.grid(column=0, row=1, columnspan=2, sticky="w", pady=5, padx=5)
        self.moveP_entr.grid(column=2, row=1, padx=10)
        self.moveS_lbl.grid(column=0, row=2, columnspan=2, sticky="w", pady=5, padx=5)
        self.moveS_entr.grid(column=2, row=2, padx=10)
        self.move_btn.grid(column=0, row=3, pady=5, sticky="w")

        self.scan_frm.grid(column=0, row=5, sticky="nsew", pady=10)
        self.ICMatch_lbl.grid(column=0, row=0, columnspan=3, rowspan=1, sticky="w")

        self.MatchContinuous_btn.grid(column=0, row=1, sticky="w")
        self.MatchPulsed_btn.grid(column=1, row=1, sticky="w")

        self.Steps_lbl.grid(column=0, row=2, sticky="w")
        self.Steps_entr.grid(column=1, row=2, sticky="w")
        self.ICMatchAut_btn.grid(column=4, row=2, sticky="w")

        self.exit_frm.grid(column=0, row=6, sticky="nsew")
        self.exit_btn.grid(column=0, row=11)

        # PROBES
        self.probe_frm = tk.Frame(self, borderwidth=15, bg="LightSteelBlue3")
        self.probe_lbl = tk.Label(self.probe_frm, text="Probes", bg="LightSteelBlue3", font='helvetica 15 bold')

        self.limProbe_frm = tk.Frame(self.probe_frm, borderwidth=5, bg="LightSteelBlue3")
        self.limProbe_lbl = tk.Label(self.limProbe_frm, text="The probe limits are", bg="LightSteelBlue3")

        if not Debug:
            self.limX_lbl = tk.Label(self.limProbe_frm,
                                text="Sample manipulator: [" + str(self.minPos[3]) + ", " + str(self.maxPos[3]) + "]",
                                bg="LightSteelBlue3")
            self.limY_lbl = tk.Label(self.limProbe_frm,
                                text="Triple Probe H: [" + str(self.minPos[4]) + ", " + str(self.maxPos[4]) + "]",
                                bg="LightSteelBlue3")
            self.limZ_lbl = tk.Label(self.limProbe_frm,
                                text="Vertical Probe V: [" + str(self.minPos[5]) + ", " + str(
                                         self.maxPos[5]).strip() + "]",
                                bg="LightSteelBlue3")
        else:
            self.limX_lbl = tk.Label(self.limProbe_frm,
                                text="Sample manipulator: Debug",
                                bg="LightSteelBlue3")
            self.limY_lbl = tk.Label(self.limProbe_frm,
                                text="Triple Probe H: Debug",
                                bg="LightSteelBlue3")
            self.limZ_lbl = tk.Label(self.limProbe_frm,
                                text="Vertical Probe V: Debug",
                                bg="LightSteelBlue3")


        self.findlimProbe_frm = tk.Frame(self.probe_frm, borderwidth=5, bg="LightSteelBlue")
        self.findlimProbe_lbl = tk.Label(self.findlimProbe_frm, text="Find limits of probes:", bg="LightSteelBlue")
        self.findLimX = tk.IntVar()
        self.limX_chk = tk.Checkbutton(self.findlimProbe_frm, variable=self.findLimX, text="Sample manipulator",
                                       bg="LightSteelBlue")
        self.findLimY = tk.IntVar()
        self.limY_chk = tk.Checkbutton(self.findlimProbe_frm, variable=self.findLimY, text="Triple Probe H",
                                       bg="LightSteelBlue")
        self.findLimZ = tk.IntVar()
        self.limZ_chk = tk.Checkbutton(self.findlimProbe_frm, variable=self.findLimZ, text="Triple Probe V",
                                       bg="LightSteelBlue")
        self.findlimProbe_btn = tk.Button(self.findlimProbe_frm, text="Go!", bg="DarkSeaGreen4", command=self.findLimProbe)

        self.posProbe_frm = tk.Frame(self.probe_frm, borderwidth=5, bg="LightSteelBlue3")
        self.posProbe_lbl = tk.Label(self.posProbe_frm, text="The probe positions are",
                                     bg="LightSteelBlue3")
        self.posX_lbl = tk.Label(self.posProbe_frm, bg="LightSteelBlue3")
        self.posY_lbl = tk.Label(self.posProbe_frm, bg="LightSteelBlue3")
        self.posZ_lbl = tk.Label(self.posProbe_frm, bg="LightSteelBlue3")

        if not Debug:
            posStrs = self.Pos.split(" ")
            for i in range(0, len(posStrs)):
                if posStrs[i] == "X":
                    self.posX_lbl.config(text="Sample manipulator: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Y":
                    self.posY_lbl.config(text="Triple Probe H: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Z":
                    self.posZ_lbl.config(text="Triple Probe V: " + posStrs[i + 1].strip())

        self.moveProbe_frm = tk.Frame(self.probe_frm, borderwidth=5, bg="LightSteelBlue")
        self.moveX_lbl = tk.Label(self.moveProbe_frm, text="Move Sample manipulator to:", bg="LightSteelBlue")
        self.moveX_entr = tk.Entry(self.moveProbe_frm, width=5)
        self.moveY_lbl = tk.Label(self.moveProbe_frm, text="Move Triple Probe H to:", bg="LightSteelBlue")
        self.moveY_entr = tk.Entry(self.moveProbe_frm, width=5)
        self.moveZ_lbl = tk.Label(self.moveProbe_frm, text="Move Triple Probe V to:", bg="LightSteelBlue")
        self.moveZ_entr = tk.Entry(self.moveProbe_frm, width=5)
        self.moveProbe_btn = tk.Button(self.moveProbe_frm, text="Go!", bg="DarkSeaGreen4", command=self.moveProbeMultithreading)

        self.scanProbe_frm = tk.Frame(self.probe_frm, borderwidth=5, bg="LightSteelBlue")
        self.scanXYZ_lbl = tk.Label(self.scanProbe_frm, text="Scan positions of:", bg="LightSteelBlue")
        # self.varscanXYZ = tk.IntVar()
        # self.scanX_chk = tk.Radiobutton(self.scanProbe_frm, text="Sample manipulator", variable=self.varscanXYZ, value=1, bg="LightSteelBlue3")
        # self.scanY_chk = tk.Radiobutton(self.scanProbe_frm, text="Triple Probe H", variable=self.varscanXYZ, value=2, bg="LightSteelBlue3")
        # self.scanZ_chk = tk.Radiobutton(self.scanProbe_frm, text="Triple Probe V", variable=self.varscanXYZ, value=3, bg="LightSteelBlue3")
        self.varscanXYZ = tk.StringVar()
        self.varscanXYZ.set("Sample manipulator")  # default value
        self.scanXYZ_opt = tk.OptionMenu(self.scanProbe_frm, self.varscanXYZ, "Sample manipulator", "Triple Probe H", "Triple Probe V")
        self.scanXYZ_opt.config(bg="white")
        self.scanXYZ_opt["menu"].config(bg="white")

        self.scanFrom_lbl = tk.Label(self.scanProbe_frm, text="from position ", bg="LightSteelBlue")
        self.scanFrom_entr = tk.Entry(self.scanProbe_frm, width=5)
        self.scanTo_lbl = tk.Label(self.scanProbe_frm, text=" to position ", bg="LightSteelBlue")
        self.scanTo_entr = tk.Entry(self.scanProbe_frm, width=5)
        self.scanStep_lbl = tk.Label(self.scanProbe_frm, text=" with step ", bg="LightSteelBlue")
        self.scanStep_entr = tk.Entry(self.scanProbe_frm, width=5)

        self.scanRoutine_lbl = tk.Label(self.scanProbe_frm, text="and perform ", bg="LightSteelBlue")
        self.scanDoIC = tk.IntVar()
        self.scanDoIC_chk = tk.Checkbutton(self.scanProbe_frm, variable=self.scanDoIC, text="IC", bg="LightSteelBlue")
        self.scanDoEC = tk.IntVar()
        self.scanDoEC_chk = tk.Checkbutton(self.scanProbe_frm, variable=self.scanDoEC, text="EC", bg="LightSteelBlue")
        self.scanDoDAQ = tk.IntVar()
        self.scanDoDAQ_chk = tk.Checkbutton(self.scanProbe_frm, variable=self.scanDoDAQ, text="DAQ", bg="LightSteelBlue")
        self.scanRoutine_btn = tk.Button(self.scanProbe_frm, text="Go!", bg="DarkSeaGreen4", command=self.scanProbe)

        # GRID PROBE
        self.probe_frm.grid(column=1, row=0, sticky="nsew")
        self.probe_lbl.grid(column=0, row=0, pady=10)

        self.limProbe_frm.grid(column=0, row=1, sticky="nsew")
        self.limProbe_lbl.grid(column=0, row=0, columnspan=4, rowspan=1, sticky="w")
        self.limX_lbl.grid(column=0, row=1, columnspan=4, sticky="w", padx=5)
        self.limY_lbl.grid(column=0, row=2, columnspan=4, sticky="w", padx=5)
        self.limZ_lbl.grid(column=0, row=3, columnspan=4, sticky="w", padx=5)

        self.findlimProbe_frm.grid(column=0, row=2, sticky="nsew")
        self.findlimProbe_lbl.grid(column=0, row=0, columnspan=3, sticky="w", pady=5, padx=5)
        self.limX_chk.grid(column=0, row=1, padx=9)
        self.limY_chk.grid(column=1, row=1, padx=9)
        self.limZ_chk.grid(column=2, row=1, padx=9)
        self.findlimProbe_btn.grid(column=0, row=2, sticky="w")

        self.posProbe_frm.grid(column=0, row=3, sticky="nsew")
        self.posProbe_lbl.grid(column=0, row=0, columnspan=4, rowspan=1, sticky="w")
        self.posX_lbl.grid(column=0, row=1, columnspan=4, sticky="w", padx=5)
        self.posY_lbl.grid(column=0, row=2, columnspan=4, sticky="w", padx=5)
        self.posZ_lbl.grid(column=0, row=3, columnspan=4, sticky="w", padx=5)

        self.moveProbe_frm.grid(column=0, row=4, sticky="nsew")
        self.moveX_lbl.grid(column=0, row=0, columnspan=2, sticky="w", pady=5, padx=5)
        self.moveX_entr.grid(column=2, row=0, padx=10)
        self.moveY_lbl.grid(column=0, row=1, columnspan=2, sticky="w", pady=5, padx=5)
        self.moveY_entr.grid(column=2, row=1, padx=10)
        self.moveZ_lbl.grid(column=0, row=2, columnspan=2, sticky="w", pady=5, padx=5)
        self.moveZ_entr.grid(column=2, row=2, padx=10)
        self.moveProbe_btn.grid(column=0, row=3, pady=5, sticky="w")

        self.scanProbe_frm.grid(column=0, row=5, sticky="nsew", pady=10)
        self.scanXYZ_lbl.grid(column=0, row=0, columnspan=3, rowspan=1, sticky="w")
        self.scanXYZ_opt.grid(column=2, row=0, columnspan=2, rowspan=1, sticky="ew")
        # self.scanX_chk.grid(column=2, row=0, columnspan=2, rowspan=1, sticky="ew")
        # self.scanY_chk.grid(column=4, row=0, columnspan=1, rowspan=1, sticky="ew")
        # self.scanZ_chk.grid(column=5, row=0, columnspan=2, rowspan=1, sticky="ew")

        self.scanFrom_lbl.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)
        self.scanFrom_entr.grid(column=1, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)
        self.scanTo_lbl.grid(column=2, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)
        self.scanTo_entr.grid(column=3, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)
        self.scanStep_lbl.grid(column=4, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)
        self.scanStep_entr.grid(column=5, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)

        self.scanRoutine_lbl.grid(column=0, row=2, columnspan=2, rowspan=1, sticky="w")
        self.scanDoIC_chk.grid(column=1, row=2, columnspan=1, rowspan=1, sticky="ew")
        self.scanDoEC_chk.grid(column=2, row=2, columnspan=1, rowspan=1, sticky="ew")
        self.scanDoDAQ_chk.grid(column=3, row=2, columnspan=1, rowspan=1, sticky="ew")
        self.scanRoutine_btn.grid(column=0, row=3, columnspan=1, rowspan=1, sticky="w", pady=10)

        # IC SIGNAL GENERATOR
        self.IC_frm = tk.Frame(self, borderwidth=15, bg="LightSteelBlue3")
        self.IC_lbl = tk.Label(self.IC_frm, text="IC system", bg="LightSteelBlue3", font='helvetica 15 bold')

        self.ICpower_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue3")

        if not Debug:
            self.ICpower_lbl = tk.Label(self.ICpower_frm, text="The IC power is " + str(self.dev.GetICPower()), bg="LightSteelBlue3")
        else:
            self.ICpower_lbl = tk.Label(self.ICpower_frm, text="The IC power is Debug", bg="LightSteelBlue3")

        self.ICsetpower_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue")
        self.setICpower_lbl = tk.Label(self.ICsetpower_frm, text="Set IC power to: ", bg="LightSteelBlue")
        self.setICpower_entr = tk.Entry(self.ICsetpower_frm, width=5)
        self.setICpower_btn = tk.Button(self.ICsetpower_frm, text="Set!", bg="DarkSeaGreen4", command=self.setICPower)

        self.ICfreq_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue3")
        if not Debug:
            freqText = str(self.getICfreqText())
        else:
            freqText = "Debug"
        if "!!" in freqText:
            self.ICfreq_lbl = tk.Label(self.ICfreq_frm, text=freqText, bg="LightSteelBlue3", fg="red")
        else:
            self.ICfreq_lbl = tk.Label(self.ICfreq_frm, text=freqText, bg="LightSteelBlue3", fg="black")

        self.setICfreq_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue")
        self.setICfreq_lbl = tk.Label(self.setICfreq_frm, text="Fix IC frequency to: ", bg="LightSteelBlue")
        self.setICfreq_entr = tk.Entry(self.setICfreq_frm, width=5)
        self.setICfreq_btn = tk.Button(self.setICfreq_frm, text="Set!", bg="DarkSeaGreen4", command=self.setICfreq)

        self.setICsweFrom_lbl = tk.Label(self.setICfreq_frm, text="Sweep IC frequency from ", bg="LightSteelBlue")
        self.setICsweFrom_entr = tk.Entry(self.setICfreq_frm, width=5)
        self.setICsweTo_lbl = tk.Label(self.setICfreq_frm, text="to", bg="LightSteelBlue")
        self.setICsweTo_entr = tk.Entry(self.setICfreq_frm, width=5)
        self.setICsweTime_lbl = tk.Label(self.setICfreq_frm, text="during", bg="LightSteelBlue")
        self.setICsweTime_entr = tk.Entry(self.setICfreq_frm, width=5)

        self.setICsweMode_lbl = tk.Label(self.setICfreq_frm, text="Do the IC frequency sweep ", bg="LightSteelBlue")
        # varICswe = tk.IntVar()
        # self.ICsweModeR1 = tk.Radiobutton(self.setICfreq_frm, text="repeatedly", variable=varICswe, value=1, bg="LightSteelBlue")
        # self.ICsweModeR2 = tk.Radiobutton(self.setICfreq_frm, text="upon trigger", variable=varICswe, value=2, bg="LightSteelBlue")
        self.varICswe = tk.StringVar()
        self.varICswe.set("repeatedly")  # default value
        self.ICswe_opt = tk.OptionMenu(self.setICfreq_frm, self.varICswe, "repeatedly", "upon trigger")
        self.ICswe_opt.config(bg="white")
        self.ICswe_opt["menu"].config(bg="white")
        self.setICswe_btn = tk.Button(self.setICfreq_frm, text="Set!", bg="DarkSeaGreen4", command=self.setICswe)

        self.ICoutput_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue3")
        ICoutText = "The IC output is"
        if self.ICout == 1:
            ICoutText += " continuous"
        elif self.ICout == 2:
            ICoutText += " pulsed with " + str(self.ICoutPulsedNumber) + " pulses, starting at " + str(self.ICoutPulsedStartTime) + "\n with on time "+ str(self.ICoutPulsedOnTime) + " and off time " + str(self.ICoutPulsedOffTime)
        self.ICoutput_lbl = tk.Label(self.ICoutput_frm, text=ICoutText, bg="LightSteelBlue3")

        self.setICoutput_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue")
        self.setICout_lbl = tk.Label(self.setICoutput_frm, text="Set the IC ", bg="LightSteelBlue")
        self.varICout = tk.IntVar()
        self.ICoutCont_chk = tk.Radiobutton(self.setICoutput_frm, text="continuous ", variable=self.varICout, value=1, bg="LightSteelBlue")
        self.ICoutPulsed_chk = tk.Radiobutton(self.setICoutput_frm, text="pulsed: ", variable=self.varICout, value=2, bg="LightSteelBlue")

        self.ICoutPulsedNumber_lbl = tk.Label(self.setICoutput_frm, text="an amount of ", bg="LightSteelBlue")
        self.ICoutPulsedNumber_entr = tk.Entry(self.setICoutput_frm, width=5)
        self.ICoutPulsedStartTime_lbl = tk.Label(self.setICoutput_frm, text=" pulses starting at ", bg="LightSteelBlue")
        self.ICoutPulsedStartTime_entr = tk.Entry(self.setICoutput_frm, width=5)
        self.ICoutPulsedOnTime_lbl = tk.Label(self.setICoutput_frm, text="with on time ", bg="LightSteelBlue")
        self.ICoutPulsedOnTime_entr = tk.Entry(self.setICoutput_frm, width=5)
        self.ICoutPulsedOffTime_lbl = tk.Label(self.setICoutput_frm, text=" and off time", bg="LightSteelBlue")
        self.ICoutPulsedOffTime_entr = tk.Entry(self.setICoutput_frm, width=5)

        self.setICout_btn = tk.Button(self.setICoutput_frm, text="Set!", bg="DarkSeaGreen4", command=self.setICout)

        self.ICswitch_frm = tk.Frame(self.IC_frm, borderwidth=5, bg="LightSteelBlue")
       
        self.ICswitch_lbl = tk.Label(self.ICswitch_frm, text="The IC is on", bg="LightSteelBlue")
        self.ICswitch_btn = tk.Button(self.ICswitch_frm, text="disable IC!", bg="DarkSeaGreen4", command=self.ICswitch)
        if not Debug:
            ICstatus = str(self.dev.GetICOutputStatus())
        else:
            ICstatus = "ICstatus Debug"
        if ICstatus == "0":
            self.ICswitch_lbl.config(text="The IC is off")
            self.ICswitch_btn.config(text="Do IC!")
            
        self.ICtrig_lbl = tk.Label(self.ICswitch_frm, text=" \t \t If set to sweep upon trigger", bg="LightSteelBlue")
        self.ICtrig_btn = tk.Button(self.ICswitch_frm, text="Trigger!", bg="DarkSeaGreen4", command=self.ICtrigger)

        # GRID IC SIGNAL GENERATOR
        self.IC_frm.grid(column=2, row=0, sticky="nsew")
        self.IC_lbl.grid(column=0, row=0, sticky="nsew", pady=10)

        self.ICpower_frm.grid(column=0, row=1, sticky="nsew")
        self.ICpower_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")

        self.ICsetpower_frm.grid(column=0, row=2, sticky="nsew")
        self.setICpower_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")
        self.setICpower_entr.grid(column=1, row=0, columnspan=1, rowspan=1, sticky="w")
        self.setICpower_btn.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w")

        self.ICfreq_frm.grid(column=0, row=3, sticky="nsew")
        self.ICfreq_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")

        self.setICfreq_frm.grid(column=0, row=4, sticky="nsew")
        self.setICfreq_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")
        self.setICfreq_entr.grid(column=4, row=0, columnspan=1, rowspan=1, sticky="w")
        self.setICfreq_btn.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)

        self.setICsweFrom_lbl.grid(column=0, row=3, columnspan=5, rowspan=1, sticky="w")
        self.setICsweFrom_entr.grid(column=5, row=3, columnspan=1, rowspan=1, sticky="w")
        self.setICsweTo_lbl.grid(column=6, row=3, columnspan=1, rowspan=1, sticky="w")
        self.setICsweTo_entr.grid(column=7, row=3, columnspan=1, rowspan=1, sticky="w")
        self.setICsweTime_lbl.grid(column=8, row=3, columnspan=1, rowspan=1, sticky="w")
        self.setICsweTime_entr.grid(column=9, row=3, columnspan=1, rowspan=1, sticky="w")

        self.setICsweMode_lbl.grid(column=0, row=4, columnspan=5, rowspan=1, sticky="w")
        # self.ICsweModeR1.grid(column=1, row=4, columnspan=2, rowspan=1, sticky="w")
        # self.ICsweModeR2.grid(column=4, row=4, columnspan=2, rowspan=1, sticky="w")
        self.ICswe_opt.grid(column=5, row=4, columnspan=3, rowspan=1, sticky="w", pady=10)
        self.setICswe_btn.grid(column=0, row=5, columnspan=1, rowspan=1, sticky="w")

        self.ICoutput_frm.grid(column=0, row=7, sticky="nsew")
        self.ICoutput_lbl.grid(column=0, row=0, columnspan=5, rowspan=1, sticky="w")

        self.setICoutput_frm.grid(column=0, row=8, sticky="nsew")
        self.setICout_lbl.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w")
        self.ICoutCont_chk.grid(column=0, row=2, columnspan=2, rowspan=1, sticky="w")
        self.ICoutPulsed_chk.grid(column=0, row=4, columnspan=1, rowspan=1, sticky="w")

        self.ICoutPulsedNumber_lbl.grid(column=1, row=4, columnspan=2, rowspan=1, sticky="w")
        self.ICoutPulsedNumber_entr.grid(column=3, row=4, columnspan=1, rowspan=1, sticky="w")
        self.ICoutPulsedStartTime_lbl.grid(column=4, row=4, columnspan=2, rowspan=1, sticky="w")
        self.ICoutPulsedStartTime_entr.grid(column=6, row=4, columnspan=1, rowspan=1, sticky="w")
        self.ICoutPulsedOnTime_lbl.grid(column=1, row=5, columnspan=2, rowspan=1, sticky="w")
        self.ICoutPulsedOnTime_entr.grid(column=3, row=5, columnspan=1, rowspan=1, sticky="w")
        self.ICoutPulsedOffTime_lbl.grid(column=4, row=5, columnspan=2, rowspan=1, sticky="w")
        self.ICoutPulsedOffTime_entr.grid(column=6, row=5, columnspan=1, rowspan=1, sticky="w")

        self.setICout_btn.grid(column=0, row=6, columnspan=1, rowspan=1, sticky="w", pady=10)

        self.ICswitch_frm.grid(column=0, row=9, sticky="nsew", pady=10)
        self.ICswitch_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")
        self.ICswitch_btn.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)
        self.ICtrig_lbl.grid(column=1, row=0, columnspan=1, rowspan=1, sticky="w")
        self.ICtrig_btn.grid(column=1, row=1, columnspan=1, rowspan=1, sticky="e", pady=10)

        # EC SIGNAL GENERATOR
        self.EC_frm = tk.Frame(self, borderwidth=15, bg="LightSteelBlue3")
        self.EC_lbl = tk.Label(self.EC_frm, text="EC system", bg="LightSteelBlue3", font='helvetECa 15 bold')

        self.ECpower_frm = tk.Frame(self.EC_frm, borderwidth=5, bg="LightSteelBlue3")

        if not Debug:
            self.ECpower_lbl = tk.Label(self.ECpower_frm, text="The EC power is " + str(self.dev.GetECPower()), bg="LightSteelBlue3")
        else:
            self.ECpower_lbl = tk.Label(self.ECpower_frm, text="The EC power is Debug", bg="LightSteelBlue3")

        self.ECsetpower_frm = tk.Frame(self.EC_frm, borderwidth=5, bg="LightSteelBlue")
        self.setECpower_lbl = tk.Label(self.ECsetpower_frm, text="Set EC power to: ", bg="LightSteelBlue")
        self.setECpower_entr = tk.Entry(self.ECsetpower_frm, width=5)
        self.setECpower_btn = tk.Button(self.ECsetpower_frm, text="Set!", bg="DarkSeaGreen4", command=self.setECPower)

        self.ECoutput_frm = tk.Frame(self.EC_frm, borderwidth=5, bg="LightSteelBlue3")
        ECoutText = "The EC output is"
        if self.ECout == 1:
            ECoutText += " continuous"
        elif self.ECout == 2:
            ECoutText += " pulsed with " + str(self.ECoutPulsedNumber) + " pulses, starting at " + str(
                self.ECoutPulsedStartTime) + "\n with on time " + str(self.ECoutPulsedOnTime) + " and off time " + str(
                self.ECoutPulsedOffTime)
        self.ECoutput_lbl = tk.Label(self.ECoutput_frm, text=ECoutText, bg="LightSteelBlue3")

        self.setECoutput_frm = tk.Frame(self.EC_frm, borderwidth=5, bg="LightSteelBlue")
        self.setECout_lbl = tk.Label(self.setECoutput_frm, text="Set the EC ", bg="LightSteelBlue")
        self.varECout = tk.IntVar()
        self.ECoutCont_chk = tk.Radiobutton(self.setECoutput_frm, text="continuous ", variable=self.varECout, value=1,
                                            bg="LightSteelBlue")
        self.ECoutPulsed_chk = tk.Radiobutton(self.setECoutput_frm, text="pulsed: ", variable=self.varECout, value=2,
                                              bg="LightSteelBlue")

        self.ECoutPulsedNumber_lbl = tk.Label(self.setECoutput_frm, text="an amount of ", bg="LightSteelBlue")
        self.ECoutPulsedNumber_entr = tk.Entry(self.setECoutput_frm, width=5)
        self.ECoutPulsedStartTime_lbl = tk.Label(self.setECoutput_frm, text=" pulses starting at ", bg="LightSteelBlue")
        self.ECoutPulsedStartTime_entr = tk.Entry(self.setECoutput_frm, width=5)
        self.ECoutPulsedOnTime_lbl = tk.Label(self.setECoutput_frm, text="with on time ", bg="LightSteelBlue")
        self.ECoutPulsedOnTime_entr = tk.Entry(self.setECoutput_frm, width=5)
        self.ECoutPulsedOffTime_lbl = tk.Label(self.setECoutput_frm, text=" and off time", bg="LightSteelBlue")
        self.ECoutPulsedOffTime_entr = tk.Entry(self.setECoutput_frm, width=5)

        self.setECout_btn = tk.Button(self.setECoutput_frm, text="Set!", bg="DarkSeaGreen4", command=self.setECout)

        self.ECswitch_frm = tk.Frame(self.EC_frm, borderwidth=5, bg="LightSteelBlue")
        self.ECswitch_lbl = tk.Label(self.ECswitch_frm, text="The EC is on", bg="LightSteelBlue")
        self.ECswitch_btn = tk.Button(self.ECswitch_frm, text="disable EC!", bg="DarkSeaGreen4", command=self.ECswitch)
        if not Debug:
            ECstatus = str(self.dev.GetECOutputStatus())
        else: 
            ECstatus = "Debug ECstatus"
        if ECstatus == "0":
            self.ECswitch_lbl.config(text="The EC is off")
            self.ECswitch_btn.config(text="Do EC!")
        
        # GRID EC SIGNAL GENERATOR
        self.EC_frm.grid(column=3, row=0, sticky="nsew")
        self.EC_lbl.grid(column=0, row=0, sticky="nsew", pady=10)

        self.ECpower_frm.grid(column=0, row=1, sticky="nsew")
        self.ECpower_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")

        self.ECsetpower_frm.grid(column=0, row=2, sticky="nsew")
        self.setECpower_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")
        self.setECpower_entr.grid(column=1, row=0, columnspan=1, rowspan=1, sticky="w")
        self.setECpower_btn.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w")

        self.ECoutput_frm.grid(column=0, row=3, sticky="nsew")
        self.ECoutput_lbl.grid(column=0, row=0, columnspan=5, rowspan=1, sticky="w")

        self.setECoutput_frm.grid(column=0, row=4, sticky="nsew")
        self.setECout_lbl.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w")
        self.ECoutCont_chk.grid(column=0, row=2, columnspan=2, rowspan=1, sticky="w")
        self.ECoutPulsed_chk.grid(column=0, row=4, columnspan=1, rowspan=1, sticky="w")

        self.ECoutPulsedNumber_lbl.grid(column=1, row=4, columnspan=2, rowspan=1, sticky="w")
        self.ECoutPulsedNumber_entr.grid(column=3, row=4, columnspan=1, rowspan=1, sticky="w")
        self.ECoutPulsedStartTime_lbl.grid(column=4, row=4, columnspan=2, rowspan=1, sticky="w")
        self.ECoutPulsedStartTime_entr.grid(column=6, row=4, columnspan=1, rowspan=1, sticky="w")
        self.ECoutPulsedOnTime_lbl.grid(column=1, row=5, columnspan=2, rowspan=1, sticky="w")
        self.ECoutPulsedOnTime_entr.grid(column=3, row=5, columnspan=1, rowspan=1, sticky="w")
        self.ECoutPulsedOffTime_lbl.grid(column=4, row=5, columnspan=2, rowspan=1, sticky="w")
        self.ECoutPulsedOffTime_entr.grid(column=6, row=5, columnspan=1, rowspan=1, sticky="w")

        self.setECout_btn.grid(column=0, row=6, columnspan=1, rowspan=1, sticky="w", pady=10)

        self.ECswitch_frm.grid(column=0, row=5, sticky="nsew", pady=10)
        self.ECswitch_lbl.grid(column=0, row=0, columnspan=1, rowspan=1, sticky="w")
        self.ECswitch_btn.grid(column=0, row=1, columnspan=1, rowspan=1, sticky="w", pady=10)

        # DAQ
        self.DAQ_frm = tk.Frame(self, borderwidth=15, bg="LightSteelBlue3")
        self.DAQ_lbl = tk.Label(self.DAQ_frm, text="Data Acquisition", bg="LightSteelBlue3", font='helvetica 15 bold')

        self.DAQinfo_frm = tk.Frame(self.DAQ_frm, borderwidth=15, bg="LightSteelBlue")
        self.DAQfile_lbl = tk.Label(self.DAQinfo_frm, text="output file name", bg="LightSteelBlue")
        self.DAQfile_entr = tk.Entry(self.DAQinfo_frm, width=25)

        self.DAQinfo_lbl = tk.Label(self.DAQinfo_frm, text="Parameter info for output file", bg="LightSteelBlue")
        self.DAQfirstshot_lbl = tk.Label(self.DAQinfo_frm, text="First shot number", bg="LightSteelBlue")
        self.DAQfirstshot_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQlastshot_lbl = tk.Label(self.DAQinfo_frm, text="Last shot number", bg="LightSteelBlue")
        self.DAQlastshot_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQgasHe_lbl = tk.Label(self.DAQinfo_frm, text="He gasflow (sccm)", bg="LightSteelBlue")
        self.DAQgasHe_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQgasD_lbl = tk.Label(self.DAQinfo_frm, text="D gasflow (sccm)", bg="LightSteelBlue")
        self.DAQgasD_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQgasAr_lbl = tk.Label(self.DAQinfo_frm, text="Ar gasflow (sccm)", bg="LightSteelBlue")
        self.DAQgasAr_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQcoilI_lbl = tk.Label(self.DAQinfo_frm, text="Coil current (A)", bg="LightSteelBlue")
        self.DAQcoilI_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQTPbat_lbl = tk.Label(self.DAQinfo_frm, text="Triple probe battery (V)", bg="LightSteelBlue")
        self.DAQTPbat_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQVDiv_lbl = tk.Label(self.DAQinfo_frm, text="Voltage divider", bg="LightSteelBlue")
        self.DAQVDiv_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQECpol_lbl = tk.Label(self.DAQinfo_frm, text="EC polarisation", bg="LightSteelBlue")
        self.DAQECpol_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQcomment_lbl = tk.Label(self.DAQinfo_frm, text="Comment", bg="LightSteelBlue")
        self.DAQcomment_entr = tk.Entry(self.DAQinfo_frm, width=5)
        self.DAQwrite_btn = tk.Button(self.DAQinfo_frm, text="Write!", bg="DarkSeaGreen4", command=self.DAQwrite)
        self.doDAQ_frm = tk.Frame(self.DAQ_frm, borderwidth=15, bg="LightSteelBlue")
        self.doDAQ_lbl = tk.Label(self.DAQinfo_frm, text="Perform DAQ", bg="LightSteelBlue")
        self.doDAQ_btn = tk.Button(self.DAQinfo_frm, text="Go!", bg="DarkSeaGreen4", command=self.doDAQ)

        # GRID DAQ
        self.DAQ_frm.grid(column=4, row=0, sticky="nsew")
        self.DAQ_lbl.grid(column=0, row=0, pady=10, sticky="nsew")
        self.DAQinfo_frm.grid(column=0, row=1, sticky="nsew")
        self.DAQfile_lbl.grid(column=0, row=1, columnspan=4, rowspan=1, sticky="w")
        self.DAQfile_entr.grid(column=0, row=2, columnspan=4, rowspan=1, sticky="w")
        self.DAQinfo_lbl.grid(column=0, row=3, columnspan=1, rowspan=1, sticky="w")
        self.DAQfirstshot_lbl.grid(column=0, row=4, columnspan=1, rowspan=1, sticky="w")
        self.DAQfirstshot_entr.grid(column=1, row=4, columnspan=1, rowspan=1, sticky="w")
        self.DAQlastshot_lbl.grid(column=0, row=5, columnspan=1, rowspan=1, sticky="w")
        self.DAQlastshot_entr.grid(column=1, row=5, columnspan=1, rowspan=1, sticky="w")
        self.DAQgasHe_lbl.grid(column=0, row=6, columnspan=1, rowspan=1, sticky="w")
        self.DAQgasHe_entr.grid(column=1, row=6, columnspan=1, rowspan=1, sticky="w")
        self.DAQgasD_lbl.grid(column=0, row=7, columnspan=1, rowspan=1, sticky="w")
        self.DAQgasD_entr.grid(column=1, row=7, columnspan=1, rowspan=1, sticky="w")
        self.DAQgasAr_lbl.grid(column=0, row=8, columnspan=1, rowspan=1, sticky="w")
        self.DAQgasAr_entr.grid(column=1, row=8, columnspan=1, rowspan=1, sticky="w")
        self.DAQcoilI_lbl.grid(column=0, row=9, columnspan=1, rowspan=1, sticky="w")
        self.DAQcoilI_entr.grid(column=1, row=9, columnspan=1, rowspan=1, sticky="w")
        self.DAQTPbat_lbl.grid(column=0, row=10, columnspan=1, rowspan=1, sticky="w")
        self.DAQTPbat_entr.grid(column=1, row=10, columnspan=1, rowspan=1, sticky="w")
        self.DAQVDiv_lbl.grid(column=0, row=11, columnspan=1, rowspan=1, sticky="w")
        self.DAQVDiv_entr.grid(column=1, row=11, columnspan=1, rowspan=1, sticky="w")
        self.DAQECpol_lbl.grid(column=0, row=12, columnspan=1, rowspan=1, sticky="w")
        self.DAQECpol_entr.grid(column=1, row=12, columnspan=1, rowspan=1, sticky="w")
        self.DAQcomment_lbl.grid(column=0, row=13, columnspan=1, rowspan=1, sticky="w")
        self.DAQcomment_entr.grid(column=1, row=13, columnspan=1, rowspan=1, sticky="w")
        self.DAQwrite_btn.grid(column=0, row=14, columnspan=1, rowspan=1, sticky="w")
        
        self.doDAQ_frm.grid(column=0, row=2, sticky="nsew", pady=10)
        self.doDAQ_lbl.grid(column=0, row=15, columnspan=1, rowspan=1, sticky="w")
        self.doDAQ_btn.grid(column=0, row=16, columnspan=1, rowspan=1, sticky="w")

        # OPERATION
        self.operation_frm = tk.Frame(self, borderwidth=15, bg="LightSteelBlue3")
        self.OP_lbl = tk.Label(self.operation_frm, text="Routine", bg="LightSteelBlue3", font='helvetica 15 bold')
        self.OProutine_frm = tk.Frame(self.operation_frm, borderwidth=15, bg="LightSteelBlue")
        self.OPamount_lbl = tk.Label(self.OProutine_frm, text="Amount of routines:", bg="LightSteelBlue")
        self.OPamount_entr = tk.Entry(self.OProutine_frm, width=5)
        self.OPRoutine_lbl = tk.Label(self.OProutine_frm, text="Perform ", bg="LightSteelBlue")
        self.OPDoIC = tk.IntVar()
        self.OPDoIC_chk = tk.Checkbutton(self.OProutine_frm, variable=self.OPDoIC, text="IC", bg="LightSteelBlue")
        self.OPDoEC = tk.IntVar()
        self.OPDoEC_chk = tk.Checkbutton(self.OProutine_frm, variable=self.OPDoEC, text="EC", bg="LightSteelBlue")
        self.OPDoDAQ = tk.IntVar()
        self.OPDoDAQ_chk = tk.Checkbutton(self.OProutine_frm, variable=self.OPDoDAQ, text="DAQ", bg="LightSteelBlue")
        self.OP_btn = tk.Button(self.OProutine_frm, text="Go!", bg="DarkSeaGreen4", command=lambda: self.operation(None,None,None))
        
        # GRID OPERATION
        self.operation_frm.grid(column=5, row=0, sticky="nsew")
        self.OP_lbl.grid(column=0, row=0, pady=10, sticky="nsew")
        self.OProutine_frm.grid(column=0, row=1, sticky="nsew")
        self.OPamount_lbl.grid(column=0, row=1, columnspan=2, rowspan=1, sticky="w")
        self.OPamount_entr.grid(column=2, row=1, columnspan=1, rowspan=1, sticky="w")
        self.OPRoutine_lbl.grid(column=0, row=2, columnspan=4, rowspan=1, sticky="w")
        self.OPDoIC_chk.grid(column=1, row=2, columnspan=1, rowspan=1, sticky="w")
        self.OPDoEC_chk.grid(column=2, row=2, columnspan=1, rowspan=1, sticky="w")
        self.OPDoDAQ_chk.grid(column=3, row=2, columnspan=1, rowspan=1, sticky="w")
        self.OP_btn.grid(column=0, row=3, columnspan=1, rowspan=1, sticky="w")
  
    
        for i in range(6):
            self.columnconfigure(i, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.mainloop()

    def on_closing(self):
        self.DAQtrig.disconnect()
        self.destroy()
        
    def moveCap(self,CsM=None,CpM=None):

        if CsM and CpM:
            moveAto = None
            movePto = str(CpM)
            moveSto = str(CsM)
        else:
            moveAto = self.moveA_entr.get()
            movePto = self.moveP_entr.get()
            moveSto = self.moveS_entr.get()

        cmd = ""
        if moveAto:
            cmd += "A " + moveAto + " "
        if movePto:
            cmd += "P " + movePto + " "
        if moveSto:
            cmd += "S " + moveSto

        if cmd == "":
            print("Specify at least one position")
            return

        # Communicate the desired position to Arduino
        print("Instruct Arduino:")
        print(cmd)
        self.arduino.write(cmd.encode())
        time.sleep(2)

        # Retrieve communication from Arduino
        newPos = self.arduino.readline()
        if "Error" in newPos.decode():
            print(newPos.decode())
            # After the error, Arduino will communicate the new positions
            newPos = self.arduino.readline()
        print("The new positions are:")
        print(newPos.decode())
        self.f.write(newPos.decode().strip()+"\n")

        # Update the information on the GUI
        posStrs = newPos.decode().split(" ")
        for i in range(0, len(posStrs)):
            if posStrs[i] == "A":
                self.posA_lbl.config(text="A: " + posStrs[i + 1].strip())
            elif posStrs[i] == "P":
                self.posP_lbl.config(text="P: " + posStrs[i + 1].strip())
            elif posStrs[i] == "S":
                self.posS_lbl.config(text="S: " + posStrs[i + 1].strip())

        self.Pos = newPos.decode()
        self.moveA_entr.delete(0, 'end')
        self.moveP_entr.delete(0, 'end')
        self.moveS_entr.delete(0, 'end')

        self.update()

    def findLimCap(self):

        cmd = "limits "
        if self.findLimA.get():
            cmd += "A "
        if self.findLimP.get():
            cmd += "P "
        if self.findLimS.get():
            cmd += "S "

        if cmd == "limits ":
            print("Specify which capacitor(s)")
            return

        # Communicate the command to Arduino
        print("Instruct Arduino:")
        print(cmd)
        self.arduino.write(cmd.encode())
        time.sleep(2)

        # Retrieve communication from Arduino
        limitAPS = self.arduino.readline()
        if "Error" in limitAPS.decode():
            print(limitAPS.decode())
        else:
            print("The limits are:")
            print(limitAPS.decode())
            # Store limits. Strip removes the newline
            limitStrs = limitAPS.decode().split(" ")
            for i in range(0, len(limitStrs)):
                if limitStrs[i] == "A":
                    self.minPos[0] = limitStrs[i + 1].strip()
                    self.maxPos[0] = limitStrs[i + 2].strip()
                elif limitStrs[i] == "P":
                    self.minPos[1] = limitStrs[i + 1].strip()
                    self.maxPos[1] = limitStrs[i + 2].strip()
                elif limitStrs[i] == "S":
                    self.minPos[2] = limitStrs[i + 1].strip()
                    self.maxPos[2] = limitStrs[i + 2].strip()

            self.fLim.write(
                "A " + str(self.minPos[0]) + " " + str(self.maxPos[0]) + " P " + str(self.minPos[1]) + " " + str(self.maxPos[1]) + " S "
                + str(self.minPos[2]) + " " + str(self.maxPos[2]) + " X " + str(self.minPos[3]) + " " + str(self.maxPos[3]) + " Y " +
                str(self.minPos[4]) + " " + str(self.maxPos[4]) + " Z "
                + str(self.minPos[5]) + " " + str(self.maxPos[5]))
            # Make sure the information is written and stored in the file right away
            self.fLim.flush()
            os.fsync(self.fLim)

            # Update the information on the GUI
            self.limA_lbl.config(text="A: [" + str(self.minPos[0]) + ", " + str(self.maxPos[0]) + "]")
            self.limP_lbl.config(text="P: [" + str(self.minPos[1]) + ", " + str(self.maxPos[1]) + "]")
            self.limS_lbl.config(text="S: [" + str(self.minPos[2]) + ", " + str(self.maxPos[2]).strip() + "]")

            self.findLimA.set(0)
            self.findLimP.set(0)
            self.findLimS.set(0)


            newPos = self.arduino.readline()
            print("The new positions are:")
            print(newPos.decode())
            self.f.write(newPos.decode().strip()+"\n")
            # Make sure the information is written and stored in the file right away
            self.f.flush()
            os.fsync(self.f)

            # Update the information on the GUI
            posStrs = newPos.decode().split(" ")
            for i in range(0, len(posStrs)):
                if posStrs[i] == "A":
                    self.posA_lbl.config(text="A: " + posStrs[i + 1].strip())
                elif posStrs[i] == "P":
                    self.posP_lbl.config(text="P: " + posStrs[i + 1].strip())
                elif posStrs[i] == "S":
                    self.posS_lbl.config(text="S: " + posStrs[i + 1].strip())

            self.update()

    def AutoMatching(self):

        #######################################
        #         Input verification          #
        #######################################
        if self.ContinuousOrPulsed.get() == 1:
            pulsed = False
        elif self.ContinuousOrPulsed.get() == 2:
            pulsed = True
        else:
            print("Neither pulse, nor continuous was selected. Aborting")
            return False
        if Debug:
            return True

        #######################################
        #        Boot up receiving server     #
        #######################################
        print("booting up receiving server, please set the DAQ collection time to 1 second")
        
        try:
            self.ICserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #UDP
            self.ICserver.bind(('192.168.70.150',5020)) #DAQ IP
        except:
            self.ICserver = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #######################################
        #          Configure RF Output        #
        #######################################
        if not pulsed:
            self.ECout = 1
            self.ECswitch() #Turn on EC
        else:
            self.ECout = 2
            self.ECoutPulsedNumber = 1
            self.ECoutPulsedStartTime = 0
            self.ECoutPulsedOnTime = 0.1 #just enough for a discharge
            self.ECoutPulsedOffTime = 0.4

        self.ICout = 2
        self.ICoutPulsedNumber = 1
        self.ICoutPulsedStartTime = 0.1
        self.ICoutPulsedOnTime = 0.4 #should be stable enough
        self.ICoutPulsedOffTime = 0


        #######################################
        #           Match the system          #
        #######################################

        for i in range(int(self.Steps_entr.get())):
            print(f"Step number {i}")
            if pulsed:
                self.operation(doIC=True,doEC=True,doDAQ=True,nIter=1) #Discharge
                #self.operation(doIC=False,doEC=False,doDAQ=True,nIter=1) #TEMPORARY
            else:
                self.operation(doIC=True,doEC=False,doDAQ=True,nIter=1) #Discharge
                #self.operation(doIC=False,doEC=False,doDAQ=True,nIter=1) #TEMPORARY
            CsM, CpM = self.ICMatch() #Get UDP signal and determine change in capacitor values
            self.moveCap(CsM,CpM)
            time.sleep(3.5) #wait 3.5 seconds for the capacitors to have moved
            # and the system to have cooled a bit.
            # It will also have cooled whilst waiting for the DAQ response

        if not pulsed:
            self.ECout = 1
            self.ECswitch() #Turn off EC



    def ICMatch(self):
        data,addr = self.ICserver.recvfrom(256)
        Vmeas = (np.array(str(data)[2:-2].split(","))).astype(float)
        Pdbm = np.zeros(6)
        
        FREQ = float(self.dev.GetICFreq())

        V0SMatrix = rfObject(touchstone='MatchingSystem/SMatrices/V0.s3p') #gets called from main location
        V1SMatrix = rfObject(touchstone='MatchingSystem/SMatrices/V1.s3p')
        V2SMatrix = rfObject(touchstone='MatchingSystem/SMatrices/V2.s3p')
        V3SMatrix = rfObject(touchstone='MatchingSystem/SMatrices/V3.s3p')
        
        #The following needs to be modified
        Pdbm[0] = (Vmeas[3]-2.333086)/0.02525475 + 57#- V0SMatrix.getS(FREQ)[0,2].real #V0
        Pdbm[1] = (Vmeas[2]-2.333738)/0.02521568 + 54#- V1SMatrix.getS(FREQ)[0,2].real #V1
        Pdbm[2] = (Vmeas[1]-2.35944)/0.02507625  + 68#- V2SMatrix.getS(FREQ)[0,2].real #V2
        Pdbm[3] = (Vmeas[0]-2.348957)/0.02479989 + 62 #- V3SMatrix.getS(FREQ)[0,2].real #V3
        Pdbm[4] = (Vmeas[4]-2.196569)/0.0257915 + 70 #Pf
        Pdbm[5] = (Vmeas[5]-2.257531)/0.02522978 + 70 #Pr
        V = np.sqrt(0.1*10**(Pdbm/10)) #Convert to Vpeak
        GPhase = 190.31 - Vmeas[6]*95.57214 #phase(Vf)-phase(Vr)
        Vf = V[4]
        Vr = V[5]
        Gamma = (10**(Pdbm[5]/10))/(10**(Pdbm[4]/10))
        print('deduced values:')
        print(f"Gamma = {Gamma} with a phase of {GPhase} degrees and |V0-3|²/|Vf|² - 1={(V[0:4]/Vf)**2 - 1}")
        
        SPFactor = 60
        StepConversionFactor = 1/10 #about 10 steps per pF

        ######################################
        #       Calculate modification       #
        ######################################
        EpsG, EpsB = ModAlgo3V(V,Vf,Vr,Gamma,GPhase,FREQ,0,1,3)

        CsM = round(SPFactor*StepConversionFactor*EpsG)
        CpM = round(SPFactor*StepConversionFactor*EpsB)

        ######################################
        #  Get current values of capacitors  #
        ######################################
        posStrs = self.Pos.split(" ")
        for i in range(0, len(posStrs)):
            if posStrs[i] == "P":
                CpO = int(posStrs[i + 1].strip())
            elif posStrs[i] == "S":
                CsO = int(posStrs[i + 1].strip())

        ######################################
        # Calculate new values of Cs and Cp  #
        ######################################
        CsN = CsO + CsM
        CpN = CpO + CpM

        print(f"going from S = {CsO} to {CsN} and P = {CpO} to {CpN}")
    
        return CsN,CpN
        
    def ICDataBaseLookup(self):
        print("Sorry, this doesn't work yet")

    def SuggestValues(self):
        if not Debug:
            SimValues = np.loadtxt("MatchingSystem/SimulatedpF.csv",delimiter=",")
            SuggestedValues = SimValues[np.abs(SimValues[:,0] - float(self.FREQ_entr.get())).argmin()]
            self.SuggestedCpVal = str(int(SuggestedValues[1]/(1000e-12-7e-12)*float(self.maxPos[1])))
            self.SuggestedCsVal = str(int(SuggestedValues[2]/(1000e-12-25e-12)*float(self.maxPos[2])))
            self.SuggestedCaVal = str(int(SuggestedValues[3]/(1000e-12-35e-12)*float(self.maxPos[0])))
        else:
            SimValues = np.loadtxt("MatchingSystem/SimulatedpF.csv",delimiter=",")
            SuggestedValues = SimValues[np.abs(SimValues[:,0] - float(self.FREQ_entr.get())).argmin()]
            self.SuggestedCpVal = SuggestedValues[1]
            self.SuggestedCsVal = SuggestedValues[2]
            self.SuggestedCaVal = SuggestedValues[3]
        self.CapLbl = None
        self.CapLbl = tk.Label(self.top, text=f"Move to the combination Cs: {self.SuggestedCsVal}, Cp: {self.SuggestedCpVal} and Ca: {self.SuggestedCaVal}",
            bg="LightSteelBlue3").place(x=220,y=50)
        self.update()
    
    def scanCap(self):

        # Enable the IC function generator output
        self.dev.IC_enable()

        # Loop through all combinations of capacitor positions
        for posCapS in range(self.minPos[2], self.maxPos[2] + 1):
            for posCapP in range(self.minPos[1], self.maxPos[1] + 1):
                for posCapA in range(self.minPos[0], self.maxPos[0] + 1):

                    # Communicate the desired position to Arduino
                    cmd = "A " + str(posCapA) + " P " + str(posCapP) + " S " + str(posCapS)
                    print(cmd)
                    self.arduino.write(cmd.encode())
                    time.sleep(2)

                    # Retrieve communication from Arduino
                    Pos = self.arduino.readline()
                    if "Error" in Pos.decode():
                        print(Pos.decode())
                        Pos = self.arduino.readline()
                        # After the error, Arduino will communicate the new positions
                        print("The new positions are:")
                        print(Pos.decode())
                        self.f.write(Pos.decode().strip()+"\n")
                        # Make sure the information is written and stored in the file right away
                        self.f.flush()
                        os.fsync(self.f)
                        # Update the information on the GUI
                        posStrs = Pos.decode().split(" ")
                        for i in range(0, len(posStrs)):
                            if posStrs[i] == "A":
                                self.posA_lbl.config(text="A: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "P":
                                self.posP_lbl.config(text="P: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "S":
                                self.posS_lbl.config(text="S: " + posStrs[i + 1].strip())
                        break
                    else:
                        print("The new positions are:")
                        print(Pos.decode())
                        self.f.write(Pos.decode().strip()+"\n")
                        # Make sure the information is written and stored in the file right away
                        self.f.flush()
                        os.fsync(self.f)
                        # Update the information on the GUI
                        posStrs = Pos.decode().split(" ")
                        for i in range(0, len(posStrs)):
                            if posStrs[i] == "A":
                                self.posA_lbl.config(text="A: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "P":
                                self.posP_lbl.config(text="P: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "S":
                                self.posS_lbl.config(text="S: " + posStrs[i + 1].strip())
                        # self.update()

                    self.doDAQ()
                    # Force an immediate trigger event to occur, such that one IC frequency sweep occurs
                    self.dev.IC_enable()
                    self.dev.trigger()
                    time.sleep(2)
                    self.dev.IC_disable()

        # Once all positions are scanned, disable the function generator output for IC and EC
        self.dev.disableOutputs()

    def moveProbeMultithreading(self):
        threading.Thread(target=self.moveProbe).start()
    def moveProbe(self):

        moveXto = self.moveX_entr.get()
        moveYto = self.moveY_entr.get()
        moveZto = self.moveZ_entr.get()

        cmd = ""
        if moveXto:
            cmd += "X " + moveXto + " "
        if moveYto:
            cmd += "Y " + moveYto + " "
        if moveZto:
            cmd += "Z " + moveZto

        if cmd == "":
            print("Specify at least one position")
            return

        # Communicate the desired position to Arduino
        print("Instruct Arduino:")
        print(cmd)
        self.arduino.write(cmd.encode())
        time.sleep(2)

        # Retrieve communication from Arduino
        newPos = self.arduino.readline()
        if "Error" in newPos.decode():
            print(newPos.decode())
            # After the error, Arduino will communicate the new positions
            newPos = self.arduino.readline()
        print("The new positions are:")
        print(newPos.decode())
        self.f.write(newPos.decode().strip()+"\n")
        # Make sure the information is written and stored in the file right away
        self.f.flush()
        os.fsync(self.f)

        # Update the information on the GUI
        posStrs = newPos.decode().split(" ")
        for i in range(0, len(posStrs)):
            if posStrs[i] == "X":
                self.posX_lbl.config(text="Sample manipulator: " + posStrs[i + 1].strip())
            elif posStrs[i] == "Y":
                self.posY_lbl.config(text="Triple Probe H: " + posStrs[i + 1].strip())
            elif posStrs[i] == "Z":
                self.posZ_lbl.config(text="Triple Probe V: " + posStrs[i + 1].strip())

        self.moveX_entr.delete(0, 'end')
        self.moveY_entr.delete(0, 'end')
        self.moveZ_entr.delete(0, 'end')
        self.CapLbl = tk.Label(self.top, text=f"Move to the combination Cs: {self.SuggestedCsVal}, Cp: {self.SuggestedCpVal} and Ca: {self.SuggestedCaVal}",
            bg="LightSteelBlue3").place(x=220,y=50)
        self.update()

    def findLimProbe(self):

        cmd = "limits "
        if self.findLimX.get():
            cmd += "X "
        if self.findLimY.get():
            cmd += "Y "
        if self.findLimZ.get():
            cmd += "Z "

        if cmd == "limits ":
            print("Specify which probe(s)")
            return

        # Communicate the command to Arduino
        print("Instruct Arduino:")
        print(cmd)
        self.arduino.write(cmd.encode())
        time.sleep(2)

        # Retrieve communication from Arduino
        limitXYZ = self.arduino.readline()
        if "Error" in limitXYZ.decode():
            print(limitXYZ.decode())
        else:
            print("The limits are:")
            print(limitXYZ.decode())
            # Store limits. Strip removes the newline
            limitStrs = limitXYZ.decode().split(" ")
            for i in range(0, len(limitStrs)):
                if limitStrs[i] == "X":
                    self.minPos[3] = limitStrs[i + 1].strip()
                    self.maxPos[3] = limitStrs[i + 2].strip()
                elif limitStrs[i] == "Y":
                    self.minPos[4] = limitStrs[i + 1].strip()
                    self.maxPos[4] = limitStrs[i + 2].strip()
                elif limitStrs[i] == "Z":
                    self.minPos[5] = limitStrs[i + 1].strip()
                    self.maxPos[5] = limitStrs[i + 2].strip()

            self.fLim.write(
                "A " + self.minPos[0] + " " + self.maxPos[0] + " P " + self.minPos[1] + " " + self.maxPos[1] + " S "
                + self.minPos[2] + " " + self.maxPos[2] + " X " + self.minPos[3] + " " + self.maxPos[3] + " Y " + self.minPos[4] + " " + self.maxPos[4] + " Z "
                + self.minPos[5] + " " + self.maxPos[5])
            # Make sure the information is written and stored in the file right away
            self.fLim.flush()
            os.fsync(self.fLim)

            # Update the information on the GUI
            self.limX_lbl.config(text="Sample manipulator: [" + str(self.minPos[3]) + ", " + str(self.maxPos[3]) + "]")
            self.limY_lbl.config(text="Triple Probe H: [" + str(self.minPos[4]) + ", " + str(self.maxPos[4]) + "]")
            self.limZ_lbl.config(text="Triple Probe V: [" + str(self.minPos[5]) + ", " + str(self.maxPos[5]).strip() + "]")

            self.findLimX.set(0)
            self.findLimY.set(0)
            self.findLimZ.set(0)

            newPos = self.arduino.readline()
            print("The new positions are:")
            print(newPos.decode())
            self.f.write(newPos.decode().strip()+"\n")
            # Make sure the information is written and stored in the file right away
            self.f.flush()
            os.fsync(self.f)

            # Update the information on the GUI
            posStrs = newPos.decode().split(" ")
            for i in range(0, len(posStrs)):
                if posStrs[i] == "X":
                    self.posX_lbl.config(text="X: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Y":
                    self.posY_lbl.config(text="Y: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Z":
                    self.posZ_lbl.config(text="Z: " + posStrs[i + 1].strip())

            self.update()

    def scanProbe(self):
        
        probeOpt = self.varscanXYZ.get()
        probe = ""
        if probeOpt == "Sample manipulator":
            probe = "X"
        elif probeOpt == "Triple Probe H":
            probe = "Y"
        elif probeOpt == "Triple Probe V":
            probe = "Z"

        doIC = self.scanDoIC.get()
        doEC = self.scanDoEC.get()
        doDAQ = self.scanDoDAQ.get()

        good = self.makeRoutine(doIC, doEC)
        if good == 0:
            return
        
        # Loop through all probe positions
        fromPos = self.scanFrom_entr.get()
        toPos = self.scanTo_entr.get()
        step = self.scanStep_entr.get()
        if fromPos == "" or toPos == "" or step == "":
            print("Specify position range and step size")
            return

        for posProbe in range(int(fromPos), int(toPos)+1, int(step)):
                    # Communicate the desired position to Arduino
                    cmd = probe + " " + str(posProbe)
                    print(cmd)
                    self.arduino.write(cmd.encode())
                    time.sleep(3)

                    # Retrieve communication from Arduino
                    Pos = self.arduino.readline()
                    if "Error" in Pos.decode():
                        print(Pos.decode())
                        Pos = self.arduino.readline()
                        # After the error, Arduino will communicate the new positions
                        print("The new positions are:")
                        print(Pos.decode())
                        self.f.write(Pos.decode().strip()+"\n")
                        # Make sure the information is written and stored in the file right away
                        self.f.flush()
                        os.fsync(self.f)
                        # Update the information on the GUI
                        posStrs = Pos.decode().split(" ")
                        for i in range(0, len(posStrs)):
                            if posStrs[i] == "X":
                                self.posX_lbl.config(text="Sample manipulator: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "Y":
                                self.posY_lbl.config(text="Triple Probe H: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "Z":
                                self.posZ_lbl.config(text="Triple Probe V: " + posStrs[i + 1].strip())
                        break
                    else:
                        print("The new positions are:")
                        print(Pos.decode())
                        self.f.write(Pos.decode().strip()+"\n")
                        # Make sure the information is written and stored in the file right away
                        self.f.flush()
                        os.fsync(self.f)
                        # Update the information on the GUI
                        posStrs = Pos.decode().split(" ")
                        for i in range(0, len(posStrs)):
                            if posStrs[i] == "X":
                                self.posX_lbl.config(text="Sample manipulator: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "Y":
                                self.posY_lbl.config(text="Triple Probe H: " + posStrs[i + 1].strip())
                            elif posStrs[i] == "Z":
                                self.posZ_lbl.config(text="Triple Probe V: " + posStrs[i + 1].strip())
                        # self.update()

                        self.doRoutine(doIC, doEC, doDAQ)
                        # As safety cross-check, disable the function generator output for IC and EC
                        self.dev.disableOutputs()

        # Return to 0
        print("done, returning to zero.")
        cmd = probe + " " + str(0)
        print(cmd)
        self.arduino.write(cmd.encode())
        time.sleep(3)

        # Retrieve communication from Arduino
        Pos = self.arduino.readline()
        if "Error" in Pos.decode():
            print(Pos.decode())
            Pos = self.arduino.readline()
            # After the error, Arduino will communicate the new positions
            print("The new positions are:")
            print(Pos.decode())
            self.f.write(Pos.decode().strip()+"\n")
            # Make sure the information is written and stored in the file right away
            self.f.flush()
            os.fsync(self.f)
            # Update the information on the GUI
            posStrs = Pos.decode().split(" ")
            for i in range(0, len(posStrs)):
                if posStrs[i] == "X":
                    self.posX_lbl.config(text="Sample manipulator: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Y":
                    self.posY_lbl.config(text="Triple Probe H: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Z":
                    self.posZ_lbl.config(text="Triple Probe V: " + posStrs[i + 1].strip())
        else:
            print("The new positions are:")
            print(Pos.decode())
            self.f.write(Pos.decode().strip()+"\n")
            # Make sure the information is written and stored in the file right away
            self.f.flush()
            os.fsync(self.f)
            # Update the information on the GUI
            posStrs = Pos.decode().split(" ")
            for i in range(0, len(posStrs)):
                if posStrs[i] == "X":
                    self.posX_lbl.config(text="Sample manipulator: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Y":
                    self.posY_lbl.config(text="Triple Probe H: " + posStrs[i + 1].strip())
                elif posStrs[i] == "Z":
                    self.posZ_lbl.config(text="Triple Probe V: " + posStrs[i + 1].strip())

    def escape(self):
        if not Debug:
            self.f.close()
            self.fLim.close()
            self.dev.disableOutputs()
            self.arduino.close()
            try:
                self.ICserver.close()
            except:
                print("Assuming you didn't use the matching system")
        self.destroy()

    def getICfreqText(self):
        ICfreqText = "The IC frequency is "
        if str(self.dev.GetICFreqMode()) == "SWE":
            ICfreqText += "set to sweep from " + str(self.dev.GetICSweepFreqStart()) + " to " + str(self.dev.GetICSweepFreqStop()) + "\n during " +  str(self.dev.GetICSweepTime())
            if str(self.dev.GetICSweepMode()) == "MAN":
                ICfreqText += ", upon trigger.\n !! This eliminates the IC output setting !!"
            elif str(self.dev.GetICSweepMode()) == "AUTO":
                ICfreqText += ", repeatedly."
            else:
                ICfreqText += ", UNCLEAR."
        elif str(self.dev.GetICFreqMode()) == "CW" or str(self.dev.GetICFreqMode()) == "FIX":
            ICfreqText += "set fixed at " + str(self.dev.GetICFreq()) + " Hz"
        else:
            ICfreqText += "UNCLEAR."
        return ICfreqText

    def setICPower(self):
        Pin = self.setICpower_entr.get()
        if len(Pin) == 0:
            print("Specify IC power")
            return

        print('set IC power to ' + str(Pin))
        # Set the IC voltage amplitude to Pin (in dBm) and the voltage ofsett to 0 V, limited at 10 dBm.
        self.dev.setICPower(float(Pin))  # dBm
        # Update information on GUI
        self.ICpower_lbl.config(text="The IC power is " + str(self.dev.GetICPower()))
        self.setICpower_entr.delete(0, 'end')

    def setICfreq(self):
        Freqin = self.setICfreq_entr.get()
        if len(Freqin) == 0:
            print("Specify IC frequency")
            return

        print ('set IC freq to ' + str(Freqin))
        # For the IC channel (2), disable the frequency sweep and set the input frequency as fixed.
        self.dev.setICFixedFrequency(Freqin)
        
        # Update information on GUI
        freqText = str(self.getICfreqText())
        if "!!" in freqText:
            self.ICfreq_lbl.config(text=freqText, fg="red")
        else:
            self.ICfreq_lbl.config(text=freqText, fg="black")
        
        self.setICfreq_entr.delete(0, 'end')

    def setICswe(self):

        frq_start = self.setICsweFrom_entr.get()
        frq_stop = self.setICsweTo_entr.get()
        sweep_time = self.setICsweTime_entr.get()
        sweep_mode = self.varICswe.get()

        if len(frq_start) == 0 or len(frq_stop) == 0 or len(sweep_time) == 0 or len(sweep_mode) == 0:
            print("Specify all frequency sweep settings")
            return

        print("set IC sweep " + sweep_mode + " from " + frq_start + " to " + frq_stop + " with sweep duration " + sweep_time)

        if sweep_mode == "repeatedly":
            # Perform the IC frequency sweep repeatedly, over the range [fstart, fstop]
            # where every sweep takes sweep_time
            self.dev.sweepICFreqRepeatedly(frq_start, frq_stop, sweep_time)
        elif sweep_mode == "upon trigger":
            # Perform the IC frequency sweeps once when a trigger occurs, over the range [frq_start, frq_stop]
            # where the sweep takes sweep_time
            self.dev.SweepICFreqOnceAtTrig(frq_start, frq_stop, sweep_time)

        # Update information on GUI
        self.ICfreq_lbl.config(text=str(self.getICfreqText()))
        self.setICsweFrom_entr.delete(0, 'end')
        self.setICsweTo_entr.delete(0, 'end')
        self.setICsweTime_entr.delete(0, 'end')

    def setICout(self):

        self.ICout = self.varICout.get() # int: 1 continuous 2 pulsed
        self.ICoutPulsedOnTime = self.ICoutPulsedOnTime_entr.get()
        self.ICoutPulsedOffTime = self.ICoutPulsedOffTime_entr.get()
        self.ICoutPulsedNumber = self.ICoutPulsedNumber_entr.get()
        self.ICoutPulsedStartTime = self.ICoutPulsedStartTime_entr.get()
        
        ICoutText = "the IC output is "
        if self.ICout == 1:
            ICoutText += "continuous"
        elif self.ICout == 2:
            if len(self.ICoutPulsedNumber) == 0 or len(self.ICoutPulsedStartTime) == 0 or len(self.ICoutPulsedOnTime) == 0 or len(self.ICoutPulsedOffTime) == 0:
                print("Specify all IC pulse settings")
                return
            else:
                ICoutText += "pulsed with " + str(self.ICoutPulsedNumber) + " pulses, starting at " + str(self.ICoutPulsedStartTime) + "\n with on time "+ str(self.ICoutPulsedOnTime) + " and off time " + str(self.ICoutPulsedOffTime)
        else:
            print("Specify IC output as continuous or pulsed")
            return

        print('set IC output such that ' + ICoutText)
        self.ICoutput_lbl.config(text=ICoutText)

        self.ICoutPulsedOnTime_entr.delete(0, 'end')
        self.ICoutPulsedOffTime_entr.delete(0, 'end')
        self.ICoutPulsedNumber_entr.delete(0, 'end')
        self.ICoutPulsedStartTime_entr.delete(0, 'end')

    def ICswitch(self):           
        print('Switch IC output')
        ICstatus = str(self.dev.GetICOutputStatus())
        if ICstatus == "0":
            self.ICoperation()
        else:
            # Enable the IC function generator output
            self.dev.IC_disable()
            print('off')
            ICstatus = str(self.dev.GetICOutputStatus())
            if ICstatus == "0":
                self.ICswitch_lbl.config(text="The IC is off")
                self.ICswitch_btn.config(text="Do IC!")
            else:
                self.ICswitch_lbl.config(text="The IC is on")
                self.ICswitch_btn.config(text="disable IC!")

    def ICoperation(self):
        
        if self.dev.GetICFreqMode() == 'SWE' and self.dev.GetICSweepMode() == 'MAN':
            print("Not allowed when frequency sweep is set. Please use trigger button")
        elif self.ICout == 1:  # continuous
            # Enable the IC function generator output
            self.dev.IC_enable()
            print('on')
            ICstatus = str(self.dev.GetICOutputStatus())
            if ICstatus == "0":
                self.ICswitch_lbl.config(text="The IC is off")
                self.ICswitch_btn.config(text="Do IC!")
            else:
                self.ICswitch_lbl.config(text="The IC is on")
                self.ICswitch_btn.config(text="disable IC!")
        elif self.ICout == 2:  # pulsed
            time.sleep(int(self.ICoutPulsedStartTime))
            counter = 0
            while counter < int(self.ICoutPulsedNumber):
                self.dev.IC_enable()
                print('on')
                time.sleep(int(self.ICoutPulsedOnTime))
                self.dev.IC_disable()
                print('off')
                time.sleep(int(self.ICoutPulsedOffTime))
                counter += 1

    def ICtrigger(self):
        print('force IC trigger')
        self.doDAQ()
        # Force an immediate trigger event to occur, such that one IC frequency sweep occurs
        self.dev.IC_enable()
        self.dev.trigger()
        time.sleep(float(self.dev.GetICSweepTime()))
        self.dev.IC_disable()

    def setECPower(self):
        # MODDED by Arthur 17/08/23 to make the power setting automatic
        Pin = self.setECpower_entr.get() # get filled in value
        try:
            float(Pin)
        except ValueError:
            print("EC power must be a number")
            return
        if len(Pin) == 0:
            print("Specify EC power")
            return
        if float(Pin)<665:
            print("Power should be between 660W and 5970W; using 665W")
            Pin = 665
        if float(Pin)>5970:
            print("Power should be between 675W and 5970W; using 5970W")
            Pin = 5970

        print('set EC power to ' + str(Pin))
        # Set the EC voltage amplitude to Pin (in dBm) and the voltage ofsett
        # to 0 V, limited at 10 dBm.
        self.DAQtrig.setECPower(float(Pin))  # dBm
        # Update information on GUI
        self.ECPower = float(Pin)
        self.ECpower_lbl.config(text="The EC power is " + str(self.ECPower) +" W")
        self.setECpower_entr.delete(0, 'end')


    def setECout(self):
        self.ECout = self.varECout.get() # int: 1 continuous 2 pulsed

        self.ECoutPulsedOnTime = self.ECoutPulsedOnTime_entr.get()
        self.ECoutPulsedOffTime = self.ECoutPulsedOffTime_entr.get()
        self.ECoutPulsedNumber = self.ECoutPulsedNumber_entr.get()
        self.ECoutPulsedStartTime = self.ECoutPulsedStartTime_entr.get()

        ECoutText = "the EC output is "
        if self.ECout == 1:
            ECoutText += "continuous"
        elif self.ECout == 2:
            if len(self.ECoutPulsedNumber) == 0 or len(self.ECoutPulsedStartTime) == 0 or len(self.ECoutPulsedOnTime) == 0 or len(self.ECoutPulsedOffTime) == 0:
                print("Specify all EC pulse settings")
                return
            else:
                ECoutText += "pulsed with " + str(self.ECoutPulsedNumber) + " pulses, starting at " + str(self.ECoutPulsedStartTime) + "\n with on time "+ str(self.ECoutPulsedOnTime) + " and off time " + str(self.ECoutPulsedOffTime)
        else:
            print("Specify EC output as continuous or pulsed")
            return

        print('set EC output such that ' + ECoutText)
        self.ECoutput_lbl.config(text=ECoutText)

        self.ECoutPulsedOnTime_entr.delete(0, 'end')
        self.ECoutPulsedOffTime_entr.delete(0, 'end')
        self.ECoutPulsedNumber_entr.delete(0, 'end')
        self.ECoutPulsedStartTime_entr.delete(0, 'end')

    def ECswitch(self):
        print('Switch EC output')
        ECstatus = str(self.dev.GetECOutputStatus())
        if ECstatus == "0":
            self.ECoperation()
        else:
            # Enable the EC function generator output
            self.dev.EC_disable()
            print('off')
            ECstatus = str(self.dev.GetECOutputStatus())
            if ECstatus == "0":
                self.ECswitch_lbl.config(text="The EC is off")
                self.ECswitch_btn.config(text="Do EC!")
            else:
                self.ECswitch_lbl.config(text="The EC is on")
                self.ECswitch_btn.config(text="disable EC!")

    def ECoperation(self):
        if self.ECout == 1:  # continuous
            # Enable the IC function generator output
            self.dev.EC_enable()
            print('on')
            ECstatus = str(self.dev.GetECOutputStatus())
            if ECstatus == "0":
                self.ECswitch_lbl.config(text="The EC is off")
                self.ECswitch_btn.config(text="Do EC!")
            else:
                self.ECswitch_lbl.config(text="The EC is on")
                self.ECswitch_btn.config(text="disable EC!")
        elif self.ECout == 2:  # pulsed
            time.sleep(int(self.ECoutPulsedStartTime))
            counter = 0
            while counter < int(self.ECoutPulsedNumber):
                self.dev.EC_enable()
                print('on')
                time.sleep(int(self.ECoutPulsedOnTime))
                self.dev.EC_disable()
                print('off')
                time.sleep(int(self.ECoutPulsedOffTime))
                counter += 1

    def doDAQ(self):
        self.DAQtrig.trigger()

    def DAQwrite(self):

        input = self.DAQfile_entr.get()
        if len(input) == 0:
            print("Specify file name")
            return

        filename = "./DAQ/" + input + ".csv"
        print("Write DAQ settings to file " + filename)
        
        fexists = exists(filename)
        
        # a+ creates the file if it does not exist and opens it in append mode
        DAQfile = open(filename, "a+")
        
        # If file did not exist yet, insert heading

        if fexists == False:            
            print("First entry to the file")
            # date
            DAQfile.write("Date,")
            DAQfile.write(self.DAQfirstshot_lbl.cget("text") + ",")
            DAQfile.write(self.DAQlastshot_lbl.cget("text") + ",")
            DAQfile.write(self.DAQgasHe_lbl.cget("text") + ",")
            DAQfile.write(self.DAQgasD_lbl.cget("text") + ",")
            DAQfile.write(self.DAQgasAr_lbl.cget("text") + ",")
            DAQfile.write(self.DAQcoilI_lbl.cget("text") + ",")
            DAQfile.write(self.DAQTPbat_lbl.cget("text") + ",")
            DAQfile.write(self.DAQVDiv_lbl.cget("text") + ",")
            DAQfile.write(self.DAQECpol_lbl.cget("text") + ",")
            DAQfile.write(self.DAQcomment_lbl.cget("text") + "\n")

        DAQfile.write(str(date.today()) + ",")
        DAQfile.write(self.DAQfirstshot_entr.get() + ",")
        DAQfile.write(self.DAQlastshot_entr.get() + ",")
        DAQfile.write(self.DAQgasHe_entr.get() + ",")
        DAQfile.write(self.DAQgasD_entr.get() + ",")
        DAQfile.write(self.DAQgasAr_entr.get() + ",")
        DAQfile.write(self.DAQcoilI_entr.get() + ",")
        DAQfile.write(self.DAQTPbat_entr.get() + ",")
        DAQfile.write(self.DAQVDiv_entr.get() + ",")
        DAQfile.write(self.DAQECpol_entr.get() + ",")
        DAQfile.write(self.DAQcomment_entr.get() + "\n")

        # Make sure the information is written and stored in the file right away
        self.DAQfile.flush()
        os.fsync(self.DAQfile)

        DAQfile.close()
        
    def makeRoutine(self, doIC, doEC):
                    
        self.ICvec.clear()
        self.ECvec.clear()
        
        if doIC:
            
            if self.dev.GetICFreqMode() == 'SWE' and self.dev.GetICSweepMode() == 'MAN': # frequency sweep upon trigger
                # Enable the IC function generator output
                # Force an immediate trigger event to occur, such that one IC frequency sweep occurs
                self.ICvec.append("trg") # this contains 1 sleeptime
                # Sleep during sweep
                nsleepEntries = float(self.dev.GetICSweepTime())/self.timeStep
                for i in range (0, round(nsleepEntries)-1):
                    self.ICvec.append("sle")
                # Disable the IC function generator output
                self.ICvec.append("dis")
            else: # Fixed frequency or repeated frequency sweeps
                if self.ICout == 1:  # continuous
                    print('Error: Enabling continuous IC is not allowed during probe scan')
                    return 0
                
                elif self.ICout == 2:  # pulsed
                
                    # sleep during start time
                    nsleepEntries =  float(self.ICoutPulsedStartTime)/self.timeStep
                    for i in range (0, round(nsleepEntries)):
                        self.ICvec.append("sle")

                    # For the desired amount of pulses
                    for i in range (0, int(self.ICoutPulsedNumber)):
                        
                        # enable output
                        self.ICvec.append("ena") # this contains 1 sleeptime

                        # sleep during onTime
                        nsleepEntries =  float(self.ICoutPulsedOnTime)/self.timeStep
                        for i in range (0, round(nsleepEntries)-1):
                            self.ICvec.append("sle")

                        # disable output
                        self.ICvec.append("dis") # this contains 1 sleeptime

                        # sleep during off time
                        nsleepEntries = float(self.ICoutPulsedOffTime)/self.timeStep
                        for i in range (0, round(nsleepEntries)-1):
                            self.ICvec.append("sle")				
    
        if doEC:
            if self.ECout == 1:  # continuous
                print('Error: Enabling continuous EC is not allowed during probe scan')
                return 0

            elif self.ECout == 2:  # pulsed

                # sleep during start time
                nsleepEntries = float(self.ECoutPulsedStartTime)/self.timeStep
                for i in range (0, round(nsleepEntries)):
                    self.ECvec.append("sle")

                # For the desired amount of pulses
                for i in range(0, int(self.ECoutPulsedNumber)):
                    # enable output
                    self.ECvec.append("ena") # this contains 1 sleeptime

                    # sleep during onTime
                    nsleepEntries = float(self.ECoutPulsedOnTime)/self.timeStep
                    for j in range(0, round(nsleepEntries)-1):
                        self.ECvec.append("sle")
                        
                    # disable output
                    self.ECvec.append("dis") # this contains 1 sleeptime

                    # sleep during off time
                    nsleepEntries = float(self.ECoutPulsedOffTime)/self.timeStep
                    for k in range(0, round(nsleepEntries)-1):
                        self.ECvec.append("sle")			
        return 1

    def doRoutine(self, doIC, doEC, doDAQ):

        print(self.ICvec)
        print(self.ECvec)

        nIter = 0
        if len(self.ICvec) > len(self.ECvec):
            nIter = len(self.ICvec)
        else:
            nIter = len(self.ECvec)

        if doDAQ:
            ticDAQ = time.time()
            # print("ticDAQ " + str(ticDAQ))
            self.doDAQ()
            tocDAQ = time.time()
            while tocDAQ - ticDAQ < 0.3:
                time.sleep(0.001)
                tocDAQ = time.time()

        tic = time.time()
        # print("tic " + str(tic))
        for i in range(0, nIter):

            if doIC and i < len(self.ICvec):
                if self.ICvec[i] == "sle":
                    pass
                elif self.ICvec[i] == "ena":
                    print("IC enable")
                    self.dev.IC_enable()
                elif self.ICvec[i] == "dis":
                    print("IC disable")
                    self.dev.IC_disable()
                elif self.ICvec[i] == "trg":
                    print("IC trig")
                    self.dev.IC_enable()
                    self.dev.trigger()

            if doEC and i < len(self.ECvec):
                if self.ECvec[i] == "sle":
                    pass
                elif self.ECvec[i] == "ena":
                    print("EC enable")
                    self.dev.EC_enable()
                elif self.ECvec[i] == "dis":
                    print("EC disable")
                    self.dev.EC_disable()

            toc = time.time()
            while toc - tic < (i + 1) * self.timeStep:
                time.sleep(self.timeStep / 10)
                toc = time.time()
            # print(str(toc - tic))

    def operation(self,doIC=None,doEC=None,doDAQ=None,nIter=None):
        if not doDAQ: #Test if not called from matching system
            doIC = self.OPDoIC.get()
            doEC = self.OPDoEC.get()
            doDAQ = self.OPDoDAQ.get()

        good = self.makeRoutine(doIC, doEC)
        if good == 0:
            return
        if not nIter:
            nIter = self.OPamount_entr.get()
            if len(nIter) == 0:
                print("Specify amount of routines")
                return
        
        for i in range(0, int(nIter)):
            self.doRoutine(doIC, doEC, doDAQ)
