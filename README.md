# 🤖 Vision-Guided Robotic Arm

A computer vision-based robotic arm capable of automatically detecting, identifying, and sorting black and white objects using a webcam, OpenCV, Python, and Arduino.

---

## 📖 Project Overview

This project aims to build a **vision-guided pick-and-place robotic arm** that can:

- Detect objects inside the workspace.
- Identify object color (Black / White).
- Convert image coordinates into robot coordinates.
- Send coordinates from Python to Arduino.
- Compute inverse kinematics.
- Pick and place objects automatically.

This repository also serves as documentation of the entire engineering process, from system planning to final integration.

---

# 🎯 Objectives

The final system should be able to:

1. Capture images from a webcam.
2. Detect objects inside the workspace.
3. Classify object colors.
4. Calculate object coordinates.
5. Communicate with Arduino through Serial.
6. Move a 4-DOF robotic arm.
7. Automatically sort objects into predefined locations.

---

# 🛠 Hardware

- Arduino Uno
- 4x SG90 Servo Motors
- USB Webcam
- External 5V Power Supply (planned)
- Robotic Arm (4 DOF)

---

# 💻 Software

- Python 3
- OpenCV
- PySerial
- NumPy
- Arduino IDE

---

# 📂 Project Structure

```
RoboticArmProject/
│
├── Arduino/
│
├── Python/
│   ├── camera.py
│   ├── detection.py
│   ├── color.py
│   ├── mapping.py
│   ├── serial.py
│   ├── config.py
│   └── main.py
│
├── Calibration/
│
├── Documentation/
│
├── Test/
│
└── README.md
```

---

# ⚙ System Architecture

```
Camera
   │
   ▼
Python (Computer Vision)
   │
   ▼
Object Detection
   │
   ▼
Color Detection
   │
   ▼
Coordinate Mapping
   │
   ▼
Serial Communication
   │
   ▼
Arduino Uno
   │
   ▼
Inverse Kinematics
   │
   ▼
Servo Control
   │
   ▼
Pick and Place
```

---

# 🚀 Development Roadmap

- ✅ Milestone 0 — System Planning
- ✅ Milestone 1 — Camera Calibration
- ⏳ Milestone 2 — Object Detection
- ⏳ Milestone 3 — Color Detection
- ⏳ Milestone 4 — Multi-Object Detection
- ⏳ Milestone 5 — Object Selection
- ⏳ Milestone 6 — Camera-to-Robot Mapping
- ⏳ Milestone 7 — Python ↔ Arduino Communication
- ⏳ Milestone 8 — Servo Control
- ⏳ Milestone 9 — Inverse Kinematics
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — System Integration
- ⏳ Milestone 12 — Optimization
- ⏳ Milestone 13 — Testing
- ⏳ Milestone 14 — Documentation

---

# 📌 Current Status

**Current Milestone:** Milestone 2 — Object Detection

Completed:

- System planning
- Workspace design
- Camera calibration
- ROI configuration
- OOP software architecture
- Camera module implementation

---

# 🧩 Engineering Principles

- Modular architecture
- Object-Oriented Programming (OOP)
- Milestone-based development
- Easy to maintain
- Well documented
- Engineering-oriented approach

---

# 📜 License

This project is developed for educational purposes.

---

# 👨‍💻 Author

**Dumadio Digdaya**

Department of Electrical Engineering

Diponegoro University

Indonesia
