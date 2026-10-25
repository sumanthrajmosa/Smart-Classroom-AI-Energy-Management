# AI-Based Smart Classroom Attendance and Energy Management System

## 1. Project Overview

The **AI-Based Smart Classroom Attendance and Energy Management System** is an IoT-based project designed to automate classroom entry/exit monitoring, occupancy detection, attendance management, and energy optimization using Artificial Intelligence and embedded systems.

The system uses a Raspberry Pi and camera to detect people, track their movement, and identify whether they are entering or leaving the classroom. Occupancy information can then be used to control classroom lighting and fans, helping reduce unnecessary energy consumption.

## 2. Objectives

- Detect people entering and exiting the classroom.
- Use YOLO for real-time person detection.
- Use ByteTrack to track detected people across video frames.
- Identify entry and exit events using virtual line crossing.
- Estimate classroom occupancy.
- Support row-wise occupancy monitoring for targeted energy control.
- Integrate environmental sensors for intelligent energy management.
- Provide a dashboard for occupancy, attendance, and energy analytics.

## 3. Proposed Technologies

| Component | Technology |
|---|---|
| Main controller | Raspberry Pi 4 or Raspberry Pi 5 |
| Camera | Raspberry Pi Camera Module 3 or compatible camera |
| Programming language | Python |
| Object detection | YOLOv8 Nano |
| Object tracking | ByteTrack |
| Computer vision | OpenCV |
| Web dashboard | Flask, HTML, CSS, JavaScript |
| Database | SQLite |
| Sensors | LDR, temperature sensor, acoustic sensor |
| Appliance control | Relay module |
| Communication | Wi-Fi |

## 4. System Architecture

```text
Camera
   |
   v
YOLO Person Detection
   |
   v
ByteTrack Object Tracking
   |
   v
Virtual Line Crossing
   |
   +---- Outside to Inside: Entering
   |
   +---- Inside to Outside: Exiting
   |
   v
Occupancy Count
   |
   v
Row-Based Occupancy Estimation
   |
   v
Energy Management
   |
   +---- LDR: Ambient Light Monitoring
   +---- Temperature: Fan Control Logic
   +---- Relay: Appliance Switching
   +---- Acoustic Sensor: Noise Monitoring
   |
   v
Database and Dashboard
```

## 5. Project Modules

### Person Detection
YOLO detects people in camera frames and generates bounding boxes.

### Object Tracking
ByteTrack associates detections across frames and assigns temporary tracking IDs.

### Entry and Exit Detection
A virtual line is configured at the classroom entrance. When a tracked person crosses it, the system determines the crossing direction and generates an entry or exit event.

### Occupancy Management
The system maintains an estimated occupancy count based on detected entry and exit events. Row-level occupancy can be estimated using configured classroom regions.

### Energy Management
Environmental sensor readings and occupancy estimates can be used to determine whether classroom lights and fans should be switched on or off.

### Dashboard
The proposed dashboard displays occupancy information, entry/exit events, sensor readings, attendance records, and energy-management status.

## 6. Hardware Requirements

- Raspberry Pi 4 (4 GB RAM) or Raspberry Pi 5 (4 GB RAM)
- Compatible camera
- MicroSD card
- Suitable Raspberry Pi power supply
- Relay module
- LDR sensor
- Temperature sensor
- Acoustic sensor
- Jumper wires and connectors
- Lights and fans for controlled demonstration

An RFID reader may be added if verified student identity is required for attendance.

## 7. Software Requirements

- Raspberry Pi OS 64-bit
- Python 3
- OpenCV
- Ultralytics
- NumPy
- Flask
- SQLite
- Raspberry Pi GPIO libraries, as required by the selected hardware

## 8. Installation

Clone the repository:

```bash
git clone https://github.com/sumanthrajmosa/Smart-Classroom-AI-Energy-Management.git
cd Smart-Classroom-AI-Energy-Management
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies after the project’s `requirements.txt` has been prepared:

```bash
pip install -r requirements.txt
```

Download the compatible YOLO model weights according to the project setup instructions.

## 9. Running the Project

After implementing and configuring the project modules, start the detection program using:

```bash
python main.py
```

If the dashboard is implemented as a separate application, start it using the documented dashboard command.

Configure the camera source, virtual line position, GPIO pins, and sensor settings before running the system on the Raspberry Pi.

## 10. Expected Output

The completed system is intended to display:

- Detected people with bounding boxes and tracking IDs
- Entry and exit events
- Estimated classroom occupancy
- Row occupancy status
- Environmental sensor readings
- Appliance-control status
- Dashboard analytics

Actual output depends on the implemented modules and connected hardware.

## 11. Applications

- Smart classrooms
- Educational institutions
- Energy-efficient buildings
- Occupancy monitoring
- Automated classroom management
- IoT-based building automation

## 12. Future Enhancements

- RFID-based identity verification
- Improved row-wise occupancy detection
- Real-time dashboard updates
- Energy-consumption measurement using power sensors
- Historical occupancy analytics
- Privacy-preserving video processing
- Edge AI acceleration

## 13. Limitations

Camera-based tracking may produce missed detections or ID switches in crowded scenes. Entry/exit counting also depends on correct camera placement and virtual-line configuration. Tracking IDs alone do not establish a student's identity; identity-based attendance requires an additional authentication mechanism.

## 14. Contributors

**Project:** AI-Based Smart Classroom Attendance and Energy Management System

**GitHub:** [sumanthrajmosa](https://github.com/sumanthrajmosa)

## 15. License

This project is distributed under the MIT License. See the `LICENSE` file for details.
