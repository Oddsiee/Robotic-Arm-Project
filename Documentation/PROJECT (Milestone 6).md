# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 6

- ✅ Milestone 0 selesai.
- ✅ Milestone 1 selesai.
- ✅ Milestone 2 selesai.
- ✅ Milestone 3 selesai.
- ✅ Milestone 4 selesai.
- ✅ Milestone 5 selesai.
- ✅ Milestone 6 selesai.
- Mapping pixel → robot awalnya didesain pakai model linear per-axis (`robot = scale * pixel + offset`) dengan asumsi kamera terpasang benar-benar top-down. Asumsi ini dicabut di tengah jalan karena kepresisian mounting kamera tidak bisa dijamin, sehingga desain direvisi memakai **homography** (`cv2.getPerspectiveTransform`) yang mengkompensasi distorsi perspektif ringan.
- Konvensi sumbu robot frame yang sebelumnya belum ditetapkan di Milestone 0 (cuma lokasi origin) sekarang dilengkapi: **X+ mengarah ke drop area putih (kanan)**, **Y+ menjauh dari base ke arah workspace/ROI**, origin tetap di pusat servo base.
- Kalibrasi dilakukan lewat tool terpisah, `calibration_mapping.py`, dengan pola yang sama seperti `calibration_color.py` (Milestone 3): reuse class yang sudah ada (`Detection`), independen dari `main.py`, hasil di-print ke console untuk disalin manual ke `config.py`.
- Kalibrasi menggunakan **4 titik pojok ROI** dengan objek fisik nyata, exact solve (bukan least-squares) karena jumlah titik pas 4. Trade-off yang disadari: tidak ada redundansi data, jadi presisi pengukuran manual di tiap titik jadi krusial.
- Pengukuran koordinat robot (cm) di tiap titik kalibrasi dilakukan pakai **alas kertas grid berpetak 1×1 cm (±0.1 cm)** yang originnya diposisikan di pusat servo base dan sumbunya disejajarkan ke konvensi X+/Y+ di atas — bukan diukur manual pakai penggaris + trigonometri.
- Class `Mapping` (`mapping.py`) hanya bertanggung jawab menerapkan matriks homography yang sudah jadi (`pixel_to_robot()`); seluruh proses fitting ada di `calibration_mapping.py`, konsisten dengan pemisahan tanggung jawab kalibrasi vs runtime yang sudah dipakai sejak Milestone 3.
- Ditambahkan `test_mapping.py` sebagai tool verifikasi terpisah (reuse `Detection` + `Mapping`) untuk mengecek akurasi mapping di titik-titik non-kalibrasi (terutama area tengah ROI) sebelum dianggap final. Disimpan permanen di `Python/` karena kalibrasi ulang kemungkinan akan diperlukan lagi ke depannya (mis. kalau mounting kamera bergeser).
- Validasi akurasi dilakukan manual: objek ditaruh di titik acak dalam ROI (bukan salah satu dari 4 titik kalibrasi), hasil `pixel_to_robot()` dibandingkan dengan posisi asli dari kertas grid — hasil dalam toleransi yang dapat diterima.
- Validasi batas workspace (menolak target yang di luar jangkauan fisik robot) sengaja **tidak** dikerjakan di milestone ini — ditunda ke Milestone 9, karena baru benar-benar relevan setelah inverse kinematics tersedia untuk menentukan jangkauan aktual.

---

## Keputusan Teknis Baru

### Decision #023 (direvisi selama sesi ini)
Mapping pixel → robot menggunakan **homography** (`cv2.getPerspectiveTransform`, matriks transformasi 3×3), bukan model linear independen per-axis.

**Alasan**
- Desain awal berasumsi kamera top-down sempurna sehingga scale + offset per axis dianggap cukup.
- Asumsi ini tidak bisa dijamin secara fisik (mounting kamera tidak presisi 100% top-down), sehingga ada distorsi perspektif ringan yang tidak tertangani oleh model linear per-axis.
- Homography mengkompensasi distorsi ini karena mentransformasikan koordinat lewat matriks perspektif penuh, bukan penskalaan independen tiap sumbu.

### Decision #024
Kalibrasi dilakukan lewat **penempatan objek fisik nyata** di titik-titik acuan, dengan pixel centroid ditangkap ulang memakai class `Detection` yang sudah ada dari Milestone 2 — bukan menandai titik secara manual di atas gambar statis.

**Alasan**
- Reuse `Detection` memastikan titik acuan kalibrasi diukur dengan pipeline deteksi yang sama persis dengan yang dipakai saat runtime, sehingga tidak ada mismatch antara kondisi kalibrasi dan kondisi operasional.

### Decision #025 (direvisi selama sesi ini)
Fitting homography menggunakan **exact solve 4 titik** (`cv2.getPerspectiveTransform`) — bukan least-squares dengan titik lebih banyak.

**Alasan**
- 4 titik adalah jumlah minimum yang dibutuhkan homography, dan dipilih untuk mempercepat proses kalibrasi fisik.
- Trade-off yang disadari sepenuhnya: karena sistem tidak over-determined, tidak ada redundansi untuk meredam kesalahan pengukuran di satu titik — akurasi kalibrasi jadi sangat bergantung pada presisi pengukuran manual tiap titik.

### Decision #026
Konvensi sumbu robot frame (yang sebelumnya belum lengkap di Milestone 0) ditetapkan: origin di pusat servo base, **X+ ke arah drop area putih (kanan)**, **Y+ menjauh dari base ke arah workspace/ROI**.

**Alasan**
- Milestone 0 hanya menetapkan lokasi origin, belum arah sumbu — ini krusial untuk homography maupun inverse kinematics (Milestone 9) supaya tidak terjadi mirroring pada mapping koordinat.

### Decision #027
Validasi batas workspace (menolak koordinat robot yang berada di luar jangkauan fisik lengan) **ditunda ke Milestone 9**, tidak dikerjakan di `Mapping`.

**Alasan**
- Jangkauan aktual robot baru bisa ditentukan secara akurat setelah inverse kinematics tersedia; menaruh validasi batas di `Mapping` sekarang berisiko memakai asumsi jangkauan yang salah dan perlu direvisi ulang nanti.

### Decision #028
`test_mapping.py` disimpan permanen di `Python/` (bukan file sekali pakai yang dibuang setelah verifikasi), reuse `Detection` + `Mapping` untuk mengecek akurasi mapping di titik non-kalibrasi.

**Alasan**
- Kalibrasi ulang kemungkinan besar akan dibutuhkan lagi di masa depan (mis. kalau mounting kamera bergeser), sehingga tool verifikasi independen dari `calibration_mapping.py` tetap berguna sebagai bagian dari alur kerja rutin, bukan hanya kebutuhan satu kali.

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ✅ Milestone 2 — Deteksi Objek
- ✅ Milestone 3 — Deteksi Warna
- ✅ Milestone 4 — Deteksi Banyak Objek
- ✅ Milestone 5 — Pemilihan Objek
- ✅ Milestone 6 — Camera to Robot Mapping
- ⏳ Milestone 7 — Python ↔ Arduino Serial
- ⏳ Milestone 8 — Kontrol Servo
- ⏳ Milestone 9 — Inverse Kinematics
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
