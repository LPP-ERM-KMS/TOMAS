# PlotData

A prototypical program able to view DAQ files and it's corresponding quantities using the necessary calibrations. 
It's also able to convert LVM files in a folder to both CSV and mat formats.
A quick demo is shown below:

https://github.com/LPP-ERM-KMS/TOMAS/assets/66306556/e85db991-f8f5-4ba5-b31e-944a3c9ea37e

more features will be added such as:

- Having a conversion of triple probe implemented (as accurate as possible)
- Having a conversion for interferometer implemented
- Converting a folder of input data to calibrated output

**Further suggestions are welcome!**

To easily get a hold of new suggestions, please create an issue.

# Requirements

## list of requirements
specials:
- tkinter
- lvm_read

usual suspects:
- numpy
- scipy
- matplotlib

## install guide
### Debian based
If you're on an old distro (e.g ubuntu):
```console
$ pip install tkinter lvm_read numpy scipy matplotlib
```
### macos / rolling release
If you're on macos or on a rolling release distro (e.g arch), open up your
terminal and create a venv:
```console
$ python -m venv FOLDER
```
where FOLDER is where you want your venv to be located
source the venv (I suggest making a shortcut for this):

```console
$ source FOLDER/bin/activate
```
and install the required software in this venv (this is
considered the "safer" way of installing python packages):

```console
$ pip install tkinter lvm_read numpy scipy matplotlib
```

now every time you open a new terminal, prior to running the software you'll have
to source the venv.
Alternatively, as the listed packages are quite tame, most (I didn't test this) of these packages
can be downloaded using your package manager in the form "python-xyz", e.g "python-tkinter".
(for macos I suggest homebrew)

### Windows
🚧 under construction
I guess in some ide with anaconda loaded you install stuff you don't have yet using pip in the kernel? 
(I haven't willingly used windows in 5 years so idk)
