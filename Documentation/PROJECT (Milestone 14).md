# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Milestone 14 — Dokumentasi Final

- ✅ Milestone 14 selesai.
- **README.md** diperbarui: progress checklist, struktur folder aktual, alur sistem, hardware specs, dan tech stack diselaraskan dengan kondisi final proyek.
- **PROJECT.md** diaudit dan diperbarui: seluruh section diselaraskan dengan realitas implementasi (bukan lagi state perencanaan Milestone 0).
- Semua **66 keputusan teknis** dari Milestone 0–12 dikonsolidasi dalam satu indeks di dokumen ini.
- Struktur folder aktual didokumentasikan (beserta file-file tools kalibrasi dan testing).
- Technical debt yang tersisa dicatat eksplisit sebagai catatan penutup.

---

## Status Final Proyek

| Milestone | Nama | Status |
|-----------|------|--------|
| M0 | Perencanaan Sistem | ✅ Selesai |
| M1 | Kalibrasi Kamera | ✅ Selesai |
| M2 | Deteksi Objek | ✅ Selesai |
| M3 | Deteksi Warna | ✅ Selesai |
| M4 | Deteksi Banyak Objek | ✅ Selesai |
| M5 | Pemilihan Objek | ✅ Selesai |
| M6 | Camera to Robot Mapping | ✅ Selesai |
| M7 | Python ↔ Arduino Serial | ✅ Selesai |
| M8 | Kontrol Servo | ✅ Selesai |
| M9 | Inverse Kinematics | ✅ Selesai |
| M10 | Pick and Place | ✅ Selesai |
| M11 | Integrasi Vision + Robot | ✅ Selesai |
| M12 | Optimisasi (Dashboard UI) | ✅ Selesai |
| M13 | Pengujian | ✅ Selesai (oleh Odi) |
| M14 | Dokumentasi | ✅ Selesai |

---

## Arsitektur Final

### Python (Vision + Mapping + IK + Serial)

```
Python/
├── main.py                  # Orchestrator — loop otomatis penuh
├── camera.py                # Webcam, ROI, FPS counter
├── detection.py             # Background subtraction + contour detection
├── color.py                 # HSV classification (BLACK / WHITE / UNKNOWN)
├── selection.py             # Memilih 1 objek dari banyak (area terbesar)
├── mapping.py               # Pixel → Robot cm (homography 3×3)
├── inverse_kinematics.py    # IK solver + WorkspaceError validation
├── dwell_lock.py            # Debounce — objek harus diam ≥ N detik
├── serial_comm.py           # Serial Python↔Arduino, blocking handshake
├── dashboard.py             # UI compositor Apple HIG (v3, ~550 baris)
├── config.py                # Semua konstanta tersentralisasi (dataclass)
│
├── Calibration color.py     # Tool: kalibrasi HSV threshold (trackbar)
├── calibration_mapping.py   # Tool: kalibrasi homography (4 titik)
├── test_mapping.py          # Tool: validasi hasil mapping
└── Robotic Arm Control Code.py  # Legacy: test awal keyboard→serial
```

### Arduino

```
Arduino/
├── ServoControl/
│   └── ServoControl.ino     # Sketch test: sweep test 4 servo
└── FinalProgram/
    └── FinalProgram.ino     # Sketch produksi: pick-and-place penuh
```

### Alur Data

```
Camera (1280×720)
  → Crop ROI (780×366)
    → Detection (background subtraction + morphology + contours)
      → Color.classify() per contour (HSV threshold, area terbatas)
        → Selection.select() (area terbesar dengan warna valid)
          → DwellLock (debounce 2 detik, posisi & warna stabil)
            → Mapping.pixel_to_robot() (homography 3×3)
              → InverseKinematics.compute() (+ validasi workspace)
                → SerialComm.send_angles_and_wait() (format: B/W,base,shldr,elbow)
                  → Arduino FinalProgram.ino
                    → Siklus: Home → Base→target → Turun → Grip → Naik
                      → Base→drop zone → Turun → Lepas → Naik → Home
                        → Balas "DONE" → Python lanjut loop
```

