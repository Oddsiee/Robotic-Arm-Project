# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 1

- ✅ Milestone 0 selesai.
- ✅ Milestone 1 selesai.
- Resolusi kamera ditetapkan pada **1280 × 720**.
- Target FPS sistem **30 FPS**.
- ROI = Workspace.
- Seluruh algoritma computer vision bekerja pada ROI.
- Arsitektur Python menggunakan **OOP**.
- `main.py` berperan sebagai orchestrator.
- Seluruh konfigurasi dipusatkan pada `config.py` menggunakan `dataclass`.
- Class `Camera` bertanggung jawab terhadap webcam, ROI, overlay dasar, dan display.
- Tidak menggunakan pembagian zona di dalam ROI karena tidak memberikan manfaat algoritmik pada sistem saat ini.

---

## Keputusan Teknis Baru

### Decision #002
Seluruh modul Python menggunakan OOP.

### Decision #003
Resolusi standar kamera adalah **1280 × 720**.

### Decision #004
Target frame rate sistem adalah **30 FPS**.

### Decision #005
Seluruh konfigurasi sistem dipusatkan pada `config.py` menggunakan `dataclass`.

### Decision #006
ROI = Workspace.

### Decision #007
Class `Camera` menangani webcam, ROI, overlay dasar, dan display. Tidak dilakukan pemisahan `Overlay` dan `Display`.

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ⏳ Milestone 2 — Deteksi Objek
- ⏳ Milestone 3 — Deteksi Warna
- ⏳ Milestone 4 — Deteksi Banyak Objek
- ⏳ Milestone 5 — Pemilihan Objek
- ⏳ Milestone 6 — Camera to Robot Mapping
- ⏳ Milestone 7 — Python ↔ Arduino Serial
- ⏳ Milestone 8 — Kontrol Servo
- ⏳ Milestone 9 — Inverse Kinematics
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
