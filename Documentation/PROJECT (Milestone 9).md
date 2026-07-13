# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 9

- ✅ Milestone 9 selesai.
- **Revisi arsitektur:** Inverse Kinematics dihitung sepenuhnya di **Python** (`inverse_kinematics.py`), bukan di Arduino. Ini merevisi arahan arsitektur sebelumnya yang menempatkan IK di Arduino — direvisi karena Odi memilih untuk menurunkan dan memvalidasi sendiri seluruh rumus geometri IK secara independen, dan lebih praktis diiterasi di Python (print, testing manual per titik) sebelum dikirim sebagai sudut jadi ke Arduino.
- Seluruh rumus IK **diturunkan dan divalidasi sendiri oleh Odi** lewat trial-and-error langsung di hardware (bukan hasil kalkulasi teoretis semata) — diuji di seluruh titik ekstrim ROI, capit jatuh presisi di titik yang dituju.
- Konstanta geometri arm hasil kalibrasi fisik final: **Tinggi (shoulder height) = 8.3 cm**, **L1 (shoulder→elbow) = 6.8 cm**, **L2 (elbow + gripper sebagai satu link rigid) = 11.64 cm**. Nilai ini berbeda dari placeholder awal yang sempat ada di `RobotConfig` (`config.py`) — dicatat sebagai technical debt di bagian bawah.
- Base angle dihitung pakai **`atan2(y_cm, x_cm)`**, bukan `arcsin(y/x)`, untuk menghindari domain error yang berpotensi muncul dari `arcsin`.
- Class `InverseKinematics` (`inverse_kinematics.py`) dibuat dengan satu method publik, `compute(x_cm, y_cm)`, yang mengembalikan `(base_angle, shoulder_angle, elbow_angle)` sebagai `float` Python biasa (bukan `numpy.float64`), konsisten dengan konvensi tipe data yang sudah dipakai modul lain (`mapping.py`, dll).
- `InverseKinematics` **tidak** bergantung pada `Mapping` maupun class lain — dia cuma nerima `x_cm, y_cm` sebagai parameter. `main.py` yang menyambungkan alur data: `Mapping.pixel_to_robot()` → `InverseKinematics.compute()` → `SerialComm.send_angles_and_wait()`, konsisten dengan pola orchestrator yang sudah dipakai sejak Milestone 5 (Decision #021).
- **Protokol serial direvisi**: dari `color,x,y` (koordinat robot cm, Milestone 0/7) menjadi `color,base,shoulder,elbow` (tiga sudut servo, derajat). Perubahan ini konsekuensi langsung dari IK yang sekarang dihitung di Python — Arduino tidak lagi perlu menerima koordinat cm sama sekali.
- Ditambahkan method baru `SerialComm.send_angles_and_wait()`, mengikuti pola handshake blocking + retry yang sama persis dengan `send_and_wait()` lama (Decision #030, #031 tetap berlaku, cuma isi pesannya yang berubah). `send_and_wait()` lama (protokol `color,x,y`) **tidak dihapus**, dipertahankan kalau masih dibutuhkan untuk testing/debug jalur lama.
- **`Arduino/SerialTest.ino` dihapus permanen** — menyelesaikan catatan outstanding sejak Milestone 7 (bukan disimpan sebagai referensi debug). Konten parsing-nya (pola `indexOf`/`substring`/`toFloat()`) tetap relevan sebagai referensi untuk sketch final di Milestone 10, cuma filenya sendiri sudah tidak dipertahankan.
- **Konvensi base servo terverifikasi fisik**: **0° = kanan (searah drop area putih)**, **180° = kiri (searah drop area hitam)**, **home = 90°**. Terverifikasi konsisten dengan konvensi sumbu robot X+ ke arah drop putih yang sudah ditetapkan di Decision #026 (Milestone 6) — tidak ada mirroring antara arah sudut base dan arah sumbu X+. Status `BASE_ANGLE_SIGN` yang sebelumnya "pending physical verification" sekarang **terverifikasi**.
- Sketch Arduino final yang menerima sudut, menjalankan `moveServoSmooth()` (reuse dari `ServoControl.ino`, Milestone 8), dan membalas `DONE` **sengaja belum dibuat di milestone ini** — masuk scope Milestone 10 (Pick and Place), karena melibatkan urutan gerak penuh (turun, grip, naik, taruh), bukan sekadar perhitungan sudut.

---

## Keputusan Teknis Baru

### Decision #042 (revisi arsitektur)
Inverse Kinematics dihitung sepenuhnya di **Python** (`inverse_kinematics.py`), bukan di Arduino.

**Alasan**
- Odi menurunkan dan memvalidasi sendiri seluruh rumus geometri IK; proses iterasi/debug (print antar-langkah, uji manual per titik ROI) jauh lebih praktis dilakukan di Python daripada re-flash Arduino berulang kali di tengah trial-and-error.
- Arduino cukup menerima sudut jadi dan mengeksekusinya lewat `moveServoSmooth()` yang sudah ada dari Milestone 8 — tidak perlu port ulang logika trigonometri ke C/C++.
- Merevisi arahan arsitektur sesi sebelumnya yang sempat menetapkan IK di Arduino; keputusan final ada di sini sebagai catatan resmi.

### Decision #043
Base angle dihitung menggunakan **`atan2(y_cm, x_cm)`**, bukan `arcsin(y_cm / x_cm)`.

**Alasan**
- `arcsin` punya risiko domain error / hasil ambigu di kuadran tertentu, sedangkan `atan2` menangani seluruh kuadran secara langsung dan aman terhadap `x_cm = 0`.

### Decision #044
Rumus final shoulder dan elbow angle, hasil kalibrasi fisik (bukan murni teoretis):

```
l = sqrt(x_cm² + y_cm²)
h = sqrt(l² + Tinggi²)
x = (h² - (L2² - L1²)) / (2h)

theta = degrees(acos(x / L1))
k = degrees(atan(l / Tinggi))
shoulder_angle = 100 - (155 - (theta + k))

alfa = degrees(acos((L1² + L2² - h²) / (2·L1·L2)))
elbow_angle = 90 - (alfa - 87)

base_angle = degrees(atan2(y_cm, x_cm))
```

Konstanta: `Tinggi = 8.3 cm`, `L1 = 6.8 cm`, `L2 = 11.64 cm`.

**Alasan**
- Konstanta offset (155° pada shoulder, 87° pada elbow) dan panjang link (`L1`, `L2`, `Tinggi`) merupakan hasil kalibrasi empiris di hardware asli, bukan hanya dari pengukuran/desain teoretis — divalidasi dengan menguji seluruh titik ekstrim ROI, hasil capit presisi jatuh di titik yang dituju.
- Rumus ini **tidak boleh diubah** tanpa validasi ulang di hardware, karena konstanta-konstanta di dalamnya spesifik terhadap kalibrasi fisik arm yang sekarang.

### Decision #045
Protokol serial direvisi dari `color,x,y` (koordinat robot cm) menjadi **`color,base,shoulder,elbow`** (tiga sudut servo, derajat).

**Alasan**
- Konsekuensi langsung dari Decision #042 — begitu IK dihitung di Python, Arduino tidak lagi punya keperluan menerima koordinat cm; yang dibutuhkan Arduino adalah sudut siap-pakai untuk langsung di-`write()` ke tiap servo.
- Method lama (`send_and_wait`, protokol `color,x,y`) dipertahankan (tidak dihapus) sebagai referensi/opsi testing, method baru (`send_angles_and_wait`) mengikuti pola handshake blocking + retry yang identik (Decision #030, #031).

### Decision #046
`Arduino/SerialTest.ino` **dihapus permanen**, tidak dipertahankan sebagai referensi debug.

**Alasan**
- Menyelesaikan catatan outstanding sejak Milestone 7 (Decision #034) yang sebelumnya belum diputuskan.
- Protokolnya sudah usang (parsing 2 angka koordinat cm, bukan 3 angka sudut) — mempertahankannya berisiko membingungkan sebagai referensi karena tidak lagi merepresentasikan alur data yang sebenarnya dipakai sistem.

### Decision #047
Konvensi base servo terverifikasi fisik: **0° = kanan (searah drop area putih)**, **180° = kiri (searah drop area hitam)**, **home = 90°**.

**Alasan**
- Konsisten dengan Decision #026 (Milestone 6): sumbu robot X+ mengarah ke drop area putih (kanan) — 0° berada di sisi X+ berarti tidak ada mirroring antara output `base_angle` dari IK dan arah fisik base servo.
- Menutup status "pending physical verification" pada `BASE_ANGLE_SIGN` yang sebelumnya masih berupa asumsi.

---

## Catatan / Technical Debt

- `RobotConfig` di `config.py` (`LINK1=8.0, LINK2=6.0, LINK3=4.0, GRIPPER=10.0`) berisi nilai **placeholder lama** yang tidak lagi dipakai — konstanta geometri aktual (`Tinggi=8.3, L1=6.8, L2=11.64`) sekarang disimpan langsung di dalam `InverseKinematics.__init__()`. Perlu dibersihkan/disinkronkan di milestone mendatang supaya tidak ada dua sumber kebenaran yang beda nilai untuk geometri arm yang sama.
- Sketch Arduino final (parsing sudut → `moveServoSmooth()` → balas `DONE`) belum dibuat — ditunda ke Milestone 10, karena scope-nya menyatu dengan urutan gerak pick-and-place penuh, bukan sekadar eksekusi sudut.

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
- ✅ Milestone 9 — Inverse Kinematics *(IK dihitung di Python)*
- ⏳ Milestone 10 — Pick and Place *(lagi di sini sekarang)*
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
