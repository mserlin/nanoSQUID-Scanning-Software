# General Introduction 

In the investigation of novel magnetic materials, it is often useful to be able to perform spatially resolved measurements of the magnetic fields they are emitting at cryogenic temperatures (around 1 Kelvin, or -272 Celcius).
During my PhD, I built from scratch a novel microscopic capable of mapping the magnetic fields emitted by a flat sample with nanoscale spatial resolution.
The spatially resolved measurements were performed by rastering a 100 nanometer diameter custom made magnetic field sensor above a flat material's surface, while maintaining a separation between the sensor and the surface of ~20 nanometers.
Our sensors were nanoscale Superconducting Quantum Interference Devices, typically shorted in name to nanoSQUIDs

# nanoSQUID Scanning Software
One of my tasks during my PhD was to develop the software required to control all of the components of the complicated experiment with an emphasis on making the software easy to use for other group members who may only have rudimentary software skills. The project presented in this GITHUB repository contains all the software that directly controls the experiment and the user interface that enables other's to use it without issue. It is capable of performing the following tasks:

1. Characterization of nanoSQUID Sensors 
2. Characterization of sample's bulk electronic properties
3. Detecting contact between the nanoSQUID Sensor and a surface. This includes (1) an automated procedure for bringing the sensor in contact with the surface and (2) a safety feature that withdraws the sensor if accidental surface contact is detected at any point (for example, if an unsuspecting dust particle is on the sample that risks damaging either the sensor or sample)
4. Coarse motion of the sensor that enables navigating to a sample's region of interest
5. Rastering the sensor on a tilted plane while performing buffered acquisition of multiple measurements
6. Monitor and control the temperature at various positions in the apparatus
7. Monitor and control a background magnetic field
8. Live visualization of all actions being performed
9. Scripting interface that enables automating all of the aforementioned functions within the software

The code is primarily written in python 2.7 and uses a mix of Serial, GPIB, and TCIP protocols to communicate with the hardware that electronically controls the apparatus. 
Asynchronous control of the hardware is performed using LabRAD, an asynchronous client/server RPC system designed for use in scientific laboratories.
Ease of use is enabled by designing a GUI with PyQt4.
