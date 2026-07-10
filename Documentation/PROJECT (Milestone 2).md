# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 2

- ✅ Milestone 0 selesai.
- ✅ Milestone 1 selesai.
- ✅ Milestone 2 selesai.
- Deteksi objek menggunakan **background subtraction** dengan reference frame (bukan MOG2 atau threshold warna langsung), karena alas workspace berwarna netral (abu-abu/kayu) dengan kontras sedang terhadap objek.
- Reference frame diambil secara manual oleh operator (tombol `r`) saat ROI dalam kondisi kosong, bukan otomatis saat startup.
- Pipeline deteksi: Grayscale → Gaussian Blur → Absolute Difference → Threshold → Morphology (Open + Close) → Contour Detection → Filter luas minimum.
- Output sistem: status **"Object Found"** atau **"No Object"**, ditampilkan sebagai overlay teks pada frame utama.
- Window debug **"Mask"** ditambahkan untuk mempermudah tuning threshold dan morphology secara visual.
- Seluruh parameter deteksi (`BLUR_KERNEL`, `DIFF_THRESHOLD`, `MORPH_KERNEL`, `MORPH_ITERATIONS`, `MIN_CONTOUR_AREA`, `CAPTURE_REF_KEY`) dipusatkan pada `DetectionConfig` di `config.py`, konsisten dengan Decision #005.
- Class `Detection` menangani seluruh logika computer vision Milestone 2, terpisah dari `Camera`.
- Parameter deteksi dituning ulang oleh operator berdasarkan kondisi alas kayu/abu-abu: `BLUR_KERNEL` dinaikkan dari 5 → 11, `DIFF_THRESHOLD` diturunkan dari 25 → 23.
- Pengujian dilakukan pada beberapa posisi ROI (pojok, tengah, tepi) dan kondisi objek ada/tidak ada; hasil stabil dan konsisten.
- Representasi objek diperkuat setelah pengujian awal terasa kurang robust: alih-alih memakai outline contour mentah (rentan bergerigi karena noise), setiap objek terdeteksi kini direpresentasikan sebagai **kotak imajiner (bounding box)** yang di-lock ke **centroid**.

---

## Keputusan Teknis Baru

### Decision #008
Deteksi objek menggunakan **background subtraction dengan reference frame** (bukan HSV threshold langsung atau MOG2 adaptif).

**Alasan**
- Alas workspace berwarna netral dengan kontras sedang, sehingga threshold warna langsung kurang reliable.
- Reference frame statis lebih sederhana dan cukup stabil selama pencahayaan tidak berubah drastis selama sesi berjalan.

### Decision #009
Reference frame diambil **manual oleh operator** melalui tombol `r`, bukan otomatis saat program dimulai.

**Alasan**
- Operator dapat memastikan ROI benar-benar kosong sebelum reference diambil.
- Menghindari reference frame yang tidak sengaja menangkap objek atau tangan operator.

### Decision #010
Preprocessing sebelum background subtraction menggunakan **Grayscale + Gaussian Blur**.

**Alasan**
- Meredam noise tekstur alas kayu/abu-abu yang dapat memicu false positive pada `absdiff`.

### Decision #011
Filtering hasil deteksi menggunakan kombinasi **Morphology (Open + Close) dan minimum contour area**, bukan hanya threshold mentah.

**Alasan**
- Morphology membersihkan noise kecil dan menutup lubang pada mask.
- Minimum contour area mencegah noise sisa terbaca sebagai objek valid.

### Decision #012
Setiap objek terdeteksi direpresentasikan sebagai **kotak imajiner (bounding box) yang di-lock ke centroid**, bukan outline contour mentah.

**Definisi:**
- **Ukuran kotak** = bounding box asli dari contour (`cv2.boundingRect` → `width`, `height`).
- **Posisi kotak (titik tengah)** = **centroid** objek, dihitung dari `cv2.moments` (`m10/m00`, `m01/m00`), bukan titik tengah bounding rect.
- Fallback: kalau `m00 == 0` (contour degenerate), titik tengah bounding rect dipakai sebagai pengganti.

**Alasan**
- Outline contour mentah bisa tidak beraturan/bergerigi akibat noise di tepi objek, sehingga kurang stabil sebagai representasi visual maupun titik acuan koordinat.
- Centroid dari moments mempertimbangkan distribusi seluruh piksel objek, sehingga lebih representatif dan stabil dibanding sekadar titik tengah geometris bounding rect.
- Titik tengah (centroid) ini menjadi **satu-satunya sumber kebenaran** untuk posisi objek pada milestone selanjutnya — dipakai untuk menghitung centroid banyak objek (Milestone 4), memilih objek mana yang diproses (Milestone 5), dan sebagai input mapping piksel → koordinat robot (Milestone 6). Jangan definisikan ulang titik tengah objek di milestone berikutnya; gunakan definisi ini.

**Struktur data objek** (dihasilkan oleh `Detection.get_objects(contours)`):
```python
{
    "centroid": (cx, cy),   # posisi titik tengah objek, dalam koordinat piksel ROI
    "width": w,              # lebar bounding box (piksel)
    "height": h,              # tinggi bounding box (piksel)
}
```

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ✅ Milestone 2 — Deteksi Objek
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
