# Utilizing Artificial Neural Networks to Detect Main Engine Irregularities on Container Ships
This project, an inter-university research collaboration, focuses on a prototype system for detecting anomalies in marine engines, tested on a small-scale diesel engine at the Shipbuilding State Polytechnic of Surabaya (PPNS). The goal is to provide early warnings using an Artificial Neural Network (ANN).

> **Key Features & Technologies:**
1. Core Function: Real-time anomaly detection using an ANN model to predict engine irregularities based on key operational data.
2. Monitored Parameters: Main Bearing Temperature, Exhaust Gas Temperature, and Engine Speed.
3. Control System: Schneider M200CE40T PLC programmed with Ladder Logic.
4. Sensors & Hardware:
   * RTD PT-100 sensors for temperature measurement.
   * ADM-4280 module for serial communication with the PLC.
   * Proximity sensor for engine speed measurement.
6. User Interface & Communication: A custom dashboard built with Node-RED, connected via MQTT for real-time data visualization.
7. Software & Development:
   - MATLAB for training the Artificial Neural Network.
   - Python and Ladder Logic for system implementation and control.


## BLOK DIAGRAM SYSTEM
![Blok Sistem](/Assets/IMG_6.jpg)

## Architecture Artificial Neural Network
![Blok Sistem](/Assets/IMG_8.jpg)

## Dokumentation
### Panel Wiring
![Blok Sistem](/Assets/IMG_1.jpg)
![Blok Sistem](/Assets/IMG_5.jpg)
### Exhaust Gas Temperature Sensor
![Blok Sistem](/Assets/IMG_2.jpg)
### Main Bearing Temperature Sensor
![Blok Sistem](/Assets/IMG_4.jpg)
### Proximity Sensor
![Blok Sistem](/Assets/IMG_3.jpg)




 
