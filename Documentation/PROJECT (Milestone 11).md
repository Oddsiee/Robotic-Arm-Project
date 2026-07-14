# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 11

- ✅ Milestone 11 selesai.
- **Sistem sekarang berjalan full otomatis**, sesuai target awal yang ditetapkan di Milestone 0: `Camera → Detect → Color → Coordinate → Serial → Arduino → Servo → Pick → Place`, tanpa keypress manual per siklus (keypress `s` yang dipakai sejak Milestone 7-10 dihapus).
- `main.py` diubah dari trigger manual per-keypress menjadi **loop otomatis**: begitu reference frame diset (`r`), tiap frame diproses sendiri — `detect → select → (dwell lock) → map → IK → serial`.
- Ditambahkan **validasi batas workspace** di `InverseKinematics.compute()`, menyelesaikan technical debt yang tertunda sejak Milestone 6 (Decision #027) dan disebut ulang sebagai catatan terbuka di Milestone 10. Target yang secara geometris tidak terjangkau, atau menghasilkan sudut di luar batas fisik servo, di-skip (bukan dikirim ke Arduino, bukan meng-crash program).
- Ditambahkan **dwell-time lock (debounce)** lewat class baru `DwellLock` — objek harus diam di posisi & warna yang sama selama `LOCK_DURATION` detik (default 2.5s) sebelum sistem memprosesnya. Mencegah sistem memicu pick-and-place saat objek masih bergerak atau tangan operator masih ada di ROI.
- **Base angle dikoreksi dengan rumus tambahan** untuk kompensasi overshoot: operator (Odi) menemukan lewat pengujian fisik bahwa saat target membutuhkan sudut base di atas 90°, putaran base secara konsisten kurang dari yang diminta. Koreksi ini ditambahkan **setelah** `atan2(y_cm, x_cm)`, sebagai lapisan tambahan di atas rumus IK inti (Decision #044) — rumus geometri shoulder/elbow **tidak disentuh**.
- Reference frame **tidak** di-capture ulang otomatis antar siklus — tetap manual sekali di awal sesi (`r`), dengan asumsi kondisi lighting/background stabil selama sesi berjalan. Kalau lighting berubah drastis di tengah sesi, operator perlu re-capture manual.
- `config.py` dirapikan: ditemukan ada **dua definisi class `SerialConfig`** (duplikat tidak disengaja, kemungkinan sisa dari proses edit Milestone 7/9 — definisi kedua otomatis menimpa yang pertama di Python, jadi tidak menyebabkan bug fungsional, tapi membingungkan dibaca). Digabung jadi satu definisi. Ditambahkan section baru `DwellLockConfig` (`LOCK_DURATION`, `POSITION_TOLERANCE`).
- Pengujian dilakukan langsung oleh Odi di hardware: loop otomatis, dwell-time lock, validasi workspace, dan koreksi overshoot base semuanya dikonfirmasi bekerja sesuai ekspektasi di kondisi fisik nyata.

---

## Keputusan Teknis Baru

### Decision #055
Trigger pemrosesan objek diubah dari **keypress manual (`s`)** menjadi **loop otomatis**: begitu ada objek yang lolos seleksi (`Selection`) dan lolos dwell lock, sistem langsung memproses siklus `Mapping → InverseKinematics → SerialComm` tanpa menunggu input keyboard.

**Alasan**
- Ini adalah target eksplisit Milestone 11 sejak roadmap awal (Milestone 0): "Semuanya berjalan otomatis."
- `SerialComm.send_angles_and_wait()` sifatnya blocking (menunggu ack `DONE`, Decision #030), sehingga loop otomatis ini otomatis "berhenti sejenak" sendiri selama Arduino menjalankan siklus fisiknya — tidak dibutuhkan state machine atau threading tambahan untuk mencegah pengiriman command yang tumpang tindih.

### Decision #056
Ditambahkan validasi batas workspace di `InverseKinematics.compute()`, lewat exception baru `WorkspaceError`. Dua lapis pengecekan:
1. **Domain check** — argumen `acos()` (dipakai untuk menghitung sudut shoulder dan elbow) harus berada di rentang `[-1, 1]`; di luar itu berarti target secara geometris tidak terjangkau lengan (terlalu jauh/terlalu dekat).
2. **Servo limit check** — hasil akhir `base_angle`, `shoulder_angle`, `elbow_angle` harus berada di rentang `0°–180°` (batas fisik SG90 positional, konsisten dengan Decision #041, Milestone 8).

Kalau salah satu gagal, `main.py` menangkap `WorkspaceError`, mencetak pesan, dan **skip siklus itu saja** (`continue`) — tidak mengirim apapun ke Arduino, tidak menghentikan program.

**Alasan**
- Menyelesaikan technical debt yang tertunda sejak Milestone 6 (Decision #027) dan masih terbuka di catatan Milestone 10 — jadi lebih krusial sekarang karena sistem berjalan otomatis tanpa operator yang memantau tiap siklus secara manual.
- Validasi ditaruh di `InverseKinematics`, bukan di `Mapping` atau `main.py`, karena kedua jenis pengecekan (domain trigonometri maupun batas sudut akhir) hanya bisa dilakukan dengan nilai-nilai yang muncul di tengah perhitungan IK itu sendiri.
- Rumus IK inti (Decision #044) **tidak diubah sama sekali** — validasi murni membungkus, bukan mengganti, logika yang sudah tervalidasi fisik.

### Decision #057
Reference frame **tidak** di-capture ulang otomatis setelah tiap siklus pick-and-place selesai. Tetap manual sekali di awal sesi lewat tombol `r`, sama seperti sejak Milestone 2.

**Alasan**
- Asumsi kondisi lighting dan background workspace stabil selama satu sesi operasi — cukup ambil reference sekali di awal.
- Menghindari kompleksitas tambahan (mis. re-capture otomatis salah menangkap objek yang belum sempat terangkat penuh oleh arm) untuk manfaat yang belum tentu terasa dalam kondisi operasi normal proyek ini.

### Decision #058
Ditambahkan debounce berbasis **dwell-time lock**, lewat class baru `DwellLock` (`dwell_lock.py`). Objek harus tetap berada di posisi (dalam toleransi piksel) dan warna yang sama selama minimal `LOCK_DURATION` detik (default **2.5 detik**, `config.py` → `DwellLockConfig`) sebelum dianggap **locked** dan diproses ke `Mapping → InverseKinematics → SerialComm`. Lock di-reset setiap kali objek hilang, berpindah posisi di luar toleransi, ganti warna, atau setelah satu siklus selesai diproses (baik berhasil dikirim maupun kena `WorkspaceError`).

**Alasan**
- Tanpa debounce, sistem otomatis berisiko memicu pick-and-place saat objek masih bergerak (baru ditaruh, masih bergeser) atau saat tangan operator masih ada di ROI — keduanya bisa menghasilkan koordinat pick yang salah atau berbahaya secara fisik.
- Dipisah sebagai class tersendiri (bukan logic inline di `main.py`), konsisten dengan prinsip satu-class-satu-tanggung-jawab yang dipakai sejak Milestone 1 (Decision #007) — `DwellLock` murni menerima `selected` dari `Selection` dan tidak bergantung pada class lain, gampang diuji terpisah.
- Reset lock setelah tiap siklus (bukan hanya saat objek hilang) sengaja dipilih supaya kalau terjadi `WorkspaceError` berulang, sistem tidak mencoba ulang tiap frame secara spam — wajib nunggu dwell-time baru lagi sebelum retry.

### Decision #059
Ditambahkan koreksi tambahan pada `base_angle`, diterapkan **setelah** hasil mentah `atan2(y_cm, x_cm)`, untuk mengompensasi overshoot fisik base servo:

```
base_calculation = atan2(y_cm, x_cm)   # derajat

if base_calculation < 90:
    base_angle = base_calculation + 5
else:
    base_angle = base_calculation + (base_calculation / 8)
```

**Alasan**
- Ditemukan Odi lewat pengujian fisik: untuk target yang membutuhkan sudut base di atas 90°, base servo secara konsisten **kurang berputar** dari sudut yang diminta (undershoot fisik pada rentang tersebut). Koreksi piecewise ini kompensasi empiris terhadap perilaku itu — bukan hasil kalkulasi teoretis.
- Diterapkan sebagai lapisan tambahan di atas hasil `atan2` mentah, bukan mengubah rumus shoulder/elbow (Decision #044) — konsisten dengan prinsip proyek bahwa rumus geometri inti yang sudah tervalidasi fisik tidak disentuh kecuali ada validasi ulang di hardware untuk bagian yang spesifik itu saja.
- Koreksi ini diterapkan **sebelum** servo limit check (Decision #056) dijalankan, sehingga validasi batas `0°–180°` tetap mengevaluasi `base_angle` versi final (setelah koreksi), bukan `base_calculation` mentah.

**Catatan**
- Sama seperti offset 155°/87° di Decision #044, angka-angka di rumus koreksi ini (`+5`, `/8`, ambang `90°`) spesifik terhadap karakteristik fisik base servo yang sekarang terpasang — kalau servo base pernah diganti fisik, koreksi ini kemungkinan besar perlu dikalibrasi ulang, bukan diasumsikan tetap berlaku.

---

## Catatan / Technical Debt

- `RobotConfig` di `config.py` masih berisi nilai placeholder lama (`LINK1=8.0, LINK2=6.0, LINK3=4.0, GRIPPER=10.0`) yang tidak dipakai — dicatat sejak Milestone 9, masih belum dibersihkan.
- Batas servo `SHOULDER_MIN/MAX` dan `ELBOW_MIN/MAX` di `InverseKinematics` (Decision #056) masih memakai asumsi `0°–180°` penuh (sama dengan batas fisik SG90 positional secara umum). Belum diverifikasi apakah lengan fisik proyek ini punya batas lebih sempit di kedua servo tersebut (mis. mentok badan robot di sudut tertentu) — kalau ditemukan kasus seperti itu di pengujian lanjutan, sesuaikan konstantanya, bukan rumus IK.
- Duplikasi class `SerialConfig` di `config.py` (ditemukan dan dibersihkan di milestone ini) menandakan perlu lebih hati-hati saat merge/edit manual `config.py` ke depannya — tidak ada mekanisme otomatis (mis. linter) yang mendeteksi duplikasi definisi class di proyek ini saat ini.

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
- ✅ Milestone 11 — Integrasi Vision + Robot *(full otomatis + dwell lock + validasi workspace + koreksi overshoot base)*
- ⏳ Milestone 12 — Optimisasi *(lagi di sini sekarang)*
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
