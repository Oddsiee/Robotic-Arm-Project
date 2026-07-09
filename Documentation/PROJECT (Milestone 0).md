# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan
> proyek.

------------------------------------------------------------------------

# 1. Tujuan Proyek

Membangun **vision-guided robotic pick-and-place system** yang mampu:

-   Mendeteksi objek menggunakan kamera.
-   Mengidentifikasi warna objek (hitam dan putih).
-   Menentukan koordinat objek.
-   Mengirim koordinat dari Python ke Arduino melalui Serial.
-   Menggerakkan lengan robot menggunakan inverse kinematics.
-   Memindahkan objek ke area tujuan sesuai warnanya secara otomatis.

------------------------------------------------------------------------

# 2. Ruang Lingkup

-   Computer Vision dengan OpenCV
-   ROI Detection
-   Deteksi objek
-   Deteksi warna
-   Camera-to-Robot Mapping
-   Serial Communication (Python ↔ Arduino)
-   Kontrol 4 Servo
-   Inverse Kinematics
-   Pick and Place otomatis

------------------------------------------------------------------------

# 3. Hardware

## Robotic Arm

-   4 DOF
-   Servo SG90 ×4
-   Gripper tipe capit

### Dimensi Link

  Link                                Panjang
  ----------------------------------- ---------
  Base → Shoulder                     ±8 cm
  Shoulder → Elbow                    ±6 cm
  Elbow → Titik Putar Gripper         ±4 cm
  Titik Putar Gripper → Ujung Capit   ±10 cm

## Controller

-   Arduino Uno

## Vision

-   Webcam (fixed mount)

## Technical Debt

Seluruh servo saat ini masih memperoleh daya dari sistem Arduino.
Sebelum tahap integrasi penuh, servo harus dipindahkan ke **power supply
eksternal 5V** dengan **common ground** ke Arduino.

------------------------------------------------------------------------

# 4. Workspace

-   Kamera dipasang hampir top-down.
-   Tinggi kamera ±24 cm dari meja.
-   Jarak horizontal kamera ke base robot ±22 cm.
-   Area deteksi berada di tengah workspace.
-   Area drop hitam berada di kiri.
-   Area drop putih berada di kanan.
-   Area breadboard dan Arduino merupakan **forbidden area**.

------------------------------------------------------------------------

# 5. Sistem Koordinat

## Robot Frame

-   Origin (0,0) berada tepat pada pusat servo base.
-   Satuan koordinat robot menggunakan cm.

## Camera Frame

-   Menggunakan koordinat pixel.

## Servo Frame

-   Menggunakan sudut servo (derajat).

Transformasi data:

Camera Frame → Robot Frame → Servo Frame

------------------------------------------------------------------------

# 6. Computer Vision

Semua algoritma OpenCV hanya bekerja pada **ROI (Region of Interest)**.

Pipeline:

Webcam → Crop ROI → Object Detection → Color Detection → Coordinate
Mapping

------------------------------------------------------------------------

# 7. Arsitektur Software

## Python

-   camera.py
-   detection.py
-   color.py
-   mapping.py
-   serial.py
-   main.py

## Arduino

-   servo
-   ik
-   serial
-   main

------------------------------------------------------------------------

# 8. Komunikasi Serial

Format data:

    B,x,y\n
    W,x,y\n

Contoh:

    B,12.4,8.1

Keterangan:

-   B = Black
-   W = White

------------------------------------------------------------------------

# 9. Home Position

-   Base = 90°
-   Shoulder = 90°
-   Elbow = 90°
-   Gripper = Open

Siklus operasi:

Home → Detect → Pick → Drop → Home

------------------------------------------------------------------------

# 10. Workspace Robot

-   Base servo dibatasi 0°--180°.
-   Area belakang robot dianggap forbidden workspace.
-   Target di luar workspace harus ditolak sebelum inverse kinematics
    dijalankan.

------------------------------------------------------------------------

# 11. Flowchart Sistem

Start

↓

Home

↓

Capture Camera

↓

Crop ROI

↓

Object Detection

↓

Color Detection

↓

Coordinate Mapping

↓

Serial

↓

Arduino

↓

Inverse Kinematics

↓

Servo

↓

Pick

↓

Drop

↓

Home

------------------------------------------------------------------------

# 12. Roadmap

-   ✅ Milestone 0 --- Perencanaan Sistem (**Selesai**)
-   ⏳ Milestone 1 --- Kalibrasi Kamera
-   ⏳ Milestone 2 --- Deteksi Objek
-   ⏳ Milestone 3 --- Deteksi Warna
-   ⏳ Milestone 4 --- Deteksi Banyak Objek
-   ⏳ Milestone 5 --- Pemilihan Objek
-   ⏳ Milestone 6 --- Camera to Robot Mapping
-   ⏳ Milestone 7 --- Python ↔ Arduino Serial
-   ⏳ Milestone 8 --- Kontrol Servo
-   ⏳ Milestone 9 --- Inverse Kinematics
-   ⏳ Milestone 10 --- Pick and Place
-   ⏳ Milestone 11 --- Integrasi Vision + Robot
-   ⏳ Milestone 12 --- Optimisasi
-   ⏳ Milestone 13 --- Pengujian
-   ⏳ Milestone 14 --- Dokumentasi

------------------------------------------------------------------------

# 13. Changelog

## 2026-07-08

-   Menyelesaikan Milestone 0.
-   Mendokumentasikan dimensi robotic arm.
-   Menetapkan layout workspace.
-   Menetapkan penggunaan ROI Detection.
-   Menetapkan origin koordinat di pusat servo base.
-   Menetapkan arsitektur software.
-   Menetapkan protokol serial `B,x,y`.
-   Menetapkan Home Position.
-   Menetapkan batas workspace robot.
-   Mencatat technical debt terkait power supply servo.
