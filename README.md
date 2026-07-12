# Vision-Guided Robotic Arm

Lengan robot 4-DOF yang pakai webcam dan OpenCV buat nemuin objek hitam dan putih di atas meja, nentuin posisinya, terus ngambil objek itu pakai gripper yang dikontrol Arduino. Ini proyek pribadi, sisi computer vision-nya di Python, sisi kinematika dan kontrol motor di Arduino.

Aku dokumentasiin seluruh proses buildnya di sini sambil jalan, milestone demi milestone, bukan langsung dump proyek yang udah jadi di akhir. Jadi wajar kalau README (dan kodenya) ini masih akan terus berubah.

---

## Yang seharusnya bisa dilakuin

1. Ambil frame dari webcam yang diarahin ke bawah, ke area kerja.
2. Cari objek di dalam region of interest (ROI) yang udah ditentuin.
3. Bedain warna hitam dan putih.
4. Konversi posisi pixel objek jadi koordinat dunia nyata.
5. Kirim koordinat itu lewat serial ke Arduino.
6. Jalanin inverse kinematics buat dapetin sudut tiap servo.
7. Gerakin lengan, ambil objeknya, terus taruh di zona yang sesuai — hitam di kiri, putih di kanan.

Belum ada yang lebih kompleks dari itu buat sekarang. Belum ada warna selain hitam/putih, belum bisa nyusun objek, belum multi-arm.

---

## Hardware

- Arduino Uno
- 4x servo SG90 (base, shoulder, elbow, gripper)
- Webcam USB, dipasang kurang lebih top-down di atas area kerja
- Rangka lengan 4-DOF (base→shoulder ±8cm, shoulder→elbow ±6cm, elbow→pivot gripper ±4cm, pivot→ujung capit ±10cm)

**Technical debt yang masih ada:** servo-servo saat ini masih dapet daya langsung dari Arduino, yang oke-oke aja kalau testing satu servo, tapi bakal bermasalah begitu semuanya jalan bareng. Perlu dipindah ke power supply eksternal 5V dengan ground yang sama sebelum masuk tahap integrasi penuh — dicatat di sini biar nggak lupa.

---

## Software

- Python 3 + OpenCV buat sisi vision
- PySerial buat komunikasi ke Arduino
- NumPy buat perhitungan koordinat
- Arduino IDE / library Servo di sisi mikrokontroler

### Struktur

```
RoboticArmProject/
│
├── Arduino/
│
├── Python/
│   ├── camera.py      # webcam, ROI, overlay FPS, display
│   ├── detection.py    # deteksi objek
│   ├── color.py         # klasifikasi hitam/putih
│   ├── mapping.py     # pixel → koordinat robot
│   ├── serial.py         # komunikasi Python ↔ Arduino
│   ├── config.py       # semua konstanta yang bisa diatur ada di sini
│   └── main.py           # nyatuin semuanya
│
├── Calibration/
├── Documentation/
├── Test/
└── README.md
```

Sisi Python sengaja ditulis pakai OOP — satu class buat satu tanggung jawab, `main.py` cuma jadi orchestrator. Semua angka-angka yang bisa berubah (resolusi, batas ROI, threshold, dll) dipusatkan di `config.py` sebagai dataclass, bukan kesebar di banyak file — ini udah nyelametin aku dari beberapa momen "loh kok ini hardcode ya" pas ngoding.

---

## Alur Sistem

```
Camera → Crop ROI → Object Detection → Color Detection
       → Coordinate Mapping → Serial → Arduino
       → Inverse Kinematics → Servo → Pick / Place
```

---

## Progres Sekarang

Dikerjain bertahap lewat serangkaian milestone, tiap milestone diuji dulu sebelum lanjut ke berikutnya, daripada langsung bangun semuanya sekaligus:

- [x] Milestone 0 — Perencanaan sistem (layout workspace, sistem koordinat, protokol serial, arsitektur)
- [x] Milestone 1 — Kalibrasi kamera (1280×720, ROI udah fix, FPS stabil)
- [x] Milestone 2 — Deteksi objek
- [x] Milestone 3 — Deteksi warna
- [x] Milestone 4 — Deteksi banyak objek 
- [x] Milestone 5 — Pemilihan objek (nentuin objek mana yang diproses kalau ada lebih dari satu)
- [x] Milestone 6 — Mapping koordinat kamera ke robot
- [x] Milestone 7 — Komunikasi serial Python ↔ Arduino
- [ ] Milestone 8 — Kontrol servo *(lagi di sini sekarang)*
- [ ] Milestone 9 — Inverse kinematics
- [ ] Milestone 10 — Pick and place
- [ ] Milestone 11 — Integrasi penuh
- [ ] Milestone 12 — Optimisasi (kecepatan, akurasi, retry logic)
- [ ] Milestone 13 — Pengujian di berbagai kondisi
- [ ] Milestone 14 — Dokumentasi akhir

---

## Catatan Pendekatan

Diusahain tiap bagian (kamera, deteksi, mapping, serial, kinematika) bisa diuji sendiri-sendiri dulu sebelum digabung semua, biar kalau ada yang error, debugging-nya nggak jadi nebak-nebak dari lima subsistem yang mana. Masih jauh dari selesai, jadi beberapa folder di atas masih placeholder.

---

## Lisensi

Dibuat untuk keperluan edukasi.

---

## Author

**Dumadio Digdaya**
Teknik Elektro, Universitas Diponegoro, Indonesia
