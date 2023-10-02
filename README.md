# General Introduction 

In the investigation of novel magnetic materials, it is often useful to be able to perform spatially resolved measurements of the magnetic fields they are emitting at cryogenic temperatures (around 1 Kelvin, or -272 Celcius). 
During my PhD, I built from scratch a novel microscopic capable of mapping the magnetic fields emitted by a flat sample with nanoscale spatial resolution. 
The spatially resolved measurements were performed by rastering a 100 nanometer diameter custom made magnetic field sensor above a flat material's surface, while maintaining a separation between the sensor and the surface of ~20 nanometers.  
Our sensors were nanoscale Superconduction Quantum Interference Devices, typically shorted in name to nanoSQUIDs

# nanoSQUID Scanning Softare
One of my tasks during my PhD was to develop the software required to control all of the components of the complicated experiment with an emphasis on making the software easy to use for other group members who may only have rudimentary software skills. The project presented in this GITHUB repository contains all the software that directly controls the experiment and the user interface that enables other's to use it without issue. It is capable of performing the following tasks:

1. Characterization the sensors
2. Characterization of eletronic resistance of samples
3. Surface defection
4. Rastering the sensor while accounting for tilts, while reading out the sensor
5. Coarse sensor motion that enables navigating to regions of interest
6. Feedback systems to prevent crashing into the surface damaging either the sensor or the sample. Must be running constantly in the background. Both account for user error and unforeseen experimental scenarios (for example, a random piece of dust on the sample surface)
7. Scripting interfaces
8. Live visualization of what's being done
9. Monitor and control the temperature of the sample / sensor

The code is primarily written in python 2.7 and uses a mix of Serial, GPIB, and TCIP protocols to communicate with the hardware that electronically controls the apparatus. 
Asynchronous control of the hardware is performed using Labrad, an asynchronous client/server RPC system designed for use in scientific laboratories.
Ease of use is enabled by designing a GUI with PyQt4.
