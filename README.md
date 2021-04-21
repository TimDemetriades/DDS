# DDS - Drone Deterrence System
## Senior Design Project - Stevens Institute of Technology

<img src="https://github.com/TimDemetriades/DDS/blob/dev/resources/qr-code.png?raw=true" width="150">

## Abstract
In the coming years the prevalence of commercial and consumer drones in residential airspace is expected to increase immensely. The availability and agility of even consumer grade drones pose a threat to the privacy of all citizens, being that they could easily be used to monitor an unsuspecting person. Our system combines the functionality of image and signal classification to detect the presence of a drone. Furthermore, system can deter* snooping drones, preventing the breach of a citizens privacy. The deterrence may be capturing the drones video signal, determining the location of the drone's operator, gathering identifying information about the drone, or issuing commands to the drone.

## Basic System Model
### High-level Overview of the System's Organization:

<p align="center">
  <img src="https://github.com/TimDemetriades/DDS/blob/dev/resources/old-system-diagram.png?raw=true" width="500">
</p>

The system consists of two Raspberry Pi 4s which communicate over ethernet using the [Pyro4](https://pyro4.readthedocs.io/en/stable/) module. This module allows the pis to share the "main-camera" class over their private network to communicate through python functions and variables. The pi illustrated in "Subsystem 2" will watch the know shape of the drone's radio frequency. When the shape is confidently detected, it will activate the object detection function on the pi labelled "Subsystem 1". This function starts a script which will run a custom trained Edgetpu enabled tflite model. This model allows the pi to detected and track drones with high accuracy. The detection of a drone by the object detection script will instruct the motor to turn in attempt to center the drone in frame. Centering the drone in frame is how the system is able to aim its directional antenna at the target. Additionally, when the drone is detected by the object detection script, Submodule 1 will notify Submodule 2 to begin sending out the jamming signal. When the drone leaves the frame, Subsystem 2 is then told to stop the jamming signal and to begin watching for the radio frequency shape again. When the shape is no longer detected the object detection process is also ended.

### System Build:
Below is the physical build of the system described above.
<p align="center">
  <img src="https://github.com/TimDemetriades/DDS/blob/dev/resources/system-build-placeholder.JPG?raw=true" width="500">
</p>

### RF Detection
<p align="center">
  <img src="https://github.com/TimDemetriades/DDS/blob/dev/resources/rf-shape.PNG?raw=true" width="500">
</p>

### Object Detection:
The system's object detection is performed by a retrained quantized tensorflow model that was then converted into a tensorflow lite model and complied with the edgetpu compiler to make is compatible for Google's Coral TPU. 
<p align="center">
  <img src="https://github.com/TimDemetriades/DDS/blob/dev/resources/cam-pov.gif?raw=true">
</p>

### RF Jamming


