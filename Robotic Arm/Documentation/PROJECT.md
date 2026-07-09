# PROJECT.md

# Robotic Arm Project

> Living document untuk menjadi **single source of truth** selama
> pengembangan proyek.

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

Fitur utama:

-   Computer Vision dengan OpenCV
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

-   Servo Base ×1
-   Servo Shoulder ×1
-   Servo Elbow ×1
-   Servo Gripper ×1

Total servo: **4 buah**

## Controller

-   Arduino Uno

## Vision

-   Webcam

------------------------------------------------------------------------

# 4. Software

## Python

Digunakan untuk:

-   OpenCV
-   Pengolahan citra
-   Deteksi warna
-   Mapping koordinat
-   Serial Communication

## Arduino

Digunakan untuk:

-   Menerima data serial
-   Mengontrol servo
-   Menjalankan inverse kinematics
-   Eksekusi pick and place

------------------------------------------------------------------------

# 5. Arsitektur Sistem

Camera ↓ Python (Vision) ↓ Coordinate Mapping ↓ Serial Communication ↓
Arduino ↓ Inverse Kinematics ↓ Servo ↓ Pick and Place

------------------------------------------------------------------------

# 6. Roadmap

-   Milestone 0 --- Perencanaan Sistem
-   Milestone 1 --- Kalibrasi Kamera
-   Milestone 2 --- Deteksi Objek
-   Milestone 3 --- Deteksi Warna
-   Milestone 4 --- Deteksi Banyak Objek
-   Milestone 5 --- Pemilihan Objek
-   Milestone 6 --- Camera to Robot Mapping
-   Milestone 7 --- Python ↔ Arduino Serial
-   Milestone 8 --- Kontrol Servo
-   Milestone 9 --- Inverse Kinematics
-   Milestone 10 --- Pick and Place
-   Milestone 11 --- Integrasi Vision + Robot
-   Milestone 12 --- Optimisasi
-   Milestone 13 --- Pengujian
-   Milestone 14 --- Dokumentasi

------------------------------------------------------------------------

# 7. Struktur Folder

``` text
RoboticArmProject/
│
├── Arduino/
│   ├── ServoControl/
│   ├── InverseKinematics/
│   └── FinalProgram/
│
├── Python/
│   ├── CameraCalibration.py
│   ├── ObjectDetection.py
│   ├── ColorDetection.py
│   ├── CoordinateMapping.py
│   ├── SerialCommunication.py
│   └── Main.py
│
├── Calibration/
├── Documentation/
└── Test/
```

------------------------------------------------------------------------

# 8. Engineering Principles

-   Modular
-   Mudah diuji
-   Bertahap (milestone)
-   Terdokumentasi
-   Berorientasi engineering, bukan sekadar "berjalan"

------------------------------------------------------------------------

# 9. Keputusan Teknis

## Decision #001

Robot menggunakan **Arduino Uno**.

**Alasan**

-   Cukup untuk 4 servo.
-   Sederhana.
-   Mudah diintegrasikan dengan Python.

------------------------------------------------------------------------

Belum ada keputusan teknis lain yang bersifat permanen. Keputusan
berikutnya akan dicatat di bagian ini.

------------------------------------------------------------------------

# 10. Progress

## Status

Project baru memasuki tahap perencanaan.

Belum ada implementasi hardware maupun software.

------------------------------------------------------------------------

# 11. TODO

-   [ ] Finalisasi spesifikasi sistem
-   [ ] Finalisasi workspace
-   [ ] Finalisasi posisi kamera
-   [ ] Kalibrasi kamera
-   [ ] Deteksi objek
-   [ ] Deteksi warna
-   [ ] Mapping koordinat
-   [ ] Serial Communication
-   [ ] Kontrol servo
-   [ ] Inverse Kinematics
-   [ ] Pick and Place
-   [ ] Integrasi
-   [ ] Pengujian
-   [ ] Dokumentasi akhir

------------------------------------------------------------------------

# 12. Changelog

## 2026-07-08

-   Membuat PROJECT.md sebagai dokumen utama proyek.
-   Menetapkan roadmap pengembangan berbasis milestone.
-   Menetapkan struktur folder proyek.
-   Mendokumentasikan spesifikasi awal sistem.

------------------------------------------------------------------------

# Catatan

Dokumen ini adalah referensi utama proyek. Semua perubahan desain,
keputusan teknis, dan progres implementasi akan diperbarui di sini agar
setiap sesi pengembangan tetap konsisten.
