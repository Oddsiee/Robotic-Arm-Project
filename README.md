# Vision-Guided Robotic Arm

A 4-DOF robotic arm that uses a webcam and OpenCV to find black and white objects on a table, figure out where they are, and pick them up with an Arduino-controlled gripper. Built as a personal engineering project — computer vision on the Python side, kinematics and motor control on the Arduino side.

I'm documenting the whole build here as I go, milestone by milestone, rather than dumping a finished project at the end. So expect this README (and the code) to keep changing.

---

## What it's supposed to do

1. Grab frames from a webcam pointed down at the workspace.
2. Find objects inside a defined region of interest.
3. Tell black apart from white.
4. Convert the object's pixel position into real-world coordinates.
5. Send that over serial to the Arduino.
6. Run inverse kinematics to get servo angles.
7. Move the arm, pick the object up, and drop it in the correct zone — black on the left, white on the right.

Nothing fancier than that for now. No color beyond black/white, no stacking, no multiple arms.

---

## Hardware

- Arduino Uno
- 4x SG90 servos (base, shoulder, elbow, gripper)
- USB webcam, mounted roughly top-down over the workspace
- 4-DOF arm frame (base→shoulder ~8cm, shoulder→elbow ~6cm, elbow→gripper pivot ~4cm, pivot→tip ~10cm)

**Known issue:** the servos are currently powered straight off the Arduino, which is fine for testing one servo at a time but won't hold up once everything runs together. Needs to move to an external 5V supply with a shared ground before I get to full integration — noted here so I don't forget.

---

## Software

- Python 3 + OpenCV for the vision side
- PySerial for talking to the Arduino
- NumPy for the coordinate math
- Arduino IDE / Servo library on the microcontroller side

### Structure

```
RoboticArmProject/
│
├── Arduino/
│
├── Python/
│   ├── camera.py      # webcam, ROI, FPS overlay, display
│   ├── detection.py    # object detection
│   ├── color.py         # black/white classification
│   ├── mapping.py     # pixel → robot coordinates
│   ├── serial.py         # Python ↔ Arduino
│   ├── config.py       # all the tunable constants live here
│   └── main.py           # ties everything together
│
├── Calibration/
├── Documentation/
├── Test/
└── README.md
```

Python side is written OOP on purpose — one class per responsibility, `main.py` just orchestrates. All the magic numbers (resolution, ROI bounds, thresholds, etc.) live in `config.py` as a dataclass instead of being scattered across files, which has already saved me from a couple of "wait why did I hardcode that" moments.

---

## Pipeline

```
Camera → Crop ROI → Object Detection → Color Detection
       → Coordinate Mapping → Serial → Arduino
       → Inverse Kinematics → Servo → Pick / Place
```

---

## Where things stand

Working through this as a series of milestones, testing each one before moving to the next instead of trying to build the whole thing at once:

- [x] Milestone 0 — System planning (workspace layout, coordinate frames, serial protocol, architecture)
- [x] Milestone 1 — Camera calibration (1280×720, ROI locked in, stable FPS)
- [x] Milestone 2 — Object detection
- [ ] Milestone 3 — Color detection *(currently here)*
- [ ] Milestone 4 — Multi-object detection
- [ ] Milestone 5 — Object selection (deciding which object to grab when there's more than one)
- [ ] Milestone 6 — Camera-to-robot coordinate mapping
- [ ] Milestone 7 — Python ↔ Arduino serial link
- [ ] Milestone 8 — Servo control
- [ ] Milestone 9 — Inverse kinematics
- [ ] Milestone 10 — Pick and place
- [ ] Milestone 11 — Full integration
- [ ] Milestone 12 — Optimization (speed, accuracy, retry logic)
- [ ] Milestone 13 — Testing under different conditions
- [ ] Milestone 14 — Final documentation

---

## Notes on approach

Trying to keep this modular enough that each part (camera, detection, mapping, serial, kinematics) can be tested on its own before wiring it all together — mostly so debugging doesn't turn into guessing which of five subsystems is broken. Still very much a work in progress, so some of the folders above are placeholders for now.

---

## License

Built for educational purposes.

---

## Author

**Dumadio Digdaya**
Electrical Engineering, Diponegoro University, Indonesia
