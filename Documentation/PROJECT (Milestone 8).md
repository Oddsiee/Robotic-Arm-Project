# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 8

- ✅ Milestone 8 selesai.
- Dibuat `Arduino/ServoControl/ServoControl.ino`, sketch **sweep test one-shot**: menggerakkan ke-4 servo secara berurutan sekali jalan di `setup()`, bukan kontrol interaktif keypress — cukup buat verifikasi wiring dan kontrol dasar sebelum Inverse Kinematics (Milestone 9).
- 3 servo positional (**shoulder, elbow, gripper** — SG90 180°) digerakkan lewat `moveServoSmooth()`: incremental step (`SERVO_STEP_SIZE` derajat per `SERVO_STEP_DELAY` ms), bukan `write(angle)` instan, supaya gerakan lebih halus dan mengurangi hentakan mekanis.
- Base (SG90 360° continuous rotation, Decision #029 Milestone 7) dikontrol lewat `baseRotate(direction, duration_ms)` — **time-based rotation**: set pulse arah, `delay()` sejumlah durasi, lalu kembali ke pulse stop. Ditangani total terpisah dari `moveServoSmooth()` karena interface-nya fundamental beda (arah + durasi vs target angle).
- Pengujian di hardware: semua servo bergerak sesuai ekspektasi. Base diam stabil di `BASE_STOP_PULSE = 90`, tidak perlu trim ulang.
- Ditemukan lewat pengujian: rotasi base dari 0°→180° butuh durasi berbeda tergantung arah — **~1650ms untuk CW**, **~1135ms untuk CCW** — dicatat sebagai `BASE_ROTATE_180_CW_MS` dan `BASE_ROTATE_180_CCW_MS`.
- Pin final (beda dari placeholder awal, disesuaikan wiring aktual): `PIN_BASE=8`, `PIN_SHOULDER=9`, `PIN_ELBOW=10`, `PIN_GRIPPER=11`.
- Urutan eksekusi sweep test (CW dulu baru CCW di kode) menghasilkan base berputar **CCW dulu secara fisik**, baru CW. Ini bukan kesalahan mapping yang perlu diperbaiki — operator mengonfirmasi urutan gerak fisik ini justru sesuai yang diinginkan, jadi label `BASE_CW`/`BASE_CCW` di kode dibiarkan apa adanya (label internal, tidak diklaim merepresentasikan arah jarum jam secara visual literal).

---

## Keputusan Teknis Baru

### Decision #035
Base servo (continuous rotation) dikontrol lewat **time-based rotation**: fungsi `baseRotate(direction, duration_ms)` — set pulse arah, tunggu durasi tertentu, lalu kembali ke pulse stop.

> **⚠️ Superseded oleh Decision #041.** Lihat bagian "Revisi Pasca-Milestone 8".

### Decision #036
Sketch `Arduino/ServoControl/ServoControl.ino` berupa **sweep test otomatis** (one-shot, dijalankan sekali di `setup()`), bukan kontrol interaktif keypress.

**Alasan**
- Cukup untuk memverifikasi tiap servo bergerak dan terpasang benar di pin yang tepat.
- Kontrol interaktif per-keypress (kalau memang dibutuhkan buat debugging manual nanti, mis. saat integrasi pick-and-place) bisa ditambahkan di milestone selanjutnya tanpa mengubah fungsi-fungsi dasar (`moveServoSmooth`, `baseRotate`) yang sudah teruji di sini.

### Decision #037
Base servo ditangani lewat fungsi terpisah (`baseRotate()`), tidak dipaksa masuk ke helper yang sama dengan 3 servo positional (`moveServoSmooth()`).

> **⚠️ Superseded oleh Decision #041.** Lihat bagian "Revisi Pasca-Milestone 8".

### Decision #038
Pin servo final: `PIN_BASE=8`, `PIN_SHOULDER=9`, `PIN_ELBOW=10`, `PIN_GRIPPER=11` — direvisi dari placeholder awal (9/10/11/6) sesuai wiring aktual yang dipakai operator.

*(Masih berlaku, tidak terdampak revisi hardware base.)*

### Decision #039
Kalibrasi durasi rotasi base dicatat sebagai referensi: **0°→180° (CW) ≈ 1650ms**, **180°→0° (CCW) ≈ 1165ms**. Asimetri ini diterima sebagai karakteristik fisik servo continuous itu sendiri (bukan bug di kode), tidak dipaksa disamakan.

> **⚠️ Superseded oleh Decision #041.** Nilai ini tidak lagi relevan karena base bukan lagi continuous rotation. Dipertahankan di sini sebagai catatan historis.

### Decision #040
Label `BASE_CW`/`BASE_CCW` di kode diperlakukan sebagai **label internal arbitrer**, bukan representasi harfiah arah searah/berlawanan jarum jam secara visual.

> **⚠️ Superseded oleh Decision #041.** Base servo baru tidak lagi punya konsep arah CW/CCW kontinu — dikontrol lewat target angle seperti servo positional lainnya.

---

## Revisi Pasca-Milestone 8

### Decision #041 — Base servo diganti dari SG90 360° continuous rotation menjadi SG90 180° positional

Base servo secara fisik diganti dari SG90 360° (continuous rotation) menjadi SG90 180° (positional), menyusul rekomendasi sebelum masuk Milestone 9.

**Perubahan kode:**
- `Arduino/ServoControl/ServoControl.ino` direvisi: `baseRotate()`, `BaseDirection` enum, dan tiga pulsa kalibrasi (`BASE_STOP_PULSE`, `BASE_CW_PULSE`, `BASE_CCW_PULSE`) **dihapus total**.
- Base sekarang dikontrol lewat `moveServoSmooth()` yang sama persis dengan shoulder/elbow/gripper — target angle, bukan arah + durasi.
- Ditambahkan `BASE_HOME = 90`, ditulis di `setup()` bersamaan dengan servo positional lain.
- Sweep test base diperbarui: `0 → 180 → home`, konsisten dengan pola sweep shoulder/elbow.

**Alasan**
- Milestone 0 sejak awal sudah membatasi workspace base hanya **0°–180°** (area belakang robot = forbidden workspace) — kebutuhan rotasi penuh 360° sebenarnya tidak pernah ada, sehingga servo 180° positional sudah cukup untuk seluruh rentang gerak yang dibutuhkan.
- Menghapus kebutuhan strategi durasi-per-derajat untuk base yang sebelumnya jadi catatan terbuka sejak Decision #029 (Milestone 7) — output sudut dari Inverse Kinematics (Milestone 9) sekarang bisa langsung di-`write()` ke base, sama seperti shoulder/elbow, tanpa estimasi waktu.
- Menghilangkan ketidakpastian akibat asimetri durasi CW/CCW (Decision #039) yang bergantung pada tegangan, beban, dan keausan motor — servo positional punya feedback posisi internal (potensiometer) sehingga tidak butuh estimasi berbasis waktu sama sekali.
- Menyeragamkan kontrol seluruh 4 servo lewat satu helper (`moveServoSmooth()`), mengurangi permukaan kode dan sumber bug.

**Dampak ke Decision sebelumnya**
- **Decision #029** (Milestone 7, base = continuous rotation): superseded — base sekarang SG90 180° positional, sama seperti shoulder/elbow/gripper.
- **Decision #035, #037** (Milestone 8, `baseRotate()` + helper terpisah): superseded — base memakai `moveServoSmooth()` yang sama dengan servo positional lain.
- **Decision #039** (Milestone 8, kalibrasi durasi CW/CCW): superseded — nilai durasi tidak lagi relevan, dipertahankan sebagai catatan historis saja.
- **Decision #040** (Milestone 8, label CW/CCW arbitrer): superseded — konsep arah CW/CCW kontinu tidak lagi berlaku untuk base.

**Dampak ke Milestone 9 (Inverse Kinematics)**
- Base tidak lagi butuh "strategi tambahan" untuk menerjemahkan output IK ke gerakan servo (catatan terbuka sejak Decision #029). Model IK cylindrical (base azimuth + shoulder/elbow sebagai 2-link planar chain) yang sudah didesain **tidak perlu diubah** — hanya cara mengeksekusi sudut base ke hardware yang jadi lebih sederhana (`write(angle)` langsung, bukan estimasi durasi).

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
- ✅ Milestone 8 — Kontrol Servo *(direvisi: base diganti ke SG90 180° positional)*
- ⏳ Milestone 9 — Inverse Kinematics *(lagi di sini sekarang)*
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi