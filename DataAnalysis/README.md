# PlotData

A prototypical program able to view DAQ files and convert to measured quantities using the necessary calibrations. 
A quick demo is shown below:

https://github.com/LPP-ERM-KMS/TOMAS/assets/66306556/8b22509e-621d-4d63-9a03-b5a4062a0ac2



more features will be added such as:

- Having a conversion of triple probe implemented (as accurate as possible)
- Having a conversion for interferometer implemented
- Converting a folder of input data to calibrated output

## Requirements

### list
specials:
- tkinter
- lvm_read

usual suspects:
- numpy
- scipy
- matplotlib

### install guide
If you're on an old distro (e.g ubuntu):
$ pip install tkinter lvm_read numpy scipy matplotlib

If you're on macos or on a rolling release distro (e.g arch), open up your
terminal and create a venv:
$ python -m venv FOLDER
where FOLDER is where you want your venv to be located
source the venv (I suggest making a shortcut for this):
$ source FOLDER/bin/activate
and install the required software in this venv (this avoids
bricking your system if one of the python programs is incompatible):
$ pip install tkinter lvm_read numpy scipy matplotlib
now every time you open a new terminal, prior to running the software you'll have
to source the venv.
Alternatively, if you're not afraid of bricking your system, most of these packages
can also be downloaded from the repository in the form "python-xyz", e.g "python-tkinter".
(for macos I suggest homebrew)

If you're on windows, I guess anaconda has you covered? (I haven't willingly used windows in 5 years so idk)