---

## Konsolidasi Keputusan Teknis (Decision #001–#066)

### Milestone 0 — Perencanaan
| # | Keputusan |
|---|-----------|
| #001 | Arduino Uno sebagai controller (cukup 4 servo, sederhana, mudah integrasi Python) |

### Milestone 1 — Kalibrasi Kamera
| # | Keputusan |
|---|-----------|
| #002 | Seluruh modul Python menggunakan OOP |
| #003 | Resolusi standar kamera: 1280×720 |
| #004 | Target FPS: 30 |
| #005 | Konfigurasi dipusatkan di `config.py` (dataclass) |
| #006 | ROI = Workspace |
| #007 | Class `Camera` menangani webcam, ROI, overlay dasar, dan display |

### Milestone 2 — Deteksi Objek
| # | Keputusan |
|---|-----------|
| #008 | Background subtraction (absolute difference) sebagai metode deteksi |
| #009 | Preprocessing: grayscale + GaussianBlur sebelum diff |
| #010 | Morphology (OPEN + CLOSE) untuk membersihkan mask |
| #011 | Minimum contour area sebagai filter noise |
| #012 | Objek diurutkan kiri→kanan berdasarkan koordinat x centroid |
| #013 | Centroid dihitung dari image moments (`cv2.moments`) |
| #014 | Reference frame ditangkap manual sekali di awal sesi (key `r`) |

### Milestone 3 — Deteksi Warna
| # | Keputusan |
|---|-----------|
| #015 | Klasifikasi warna: HSV thresholding |
| #016 | Threshold dibatasi hanya pada area contour (bukan seluruh ROI) |
| #017 | Warna yang didukung: BLACK, WHITE, UNKNOWN |
| #018 | Threshold dikalibrasi manual via `Calibration color.py` (trackbar) |

### Milestone 4 — Deteksi Banyak Objek
*(Multi-object detection terintegrasi di Detection.detect() — tidak ada keputusan teknis baru terpisah)*

### Milestone 5 — Pemilihan Objek
| # | Keputusan |
|---|-----------|
| #019 | Rule pemilihan: objek dengan area contour terbesar |
| #020 | Objek UNKNOWN di-skip, fallback ke kandidat berikutnya |
| #021 | Dependency injection: `Selection` menerima instance `Color`, tidak membuat sendiri |

### Milestone 6 — Camera to Robot Mapping
| # | Keputusan |
|---|-----------|
| #022 | Mapping: pixel → koordinat robot (cm) |
| #023 | Homography 3×3 (perspective transform), bukan linear scale+offset per axis |
| #024 | Kalibrasi: 4 titik pojok ROI + koordinat robot manual |
| #025 | Origin robot: pusat servo base (0,0) |
| #026 | X+ : ke arah drop putih (kanan), Y+ : menjauh dari base |
| #027 | Technical debt: validasi batas workspace → ditunda ke milestone lanjutan |

### Milestone 7 — Python ↔ Arduino Serial
| # | Keputusan |
|---|-----------|
| #028 | Baud rate: 115200 |
| #029 | Format protokol awal: `B,x,y\n` / `W,x,y\n` |
| #030 | Handshake blocking: kirim → tunggu ack → retry atau stop |
| #031 | ACK token: `DONE`, timeout 5 detik, max 3 retry |
| #032 | Parsing di Arduino: manual (`indexOf`/`substring`/`toFloat`), bukan `sscanf` |
| #033 | Delay 2 detik setelah connect untuk Arduino restart |

### Milestone 8 — Kontrol Servo
| # | Keputusan |
|---|-----------|
| #034 | Pin: Base=8, Shoulder=9, Elbow=10, Gripper=11 |
| #035 | Base diganti dari SG90 360° continuous → SG90 180° positional |
| #036 | Semua 4 servo sekarang jenis yang sama: SG90 180° positional |
| #037 | Gerakan: `moveServoSmooth()` — step kecil + delay antar step |
| #038 | Servo step: 1° per step, delay 15ms (ServoControl) / 9ms (FinalProgram) |
| #039 | `ServoControl.ino` = sketch test (sweep), `FinalProgram.ino` = sketch produksi |
| #040 | Gripper: OPEN=90°, CLOSE=5° |
| #041 | Batas servo positional: 0°–180° |

### Milestone 9 — Inverse Kinematics
| # | Keputusan |
|---|-----------|
| #042 | IK dihitung di Python (sebelumnya direncanakan di Arduino) |
| #043 | Konstanta geometri arm hasil kalibrasi fisik: Tinggi=8.3, L1=7, L2=12 |
| #044 | Rumus IK: hasil trial-and-error fisik Odi, tidak boleh diubah tanpa validasi ulang |
| #045 | Protokol serial diperbarui: `B,base,shoulder,elbow\n` |
| #046 | Offset shoulder: 155° dan 87° adalah konstanta kalibrasi spesifik hardware |
| #047 | Konvensi arah base: 0° = kanan (drop putih), 180° = kiri (drop hitam) |

### Milestone 10 — Pick and Place
| # | Keputusan |
|---|-----------|
| #048 | Posisi hover = HOME shoulder/elbow (90°/90°), tanpa rumus IK baru |
| #049 | Drop zone: konstanta hardcoded di Arduino, bukan hasil Mapping/IK |
| #050 | Urutan gerak: base dulu → delay → shoulder/elbow turun |
| #051 | Urutan turun/naik: elbow dulu, baru shoulder |
| #052 | BASE_HOME direvisi: 90° → 0° (supersede Milestone 0 Section 9) |
| #053 | FinalProgram.ino: 1 command = 1 siklus penuh, 1 balasan DONE |
| #054 | Kecepatan servo diperlambat: step 1°, delay 9ms |

### Milestone 11 — Integrasi Vision + Robot
| # | Keputusan |
|---|-----------|
| #055 | Trigger: keypress manual → loop otomatis penuh |
| #056 | Validasi workspace di `InverseKinematics.compute()` via `WorkspaceError` |
| #057 | Reference frame tidak di-capture ulang otomatis antar siklus |
| #058 | Dwell-time lock: objek harus diam ≥2 detik sebelum diproses |
| #059 | Koreksi overshoot base: piecewise (`+5` untuk <90°, `+angle/20` untuk ≥90°) |

### Milestone 12 — Optimisasi (Dashboard UI)
| # | Keputusan |
|---|-----------|
| #060 | Dashboard: 1 window komposit (Apple HIG), menggantikan 3 window OpenCV |
| #061 | Palet: iOS dark mode (#1C1C1E, #2C2C2E, #3A3A3C) |
| #062 | State-driven UI: `dashboard.update_state()` tiap frame |
| #063 | Log berlevel: 8 level dengan color-coded dot |
| #064 | Sidebar: 4 kartu independen + Mask toggle |
| #065 | Footer: SF-style key badges + Auto Mode indicator |
| #066 | `config.py` dibersihkan dari duplikasi class |

---

## Spesifikasi Final Hardware

| Komponen | Spesifikasi |
|----------|-------------|
| Controller | Arduino Uno |
| Servo Base | SG90 180° positional (Pin 8) |
| Servo Shoulder | SG90 180° positional (Pin 9) |
| Servo Elbow | SG90 180° positional (Pin 10) |
| Servo Gripper | SG90 180° positional (Pin 11) |
| Kamera | Webcam USB, fixed mount, ~top-down |
| Resolusi | 1280 × 720 @ 30 FPS |
| ROI | 780 × 366 px (offset x=200, y=45) |
| Tinggi kamera | ±24 cm dari meja |
| Jarak kamera ke base | ±22 cm horizontal |
| Link 1 (Base→Shoulder) | ±8 cm |
| Link 2 (Shoulder→Elbow) | ±6 cm |
| Link 3 (Elbow→Gripper pivot) | ±4 cm |
| Gripper (pivot→ujung capit) | ±10 cm |

