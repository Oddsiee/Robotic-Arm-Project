# PROJECT.md

# Robotic Arm Project

> **Single source of truth** — state final pasca Milestone 14.
> Terakhir diperbarui: 2026-07-16.

------------------------------------------------------------------------

# 1. Tujuan Proyek

Membangun **vision-guided robotic pick-and-place system** yang mampu:

-   Mendeteksi objek menggunakan kamera.
-   Mengidentifikasi warna objek (hitam dan putih).
-   Menentukan koordinat objek dalam satuan cm.
-   Mengirim sudut servo dari Python ke Arduino melalui Serial.
-   Menggerakkan lengan robot menggunakan inverse kinematics.
-   Memindahkan objek ke area tujuan sesuai warnanya secara **otomatis penuh**.

------------------------------------------------------------------------

# 2. Ruang Lingkup (Final)

-   Computer Vision dengan OpenCV (background subtraction + HSV thresholding)
-   ROI Detection (780×366 px)
-   Deteksi multi-objek + pemilihan (area terbesar)
-   Deteksi warna (BLACK / WHITE / UNKNOWN)
-   Camera-to-Robot Mapping (homography 3×3)
-   Serial Communication 115200 baud (Python ↔ Arduino)
-   Kontrol 4 Servo SG90 180° positional
-   Inverse Kinematics (dihitung di Python)
-   Dwell-time lock (debounce 2 detik)
-   Validasi batas workspace (WorkspaceError)
-   Dashboard UI Apple HIG (single-window compositor)
-   Pick and Place otomatis penuh

------------------------------------------------------------------------

# 3. Hardware (Final)

## Robotic Arm

-   4 DOF
-   Servo SG90 180° positional ×4
-   Gripper tipe capit

### Pin Configuration

  Servo     Pin
  --------- ----
  Base      8
  Shoulder  9
  Elbow     10
  Gripper   11

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

-   Webcam USB, fixed mount ~top-down
-   Resolusi: 1280 × 720 @ 30 FPS
-   Tinggi kamera ±24 cm dari meja
-   Jarak horizontal kamera ke base ±22 cm

------------------------------------------------------------------------

# 4. Workspace

-   Kamera dipasang hampir top-down.
-   ROI: 780×366 px (offset x=200, y=45).
-   Area deteksi berada di tengah workspace.
-   Area drop **hitam** di kiri (base ~0°).
-   Area drop **putih** di kanan (base ~170°).
-   Area breadboard dan Arduino merupakan **forbidden area**.

------------------------------------------------------------------------

# 5. Sistem Koordinat

## Robot Frame

-   Origin (0,0) berada tepat pada pusat servo base.
-   Satuan: cm.
-   X+ : ke kanan (arah drop putih).
-   Y+ : menjauh dari base (ke arah workspace).

## Camera Frame

-   Koordinat pixel dalam ROI (780×366).

## Servo Frame

-   Sudut servo dalam derajat (0°–180°).

Transformasi data:

```
Camera Frame (pixel) → Robot Frame (cm) → Servo Frame (derajat)
```

------------------------------------------------------------------------

# 6. Computer Vision Pipeline

```
Webcam (1280×720) → Crop ROI (780×366) → Grayscale + GaussianBlur
  → Background Subtraction (absdiff vs reference) → Threshold
    → Morphology (OPEN + CLOSE) → Contour Detection
      → Filter by min area → Sort left→right → Assign IDs
        → Color.classify() per contour (HSV, area terbatas)
          → Selection.select() (area terbesar, skip UNKNOWN)
```

------------------------------------------------------------------------

# 7. Arsitektur Software (Final)

## Python (12 file)

  File                       Class               Tanggung Jawab
  -------------------------- ------------------- ------------------------------------
  `main.py`                  —                   Orchestrator, loop otomatis
  `camera.py`                `Camera`             Webcam, ROI, FPS
  `detection.py`             `Detection`          Background subtraction, contour
  `color.py`                 `Color`              HSV classification
  `selection.py`             `Selection`          Pilih 1 objek dari N
  `mapping.py`               `Mapping`            Pixel → cm (homography)
  `inverse_kinematics.py`    `InverseKinematics`  IK solver + validasi
  `dwell_lock.py`            `DwellLock`          Debounce 2 detik
  `serial_comm.py`           `SerialComm`         Serial + handshake
  `dashboard.py`             `Dashboard`          UI compositor
  `config.py`                (dataclass ×9)       Semua konstanta

## Arduino (2 sketch)

  Sketch              Fungsi
  ------------------- -------------------------
  `ServoControl.ino`  Sweep test 4 servo
  `FinalProgram.ino`  Produksi: pick-and-place

