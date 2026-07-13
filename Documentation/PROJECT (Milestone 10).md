# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 10

- ✅ Milestone 10 selesai.
- Dibuat `Arduino/FinalProgram/FinalProgram.ino` — sketch Arduino **final/produksi**, berbeda dari `ServoControl.ino` (Milestone 8) yang cuma sweep test satu kali jalan. Satu perintah serial (`color,base,shoulder,elbow`, protokol yang sama persis dari Milestone 9) sekarang memicu **satu siklus penuh** pick → drop → home, dan Arduino cuma membalas **satu** `DONE` di akhir seluruh siklus, bukan per-langkah.
- **Konsep "hover" untuk turun/naik ke objek** diselesaikan tanpa menambah rumus IK baru: posisi HOME shoulder/elbow (yang sudah ada sejak awal) direuse sebagai posisi hover — base selalu berputar ke target dulu selagi shoulder/elbow masih di HOME (otomatis ngambang di atas meja), baru setelah itu shoulder/elbow turun ke sudut hasil IK. `InverseKinematics.compute()` di Python **tidak disentuh sama sekali** — rumus yang sudah tervalidasi fisik di Milestone 9 (Decision #044) tetap utuh.
- Titik **drop zone hitam & putih** ditetapkan sebagai **konstanta hardcoded** di Arduino (bukan hasil mapping/IK), ditentukan manual oleh Odi lewat pengukuran fisik langsung (kirim command manual via serial monitor, amati posisi capit, iterasi sampai pas).
- **Urutan gerak per siklus** (base dulu → delay → turun → grip/lepas → naik → base berikutnya) sengaja dibuat sekuensial per-servo, bukan simultan, dan sengaja dibuat **pelan** (`SERVO_STEP_DELAY`/`SERVO_STEP_SIZE` diperlambat dari nilai default `ServoControl.ino`), karena body robot tidak kuat menahan gerakan cepat/hentakan.
- **Urutan turun/naik direvisi di tengah sesi**: desain awal shoulder-dulu-baru-elbow diganti jadi **elbow dulu baru shoulder**, di keempat fase yang menggerakkan shoulder+elbow bersamaan (turun ke pick, naik dari pick, turun ke drop, naik dari drop).
- **`BASE_HOME` direvisi dari 90° menjadi 0°**, berdasarkan hasil kalibrasi fisik final Odi. Ini men-supersede pernyataan Home Position di Milestone 0 (Section 9: "Base = 90°"). Konvensi arah base (0°=kanan/putih, 180°=kiri/hitam — Decision #047, Milestone 9) **tidak berubah**, yang berubah cuma titik "istirahat" default-nya.
- Konsekuensi dari `BASE_HOME = 0°` bertepatan dengan `DROP_BLACK_BASE = 0°`: pada siklus drop objek **hitam**, base secara fisik **tidak berpindah sama sekali** di antara fase "naik dari pick" dan "turun ke drop" — base sudah berada di posisi yang benar sejak awal. Bukan bug, hanya konsekuensi geometris dari nilai kalibrasi; `SETTLE_DELAY` tetap jalan di fase itu walau base diam (tidak mengganggu fungsi, hanya delay yang secara teknis tidak diperlukan untuk kasus ini).
- Parsing command serial di Arduino tetap manual (`indexOf`/`substring`/`toFloat()`), konsisten dengan pola yang sudah ditetapkan sejak Milestone 7 — tidak pakai `sscanf`.
- `main.py` dan `serial_comm.py` **tidak ada perubahan** dari Milestone 9 — protokol `color,base,shoulder,elbow` → `DONE` tetap sama persis, seluruh logika hover/drop/home sepenuhnya ditangani di sisi Arduino per satu command.
- Pengujian fisik dilakukan oleh Odi langsung di hardware; hasil dikonfirmasi sesuai (nilai `BASE_HOME` dan konstanta drop di atas adalah hasil akhir pasca-tes, bukan lagi placeholder).

---

## Keputusan Teknis Baru

### Decision #048
Posisi "hover" (dipakai base untuk berpindah dengan aman sebelum turun ke objek/drop zone) direalisasikan dengan **reuse posisi HOME shoulder & elbow yang sudah ada**, bukan menambah rumus/variabel IK baru untuk ketinggian.

**Alasan**
- `InverseKinematics.compute()` (Milestone 9) sengaja dirancang cuma untuk target di level meja (Tinggi=8.3cm fixed) dan sudah tervalidasi fisik penuh (Decision #044) — mengubahnya untuk menambah konsep ketinggian variabel berisiko merusak kalibrasi yang sudah presisi tanpa manfaat yang sepadan.
- Base yang berputar sementara shoulder/elbow di HOME sudah otomatis aman (capit terangkat dari meja), jadi tidak ada kebutuhan riil untuk hover angle yang berbeda dari HOME.

### Decision #049
Titik drop zone **BLACK** dan **WHITE** (masing-masing base/shoulder/elbow) adalah **konstanta hardcoded** di `FinalProgram.ino`, ditentukan manual oleh operator lewat pengukuran fisik langsung — bukan dihitung dari koordinat cm lewat `Mapping`/`InverseKinematics`.

**Alasan**
- Drop zone posisinya tetap (tidak berubah-ubah seperti posisi objek yang dideteksi kamera), sehingga tidak ada manfaat menghitungnya lewat pipeline vision+IK setiap siklus — konstanta lebih sederhana dan lebih cepat dieksekusi.
- Konsisten dengan pola kalibrasi manual yang sudah dipakai di proyek ini (mis. HSV threshold Milestone 3, homography Milestone 6) — nilai akhir hasil trial-and-error fisik disimpan sebagai konstanta di kode, bukan dihitung ulang tiap saat.

### Decision #050
Struktur satu siklus pick-and-place: **base gerak duluan → delay settle → shoulder/elbow turun → grip/lepas → shoulder/elbow naik → (ulangi untuk drop) → base kembali ke home**. Servo digerakkan **sekuensial satu-satu**, bukan simultan.

**Alasan**
- Base gerak duluan sebelum shoulder/elbow turun mencegah capit menyenggol objek/workspace lain saat masih dalam perjalanan menuju target.
- Gerakan sekuensial (bukan simultan) dipilih supaya desain awal tetap sederhana dan aman; optimasi ke arah gerakan simultan/lebih cepat sengaja ditunda ke Milestone 12 (Optimisasi), bukan diprioritaskan di sini.

### Decision #051
Urutan gerak turun/naik untuk shoulder+elbow direvisi menjadi **elbow bergerak duluan, baru shoulder** (bukan shoulder-dulu seperti desain awal sesi ini), berlaku di seluruh fase turun/naik (pick maupun drop).

**Alasan**
- Preferensi eksplisit Odi berdasarkan pertimbangan fisik lengan yang belum sepenuhnya diketahui dari luar kode (kemungkinan terkait distribusi beban/momen saat menekuk).
- Dicatat sebagai keputusan final karena mengubah lintasan gerak capit secara nyata dibanding desain sebelumnya — kalau ke depannya perlu direvisi lagi (mis. karena resiko nyenggol di titik tertentu), catat sebagai revisi baru, jangan diam-diam diubah balik.

### Decision #052
`BASE_HOME` direvisi dari **90° menjadi 0°**, berdasarkan hasil kalibrasi fisik final. Ini men-**supersede** pernyataan Home Position untuk base di Milestone 0 (Section 9).

**Alasan**
- Ditentukan Odi lewat pengujian fisik langsung sebagai titik istirahat yang lebih sesuai untuk siklus pick-and-place yang sebenarnya dijalankan.
- Konvensi arah base (0°=kanan/searah drop putih, 180°=kiri/searah drop hitam — Decision #047, Milestone 9) tetap berlaku apa adanya; yang berubah murni titik default/istirahatnya, bukan konvensi arahnya.

**Dampak**
- Karena `DROP_BLACK_BASE = 0°` sama dengan `BASE_HOME` yang baru, base tidak berpindah sama sekali selama siklus drop objek hitam antara fase "naik dari pick" dan "turun ke drop". Diverifikasi ini bukan bug — murni konsekuensi geometris, tidak mempengaruhi fungsi.

### Decision #053
`Arduino/FinalProgram/FinalProgram.ino` adalah sketch **produksi final**, terpisah dari `ServoControl.ino` (Milestone 8, khusus sweep test one-shot). Satu command serial diterima = satu siklus penuh pick→drop→home dieksekusi Arduino, dibalas dengan **satu** `DONE` di akhir siklus. Protokol serial (`color,base,shoulder,elbow` → `DONE`) tidak berubah dari Milestone 9.

**Alasan**
- Memisahkan sketch test (M8) dari sketch produksi (M10) menjaga `ServoControl.ino` tetap berguna sebagai referensi/debug dasar tanpa tercampur logika siklus penuh.
- Membiarkan seluruh logika hover/drop/home sepenuhnya di sisi Arduino, tanpa mengubah `main.py`/`serial_comm.py`, mempertahankan pembagian tanggung jawab yang sudah ditetapkan sejak Milestone 0: Python murni vision+mapping+IK, Arduino murni eksekusi gerakan.
- Satu `DONE` per siklus penuh (bukan per-langkah) menjaga kompatibilitas dengan pola handshake blocking Python yang sudah ada (Decision #030, #031) — `main.py` tidak perlu tahu apa-apa soal sub-langkah di dalam satu siklus.

### Decision #054
Kecepatan gerak servo sengaja diperlambat dari nilai default `ServoControl.ino`: `SERVO_STEP_DELAY` 15→20ms, `SERVO_STEP_SIZE` 2°→1° per step.

**Alasan**
- Body robot secara fisik tidak kuat menahan gerakan cepat/hentakan (keterangan langsung dari Odi) — memperhalus step size dan menaikkan delay antar step mengurangi resiko stress mekanis di sambungan lengan.
- Nilai ini disadari masih bisa ditune lebih lanjut (baik dipercepat maupun diperlambat lagi); tidak dianggap final/kaku, sengaja tetap sebagai konstanta terpisah supaya gampang diubah tanpa menyentuh logika siklus.

---

## Catatan / Technical Debt

- **Validasi batas workspace** (menolak target di luar jangkauan fisik lengan sebelum dikirim ke servo) — ditunda sejak Milestone 6 ke Milestone 9 (Decision #027), lalu di Milestone 9 belum sempat dikerjakan. **Masih belum diimplementasikan di Milestone 10 ini juga.** Perlu diputuskan di milestone mendatang (kemungkinan besar relevan di Milestone 11 saat integrasi otomatis, supaya sistem tidak mengirim command dengan sudut hasil IK yang invalid/di luar jangkauan tanpa disadari).
- `RobotConfig` di `config.py` masih berisi nilai placeholder lama yang tidak dipakai (dicatat sejak Milestone 9) — belum dibersihkan.
- Dokumentasi Milestone 0 (Section 9, Home Position) menyatakan Base = 90°, sekarang **usang** — perlu direvisi/diberi catatan silang ke Decision #052 di update berikutnya kalau Milestone 0 pernah diaudit ulang.

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
- ✅ Milestone 9 — Inverse Kinematics
- ✅ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot *(lagi di sini sekarang)*
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi