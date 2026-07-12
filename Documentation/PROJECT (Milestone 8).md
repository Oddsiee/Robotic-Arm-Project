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

**Alasan**
- Base tidak punya sudut absolut secara fisik (Decision #029, Milestone 7), sehingga tidak bisa dikontrol dengan `write(angle)` seperti servo positional.
- Time-based rotation adalah strategi paling sederhana yang tidak butuh sensor tambahan (encoder/limit switch) — cukup untuk kebutuhan Milestone 8. Kalau ke depannya presisi time-based ini terbukti tidak cukup konsisten (mis. drift baterai/beban), opsi encoder/limit switch bisa dipertimbangkan ulang di Milestone 9.

### Decision #036
Sketch `Arduino/ServoControl/ServoControl.ino` berupa **sweep test otomatis** (one-shot, dijalankan sekali di `setup()`), bukan kontrol interaktif keypress.

**Alasan**
- Cukup untuk memverifikasi tiap servo bergerak dan terpasang benar di pin yang tepat.
- Kontrol interaktif per-keypress (kalau memang dibutuhkan buat debugging manual nanti, mis. saat integrasi pick-and-place) bisa ditambahkan di milestone selanjutnya tanpa mengubah fungsi-fungsi dasar (`moveServoSmooth`, `baseRotate`) yang sudah teruji di sini.

### Decision #037
Base servo ditangani lewat fungsi terpisah (`baseRotate()`), tidak dipaksa masuk ke helper yang sama dengan 3 servo positional (`moveServoSmooth()`).

**Alasan**
- Interface base (arah + durasi) fundamental beda dari interface servo positional (target angle) — memaksakan satu abstraksi seragam untuk 4 servo (1 di antaranya beda jenis) hanya menambah kompleksitas tanpa benefit nyata di skala proyek ini.

### Decision #038
Pin servo final: `PIN_BASE=8`, `PIN_SHOULDER=9`, `PIN_ELBOW=10`, `PIN_GRIPPER=11` — direvisi dari placeholder awal (9/10/11/6) sesuai wiring aktual yang dipakai operator.

### Decision #039
Kalibrasi durasi rotasi base dicatat sebagai referensi: **0°→180° (CW) ≈ 1650ms**, **180°→0° (CCW) ≈ 1165ms**. Asimetri ini diterima sebagai karakteristik fisik servo continuous itu sendiri (bukan bug di kode), tidak dipaksa disamakan.

**Alasan**
- Nilai ini akan jadi titik awal untuk menghitung estimasi durasi-per-derajat base di Milestone 9 (Inverse Kinematics), yang sebelumnya dicatat sebagai catatan terbuka di Milestone 7 (Decision #029) — base butuh "strategi tambahan" karena tidak bisa langsung `write(angle)`.
- Asimetri arah tidak dipaksakan simetris (mis. dengan trim ulang `BASE_CW_PULSE`/`BASE_CCW_PULSE`) karena servo continuous murah memang lazim punya karakteristik begini; lebih aman dikompensasi secara software (durasi berbeda per arah) daripada dipaksa lewat tuning pulsa yang belum tentu stabil di semua kondisi.

### Decision #040
Label `BASE_CW`/`BASE_CCW` di kode diperlakukan sebagai **label internal arbitrer**, bukan representasi harfiah arah searah/berlawanan jarum jam secara visual. Urutan eksekusi sweep test (CW dulu, lalu CCW) yang secara fisik menghasilkan CCW dulu baru CW, dibiarkan apa adanya karena dikonfirmasi operator sudah sesuai urutan gerak yang diinginkan.

**Alasan**
- Yang penting adalah konsistensi pemakaian (`BASE_CW_PULSE` selalu dipakai buat "arah A", `BASE_CCW_PULSE` buat "arah B") dan operator sudah tahu persis pulsa mana yang menghasilkan gerak fisik ke arah mana — nama variabel tidak perlu match literal ke arah jarum jam visual selama tidak menyebabkan salah pakai di kode lain.

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
- ⏳ Milestone 9 — Inverse Kinematics
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