## Tools (3 file)

  File                      Fungsi
  ------------------------- ---------------------------------
  `Calibration color.py`    Kalibrasi HSV threshold (trackbar)
  `calibration_mapping.py`  Kalibrasi homography (4 titik)
  `test_mapping.py`         Validasi mapping

------------------------------------------------------------------------

# 8. Komunikasi Serial (Final)

**Baud rate**: 115200

**Format command** (Python → Arduino):

    B,base_angle,shoulder_angle,elbow_angle\n
    W,base_angle,shoulder_angle,elbow_angle\n

**Format response** (Arduino → Python):

    DONE\n

**Handshake**: Blocking — Python mengirim command, menunggu `DONE`
(timeout 5 detik, max 3 retry), baru lanjut ke siklus berikutnya.

------------------------------------------------------------------------

# 9. Home Position (Final)

  Servo     Sudut Home
  --------- ------------
  Base      0° (direvisi dari 90°, Decision #052)
  Shoulder  90°
  Elbow     90°
  Gripper   90° (OPEN)

Siklus operasi:

```
Home → Detect → Dwell Lock → Pick → Drop → Home → (loop)
```

------------------------------------------------------------------------

# 10. Batas & Validasi

-   Base servo: 0°–180°.
-   Shoulder servo: 0°–180°.
-   Elbow servo: 0°–180°.
-   Target di luar jangkauan geometris lengan → `WorkspaceError` → skip siklus.
-   Area belakang robot (base ~90°–270°) → forbidden workspace.
-   Objek harus diam ≥2 detik sebelum diproses (DwellLock).

------------------------------------------------------------------------

# 11. Flowchart Sistem

```
START
  ↓
HOME
  ↓
CAPTURE CAMERA
  ↓
CROP ROI
  ↓
[HAS REFERENCE?] ──No──→ TUNGGU KEY 'r'
  ↓ Yes
OBJECT DETECTION
  ↓
[OBJECTS FOUND?] ──No──→ LOOP
  ↓ Yes
COLOR DETECTION
  ↓
OBJECT SELECTION (largest area, valid color)
  ↓
[SELECTED?] ──No──→ LOOP
  ↓ Yes
DWELL LOCK (≥2 detik stabil)
  ↓
[LOCKED?] ──No──→ LOOP
  ↓ Yes
PIXEL → ROBOT CM (homography)
  ↓
INVERSE KINEMATICS
  ↓
[VALID?] ──No──→ SKIP + LOG → LOOP
  ↓ Yes
SERIAL: SEND ANGLES
  ↓
WAIT ACK ("DONE")
  ↓
[ACK?] ──No──→ RETRY (max 3×) → STOP
  ↓ Yes
RESET DWELL LOCK
  ↓
LOOP
```

------------------------------------------------------------------------

# 12. Keputusan Teknis

66 keputusan teknis tercatat dari Milestone 0 hingga Milestone 12.
Lihat `Documentation/PROJECT (Milestone 14).md` untuk indeks lengkap.

------------------------------------------------------------------------

# 13. Technical Debt Tersisa

1.  ⚠️ **Power supply servo**: Servo masih dari Arduino, perlu external 5V + common ground.
2.  `RobotConfig` di `config.py`: nilai placeholder tidak terpakai.
3.  Batas fisik shoulder/elbow belum diverifikasi (asumsi 0°–180° penuh).
4.  Koreksi overshoot base spesifik hardware — perlu rekalibrasi kalau servo base diganti.
5.  Tool kalibrasi belum pakai Dashboard (3 window OpenCV terpisah).
6.  Ukuran dashboard hardcoded (800px total width).

------------------------------------------------------------------------

# 14. Changelog

## 2026-07-16 (Milestone 14)

-   Dokumentasi final: README.md, PROJECT.md, dan PROJECT (Milestone 14).md diperbarui.
-   Semua 66 keputusan teknis dikonsolidasi.
-   Struktur folder aktual didokumentasikan.
-   Technical debt tersisa dicatat eksplisit.

## 2026-07-08 (Milestone 0)

-   Membuat PROJECT.md sebagai dokumen utama proyek.
-   Menetapkan roadmap pengembangan berbasis milestone.
-   Mendokumentasikan spesifikasi awal sistem.

------------------------------------------------------------------------

# Catatan

Dokumen ini adalah referensi utama proyek. Semua perubahan desain,
keputusan teknis, dan progres implementasi akan diperbarui di sini agar
setiap sesi pengembangan tetap konsisten.
