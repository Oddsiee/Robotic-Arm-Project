# Vision-Guided Robotic Arm

Lengan robot 3-DOF yang menggunakan webcam dan OpenCV untuk mendeteksi objek hitam dan putih di atas meja, menentukan posisinya dalam koordinat dunia nyata, lalu mengambil dan memindahkan objek ke zona drop berdasarkan warnanya — **sepenuhnya otomatis**.

Computer vision di Python (OpenCV), kinematika dan kontrol motor di Arduino Uno.

---

## Yang Dilakukan Sistem

1. Menangkap frame dari webcam yang diarahkan top-down ke area kerja.
2. Mendeteksi objek di dalam Region of Interest (ROI) via background subtraction.
3. Mengklasifikasikan warna objek: BLACK atau WHITE (HSV thresholding).
4. Memilih satu objek untuk diproses (area terbesar dengan warna valid).
5. Menunggu objek diam ≥2 detik (dwell-time lock / debounce).
6. Mengonversi koordinat pixel ke koordinat robot (cm) via homography 3×3.
7. Menghitung sudut servo (base, shoulder, elbow) via inverse kinematics.
8. Mengirim sudut ke Arduino via serial: `B/W,base,shoulder,elbow`.
9. Arduino menjalankan siklus pick-and-place penuh: Home → Pick → Drop → Home.
10. Membalas `DONE` ke Python, lalu sistem melanjutkan ke objek berikutnya.

---

## Hardware

| Komponen | Detail |
|----------|--------|
| Controller | Arduino Uno |
| Servo ×4 | SG90 180° positional (base, shoulder, elbow, gripper) |
| Kamera | Webcam USB, fixed mount ~top-down |
| Rangka | 3-DOF: base→shoulder ±8cm, shoulder→elbow ±6cm, elbow→gripper ±4cm |
| Power | ⚠️ Servo masih dari Arduino — perlu external 5V supply untuk produksi |

---

## Software Stack

| Layer | Teknologi |
|-------|-----------|
| Vision + Mapping + IK | Python 3 + OpenCV + NumPy |
| Serial | PySerial |
| UI Dashboard | OpenCV primitives (Apple HIG dark mode) |
| Kontrol Servo | Arduino C++ (`Servo.h`) |
| Protokol | USB Serial 115200 baud |

---

## Struktur Proyek

```
Robotic Arm/
│
├── Arduino/
│   ├── FinalProgram/
│   │   └── FinalProgram.ino      # Sketch produksi: pick-and-place penuh
│   └── ServoControl/
│       └── ServoControl.ino      # Sketch test: sweep test 4 servo
│
├── Python/
│   ├── main.py                   # Orchestrator — loop otomatis penuh
│   ├── camera.py                 # Webcam, ROI, FPS
│   ├── detection.py              # Background subtraction + contour
│   ├── color.py                  # Klasifikasi HSV (BLACK/WHITE)
│   ├── selection.py              # Pemilihan objek (area terbesar)
│   ├── mapping.py                # Pixel → Robot cm (homography)
│   ├── inverse_kinematics.py     # IK solver + WorkspaceError
│   ├── dwell_lock.py             # Debounce: objek harus diam ≥ N detik
│   ├── serial_comm.py            # Serial Python↔Arduino (blocking handshake)
│   ├── dashboard.py              # UI compositor Apple HIG (~550 baris)
│   ├── config.py                 # Semua konstanta (dataclass)
│   ├── Calibration color.py      # Tool: kalibrasi HSV threshold
│   ├── calibration_mapping.py    # Tool: kalibrasi homography (4 titik)
│   ├── test_mapping.py           # Tool: validasi mapping
│   └── Robotic Arm Control Code.py  # Legacy: test keyboard→serial
│
├── Documentation/                # 14 file milestone (M0–M14) + PROJECT.md
└── README.md
```

---

## Alur Sistem

```
Webcam → Crop ROI → Background Subtraction → Contour Detection
  → Color Classification (HSV) → Object Selection (largest area)
    → Dwell Lock (≥2s stable) → Pixel→Robot (Homography)
      → Inverse Kinematics → Serial (B/W,base,shoulder,elbow)
        → Arduino → Pick → Drop → Home → "DONE" → Loop
```

---

## Cara Menjalankan

### 1. Arduino
- Buka `Arduino/FinalProgram/FinalProgram.ino` di Arduino IDE
- Upload ke Arduino Uno
- Pastikan Serial Monitor **tidak** terbuka (port akan dipakai Python)

### 2. Python
```bash
pip install opencv-python numpy pyserial
cd Python
python main.py
```

### 3. Operasi
| Tombol | Fungsi |
|--------|--------|
| `r` | Tangkap reference frame (ROI kosong) — mengaktifkan mode otomatis |
| `m` | Toggle panel Mask Debug |
| `p` | Print objek terpilih ke log |
| `q` | Keluar |

Setelah reference frame diset, sistem berjalan **otomatis penuh**: deteksi → lock → pick → drop → ulangi.

---

## Progress

- [x] Milestone 0 — Perencanaan Sistem
- [x] Milestone 1 — Kalibrasi Kamera
- [x] Milestone 2 — Deteksi Objek
- [x] Milestone 3 — Deteksi Warna
- [x] Milestone 4 — Deteksi Banyak Objek
- [x] Milestone 5 — Pemilihan Objek
- [x] Milestone 6 — Camera to Robot Mapping
- [x] Milestone 7 — Python ↔ Arduino Serial
- [x] Milestone 8 — Kontrol Servo
- [x] Milestone 9 — Inverse Kinematics
- [x] Milestone 10 — Pick and Place
- [x] Milestone 11 — Integrasi Vision + Robot
- [x] Milestone 12 — Optimisasi (Dashboard UI)
- [x] Milestone 13 — Pengujian
- [x] Milestone 14 — Dokumentasi ✅

---

## Engineering Principles

- **Modular** — 1 class = 1 tanggung jawab
- **Config-driven** — semua konstanta di `config.py` (dataclass)
- **Dependency injection** — tidak ada `import` silang antar modul
- **State-driven UI** — dashboard menerima state, tidak melakukan side effect
- **Kalibrasi terpisah** — tool kalibrasi terisolasi dari kode runtime
- **Validasi defensive** — `WorkspaceError` mencegah command invalid ke servo

## Lisensi

Dibuat untuk keperluan edukasi dan pemuas rasa gabut liburan semester.

---

## Author

**Dumadio Digdaya**
Teknik Elektro, Universitas Diponegoro, Indonesia