## Spesifikasi Final Software

| Layer | Teknologi |
|-------|-----------|
| Vision | Python 3 + OpenCV (`cv2`) |
| Numerik | NumPy |
| Serial | PySerial |
| UI | OpenCV primitives (Apple HIG compositor) |
| Mikrokontroler | Arduino C++ (`Servo.h`) |
| Komunikasi | USB Serial, 115200 baud |
| Protokol | `B/W,base,shoulder,elbow\n` → `DONE\n` |

---

## Technical Debt Tersisa

1. **Power supply servo**: Seluruh servo masih mengambil daya dari Arduino. Harus dipindahkan ke power supply eksternal 5V dengan common ground sebelum penggunaan jangka panjang.

2. **`RobotConfig` di `config.py`**: Masih berisi nilai placeholder lama (`LINK1=8.0, LINK2=6.0, LINK3=4.0, GRIPPER=10.0`) yang tidak dipakai — bisa dibersihkan.

3. **Batas fisik shoulder/elbow**: Validasi workspace (Decision #056) masih pakai asumsi `0°–180°` penuh. Belum diverifikasi apakah lengan fisik punya batas lebih sempit (mis. mentok badan robot di sudut tertentu).

4. **Koreksi overshoot base**: Rumus koreksi (`+5`, `/20`, ambang `90°`) spesifik terhadap karakteristik fisik servo base saat ini. Kalau servo base diganti, perlu kalibrasi ulang.

5. **Tool kalibrasi**: `calibration_color.py`, `calibration_mapping.py`, `test_mapping.py` masih pakai 3 window OpenCV terpisah, bukan `Dashboard`. Tidak kritis karena hanya dipakai sesekali.

6. **Dokumentasi Milestone 0 usang**: Section 9 (Home Position) menyatakan Base = 90°, sudah di-supersede oleh Decision #052 (BASE_HOME = 0°). Section 8 (Komunikasi Serial) masih menunjukkan format lama `B,x,y` — sudah di-upgrade ke `B,base,shoulder,elbow` sejak Milestone 9.

7. **Ukuran dashboard hardcoded**: Total lebar dashboard = 800px (kamera 540 + sidebar 260). Kalau layar lebih kecil, panel log bisa terpotong.

---

## Perubahan File

| File | Status | Keterangan |
|------|--------|------------|
| `Documentation/PROJECT (Milestone 14).md` | **Buat baru** | Dokumen ini |
| `README.md` | **Update** | Progress, struktur folder, alur, spesifikasi final |
| `PROJECT.md` | **Update** | Diselaraskan dengan state final |

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ✅ Milestone 2 — Deteksi Objek
- ✅ Milestone 3 — Deteksi Warna
- ✅ Milestone 4 — Deteksi Banyak Objek
- ✅ Milestone 5 — Pemilihan Objek
- ✅ Milestone 6 — Camera to Robot Mapping
- ✅ Milestone 7 — Python ↔ Arduino Serial
- ✅ Milestone 8 — Kontrol Servo
- ✅ Milestone 9 — Inverse Kinematics
- ✅ Milestone 10 — Pick and Place
- ✅ Milestone 11 — Integrasi Vision + Robot
- ✅ Milestone 12 — Optimisasi (Dashboard UI)
- ✅ Milestone 13 — Pengujian (oleh Odi)
- ✅ Milestone 14 — Dokumentasi 🎉

---

**PROYEK SELESAI.** 🎯
