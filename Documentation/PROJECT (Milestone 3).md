# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 3

- ✅ Milestone 0 selesai.
- ✅ Milestone 1 selesai.
- ✅ Milestone 2 selesai.
- ✅ Milestone 3 selesai.
- Klasifikasi warna menggunakan **HSV thresholding**, dibatasi hanya pada area **contour** hasil `Detection` (Milestone 2) — bukan pada seluruh ROI atau bounding box, supaya piksel background/alas tidak ikut memengaruhi keputusan warna.
- Untuk tiap contour valid, dihitung jumlah piksel yang cocok dengan threshold `BLACK` dan `WHITE` di dalam area contour tersebut; warna dengan jumlah piksel terbanyak yang dipilih (majority count).
- Jika tidak ada piksel yang cocok dengan threshold manapun, sistem mengembalikan `UNKNOWN` — tidak dipaksa menebak `BLACK` atau `WHITE`.
- Output sistem per objek: label **`BLACK`**, **`WHITE`**, atau **`UNKNOWN`**, ditampilkan sebagai bounding box + teks berwarna di window ROI.
- Kalibrasi threshold HSV dilakukan lewat tool terpisah, `calibration_color.py`, menggunakan **trackbar interaktif** (live tuning), bukan digabung ke `main.py` maupun editing manual `config.py` secara langsung tanpa preview.
- Nilai `HSVConfig` di `config.py` diperbarui berdasarkan hasil kalibrasi trackbar tersebut (nilai final tersimpan di `config.py`, tidak diduplikasi di sini, sesuai prinsip single source of truth).
- Class `Color` menangani seluruh logika klasifikasi warna, terpisah dari `Detection` dan `Camera` — konsisten dengan Decision #002 (OOP, satu class satu tanggung jawab).
- Pengujian dilakukan dengan objek hitam dan putih pada ROI; hasil klasifikasi BLACK/WHITE konsisten dan sesuai objek aslinya.

---

## Keputusan Teknis Baru

### Decision #012
Klasifikasi warna menggunakan **HSV thresholding yang dibatasi pada area contour**, bukan pada seluruh ROI atau bounding box persegi.

**Alasan**
- Bounding box persegi ikut menyertakan piksel background di sekitar objek, yang bisa mengganggu keputusan warna kalau alas dan objek punya HSV yang berdekatan.
- Masking langsung ke bentuk contour memastikan hanya piksel objek itu sendiri yang dihitung.

### Decision #013
Keputusan warna diambil lewat **majority pixel count** (jumlah piksel BLACK vs WHITE di dalam contour), dan mengembalikan `UNKNOWN` jika kedua hitungan nol.

**Alasan**
- Objek jarang 100% seragam warnanya karena bayangan/pantulan cahaya; majority count lebih tahan noise dibanding cek satu titik piksel saja.
- `UNKNOWN` sengaja dipertahankan sebagai output valid, bukan fallback ke `BLACK`/`WHITE`, supaya Milestone 5 (pemilihan objek) bisa memutuskan untuk skip objek yang warnanya ambigu daripada salah ambil.

### Decision #014
Kalibrasi HSV dilakukan lewat tool terpisah (`calibration_color.py`) dengan **trackbar interaktif**, dijalankan independen dari `main.py`.

**Alasan**
- Konsisten dengan Decision #009 (Milestone 2): operator butuh fokus penuh saat kalibrasi tanpa noise interaksi lain dari alur utama.
- `main.py` tetap berperan murni sebagai orchestrator (Decision #003, Milestone 1), tidak perlu tahu soal mekanisme kalibrasi.
- Trackbar memberi feedback visual langsung (window Black Mask / White Mask), mempercepat proses tuning dibanding trial-and-error lewat edit `config.py` berulang kali.

### Decision #015
Class `Color` menghasilkan output lewat method terpisah: `classify()` untuk logika, `draw_label()` untuk visualisasi.

**Alasan**
- Memisahkan logic dari rendering memudahkan pengujian `classify()` secara independen di masa depan (mis. untuk unit test), dan konsisten dengan pola yang sudah dipakai `Detection` (`detect()` vs `draw_contours()` / `draw_status()`).

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ✅ Milestone 2 — Deteksi Objek
- ✅ Milestone 3 — Deteksi Warna
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
