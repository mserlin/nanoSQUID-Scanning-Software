# LabRAD-nSOT-Scanner
 
# General Introduction 

In the investigation of novel magnetic materials, it is often useful to be able to perform spatially resolved measurements of the magnetic fields they are emitting. 
During my PhD, I built from scratch a novel microscopic capable of mapping the magnetic fields emitted by a flat sample with nanoscale spatial resolution. 
The spatially resolved measurements were performed by rastering a single custom made magnetic field sensor (about 100 nanometers in diameter) above a flat material's surface while maintaining a separation between the sensor and the surface of ~20 nanometers.  

The hardware used to control the experiment, some of which I developed and some of which was purchased, all needed to be reliably controlled with software that enables ease of use of a complicated experiment 

Characterization the sensors
Surface defection
Rastering the sensor while accounting for tilts 
Navigating to regions of interest
Feedback systems to prevent crashing into the surface damaging either the sensor or the sample
Scripting interfaces

# Description of software

This is the software suite I developped during my PhD to control the scanning experiment. 

The code is written in python 2.7. 
I use a mix of Serial, GPIB, and TCIP protocols to communicate with the hardware that electronically controls the apparatus. 
Asynchronous control of the hardware is performed using Labrad, an asynchronous client/server RPC system designed for use in scientific laboratories.
Ease of use is enabled by designing a GUI with PyQt4.
