# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 5

- ✅ Milestone 5 selesai.
- Ditambahkan class `Selection`, bertanggung jawab memilih **satu objek** yang akan diproses dari sekian banyak objek hasil `Detection.detect()` (Milestone 4).
- Rule pemilihan: **area contour terbesar** (`obj["area"]`), sesuai representasi objek yang sudah ditetapkan di Decision #012 (Milestone 2).
- Kalau kandidat dengan area terbesar hasil klasifikasinya `UNKNOWN` (Color, Milestone 3), objek tersebut **di-skip**, dan kandidat berikutnya (area terbesar selanjutnya) dicoba — bukan dipaksa diproses sebagai UNKNOWN, bukan juga menolak seluruh frame.
- `Selection` **tidak** membuat instance `Color` sendiri — instance `Color` di-inject lewat constructor (`Selection(color)`), supaya satu instance `Color` yang sama dipakai konsisten di seluruh sistem (`main.py` sebagai orchestrator yang membuat & menyambungkan instance-instance ini).
- Tidak ditambahkan `SelectionConfig` baru di `config.py`, karena rule pemilihan (area terbesar, skip UNKNOWN) tidak punya nilai yang perlu di-tuning — konsisten dengan prinsip Decision #005 (config hanya untuk nilai yang memang bisa/butuh diubah).
- `main.py` diupdate: setelah `detection.detect()`, hasil objects dilempar ke `selection.select(roi, objects)`. Objek terpilih digambar dengan kotak hijau tebal + label `SELECTED #id COLOR` di window ROI (`Selection.draw_selected()`), terpisah dari visualisasi umum semua objek (`Detection.draw_objects()`).
- Key `p` di `main.py` diupdate: mencetak objek yang **terpilih** (bukan lagi seluruh list objek), dengan pesan berbeda untuk tiga kondisi: ada objek terpilih, ada objek tapi semua UNKNOWN, atau tidak ada objek sama sekali.
- Pengujian dilakukan pada kondisi: satu objek besar + beberapa objek kecil (objek besar terpilih), objek besar tapi UNKNOWN + objek kecil BLACK/WHITE (skip ke objek kecil), dan seluruh objek UNKNOWN (tidak ada yang terpilih) — hasil sesuai rule yang ditetapkan.

---

## Keputusan Teknis Baru

### Decision #019
Rule pemilihan objek adalah **area contour terbesar** (`obj["area"]`), bukan posisi kiri, posisi atas, atau jarak ke robot.

**Alasan**
- Paling sederhana untuk dihitung dan dijelaskan (tidak butuh referensi posisi robot yang baru akan ditetapkan di Milestone 6).
- `area` sudah tersedia langsung di struktur data objek sejak Milestone 4 (Decision #018), tidak perlu perhitungan tambahan.
- Cukup konsisten antar frame selama objek tidak berpindah drastis, karena area contour relatif stabil dibanding noise kecil di tepi objek.

### Decision #020
Kalau kandidat dengan area terbesar berstatus `UNKNOWN` (Color, Milestone 3), sistem **skip** ke kandidat area terbesar berikutnya, bukan memaksa memproses objek UNKNOWN maupun menolak seluruh frame.

**Alasan**
- Konsisten dengan Decision #013 (Milestone 3): `UNKNOWN` sengaja dipertahankan sebagai output valid supaya keputusan lanjutannya eksplisit di sini, di Milestone 5 — dan keputusannya adalah skip, bukan tebak warna.
- Robot tidak boleh mengambil objek yang warnanya tidak jelas (bisa salah taruh ke zona hitam/putih), tapi juga tidak perlu berhenti total kalau masih ada objek lain yang warnanya jelas.

### Decision #021
`Selection` menerima instance `Color` lewat **dependency injection** di constructor (`Selection(color)`), bukan membuat instance `Color` sendiri di dalam class.

**Alasan**
- Memastikan hanya ada **satu instance `Color`** yang dipakai di seluruh sistem, dibuat dan disambungkan oleh `main.py` sebagai orchestrator (Decision #003, Milestone 1) — konsisten dengan prinsip satu sumber kebenaran per komponen.
- Memudahkan pengujian `Selection` secara independen di masa depan (bisa suntik mock/stub `Color` tanpa perlu HSV asli).

---

## Roadmap

- ✅ Milestone 0 — Perencanaan Sistem
- ✅ Milestone 1 — Kalibrasi Kamera
- ✅ Milestone 2 — Deteksi Objek
- ✅ Milestone 3 — Deteksi Warna
- ✅ Milestone 4 — Deteksi Banyak Objek
- ✅ Milestone 5 — Pemilihan Objek
- ⏳ Milestone 6 — Camera to Robot Mapping
- ⏳ Milestone 7 — Python ↔ Arduino Serial
- ⏳ Milestone 8 — Kontrol Servo
- ⏳ Milestone 9 — Inverse Kinematics
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
