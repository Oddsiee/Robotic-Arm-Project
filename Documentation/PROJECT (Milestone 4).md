# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 4

- ✅ Milestone 4 selesai.
- `Detection.detect()` sekarang mengembalikan **list of objects** (bukan lagi boolean `object_found` + list contour terpisah). Setiap objek berisi `id`, `centroid`, `bbox`, `contour`, dan `area`.
- Centroid tiap objek dihitung menggunakan **image moments** (`cv2.moments`), bukan titik tengah bounding box, supaya lebih akurat untuk bentuk objek yang tidak simetris.
- Setiap objek dibungkus **bounding box** (`cv2.boundingRect`). Bounding box merepresentasikan wilayah objek — seluruh area di dalam kotak dianggap milik objek yang sama.
- Objek diberi nomor urut berdasarkan **posisi x centroid, kiri ke kanan**, agar penomoran konsisten antar frame walau urutan contour dari OpenCV berubah-ubah.
- Visualisasi ROI (`draw_objects`) menggambar bounding box + titik centroid + label `#id (x,y)` per objek, menggantikan visualisasi contour outline dari Milestone 2.
- Status overlay pada frame utama diubah dari `Object Found` / `No Object` menjadi `Objects Found: N` / `No Object`.
- Ditambahkan key `p` pada `main.py` untuk mem-print daftar objek (`Object N (x,y)`) ke console, sesuai format output yang ditetapkan di spesifikasi Milestone 4.
- Pengujian dilakukan pada beberapa kondisi: objek tunggal, 2-3 objek berjauhan, objek berdekatan, objek di pojok ROI, dan objek sebagian keluar ROI — hasil stabil.

---

## Keputusan Teknis Baru

### Decision #016
Objek diurutkan berdasarkan koordinat **x centroid, kiri ke kanan**, dan penomoran (`id`) dibuat konsisten antar frame.

**Alasan**
- Urutan contour mentah dari `cv2.findContours` tidak dijamin konsisten antar frame walau posisi objek tidak berubah.
- Urutan kiri-ke-kanan langsung berguna sebagai salah satu kandidat rule pemilihan objek di Milestone 5.

### Decision #017
Centroid dihitung menggunakan **image moments** (`cv2.moments`), bukan titik tengah bounding box.

**Alasan**
- Moments memberikan titik pusat massa objek yang lebih representatif untuk bentuk tidak beraturan, dibanding sekadar tengah kotak pembungkus.

### Decision #018
Setiap objek direpresentasikan dengan **bounding box** (`cv2.boundingRect`) untuk keperluan visualisasi, disimpan terpisah dari `centroid` dan `contour` dalam struktur data objek. Klasifikasi warna (Decision #012, Milestone 3) tetap memakai `contour`, bukan `bbox`.

**Alasan**
- Bounding box mendefinisikan wilayah objek secara eksplisit untuk visualisasi (1 objek = 1 kotak).
- Bounding box persegi ikut menyertakan piksel background di sekitar objek (lihat Decision #012, Milestone 3), sehingga tidak dipakai untuk logika warna — hanya untuk tampilan dan kebutuhan geometris lain seperti cek batas objek.

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ✅ Milestone 2 — Deteksi Objek
- ✅ Milestone 3 — Deteksi Warna
- ✅ Milestone 4 — Deteksi Banyak Objek
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
