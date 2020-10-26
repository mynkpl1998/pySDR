pyComm
======

An open source python library designed for RTL-SDR.

Objectives
----------

* This library is developed to provide easy access to RTL-SDR by wrapping the C based **librtlsdr** driver for python using ctypes. 

---
**NOTE**

This library is designed to work with RTL SDR which uses **Realtek RTL2832U** and **Rafael Micro R820T tuner** only.

---

Installation
------------
We recommend you to create a virtual or conda environment. You get the minimal version of conda(Miniconda) form [here](https://docs.conda.io/en/latest/miniconda.html).

```bash
# Create a conda environment named pySDR.
conda create -n pysdr python=3.8
conda activate pysdr

# Begin installation.
pip install -r requirements.txt
python setup.py install
```
Credits
-------

* Most of the base code is adapted from [https://github.com/roger-/pyrtlsdr](https://github.com/roger-/pyrtlsdr).