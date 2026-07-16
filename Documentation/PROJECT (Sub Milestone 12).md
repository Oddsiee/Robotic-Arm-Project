# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 12

- ✅ Sub-Milestone 12 (Dashboard UI) selesai.
- **Dashboard runtime diganti total** dari tampilan OpenCV mentah (3 window terpisah: Camera, ROI, Mask + terminal untuk log) menjadi **satu window komposit bergaya Apple Human Interface (HIG)** — dark mode iOS, rounded corner cards, typography DUPLEX/SIMPLEX, color-coded semantic accents.
- Dibuat class `Dashboard` (`dashboard.py`) sebagai compositor tampilan tunggal, menggantikan `Camera.show()` / `Camera.show_roi()` / window Mask terpisah yang dipakai sejak Milestone 1-2.
- Layout baru: **Header** (title + status pill + FPS) → **Body** (camera feed kiri + sidebar cards kanan: ROI preview, Detection, IK, Serial, Mask toggle) → **System Log** (timestamp + color-coded level dots) → **Footer** (SF-style keyboard shortcut badges + Auto Mode indicator).
- **State-driven UI**: `dashboard.update_state()` dipanggil tiap frame dari `main.py` — semua panel (Detection card, IK card, Serial card, status pill) otomatis merefleksikan kondisi sistem real-time tanpa perlu refresh manual.
- **Log berlevel**: method `log(message, level)` menggantikan `print()` mentah. Level: `REF`, `LOCK`, `SEND`, `ACK`, `ERR`, `SKIP`, `UI`, `INFO` — masing-masing punya warna dot sendiri di panel System Log.
- `SerialComm._log()` di-upgrade dari 1-argumen ke 2-argumen (`message`, `level`) supaya semua pesan komunikasi serial juga tampil dengan level yang benar di dashboard.
- **Tidak ada perubahan** pada pipeline vision (`Detection`, `Color`, `Selection`), mapping (`Mapping`), inverse kinematics (`InverseKinematics`), protokol serial (`SerialComm`), maupun sketch Arduino (`FinalProgram.ino`). Dashboard murni lapisan presentasi — semua logika di bawahnya tidak disentuh.
- Tool kalibrasi (`calibration_color.py`, `calibration_mapping.py`, `test_mapping.py`) **tidak disentuh** — tetap pakai window OpenCV bawaan seperti biasa.

---

## Keputusan Teknis Baru

### Decision #060
Semua tampilan runtime digabung menjadi **satu window komposit** lewat class `Dashboard` (`dashboard.py`), menggantikan 3 window OpenCV + terminal yang dipakai sejak Milestone 1.

**Alasan**
- Operator tidak perlu bolak-balik antar window atau ke terminal untuk memonitor status sistem — semua informasi (camera feed, ROI, detection, IK, serial, log) terlihat dalam satu layar.
- Konsisten dengan prinsip single-class-single-responsibility: `Dashboard` murni compositor tampilan, tidak menyentuh pipeline vision/serial sama sekali — `main.py` tetap pemilik orchestration, `Dashboard` cuma penerima data lewat `update_state()`.

### Decision #061
Desain visual mengadopsi **Apple Human Interface Guidelines (HIG) dark mode**: palet iOS (`#1C1C1E` system background, `#2C2C2E` cards, `#3A3A3C` elevated), rounded corners (10px pada cards, 4-6px pada badge/preview), typography `HERSHEY_DUPLEX` untuk heading dan `HERSHEY_SIMPLEX` untuk body, spacing generous (gap 10px antar card, padding 12-16px).

**Alasan**
- OpenCV tidak punya engine UI native — semua "komponen" (card, pill, rounded rect, separator) dibangun manual dari primitif `cv2.rectangle`, `cv2.ellipse`, `cv2.line`, `cv2.putText`. Apple HIG dipilih sebagai referensi karena konsisten, bersih, dan informasi-dense tanpa terlihat penuh.
- Dark mode dipilih karena: (a) kontras rendah lebih nyaman dipandang lama saat operasi, (b) kamera feed (terang) jadi focal point alami di atas background gelap.

### Decision #062
Dashboard bersifat **state-driven**: `main.py` memanggil `dashboard.update_state(**kwargs)` tiap frame dengan seluruh state terkini (`armed`, `fps`, `selected`, `locked`, `remaining`, `angles`, `processing`, `serial_ok`, `last_cmd`). Setiap panel membaca dari `self._state` saat render — tidak ada callback, tidak ada event bus.

**Alasan**
- Pola paling sederhana yang konsisten dengan arsitektur proyek yang sudah ada (dependency injection, tanpa framework). State dictionary adalah single source of truth untuk seluruh UI dalam satu frame.
- Tidak butuh reactive framework atau observer pattern untuk dashboard single-window dengan ~10 field state — overhead tidak sepadan.

### Decision #063
Method `log()` di-upgrade dari `log(message)` menjadi `log(message, level="INFO")`. Level menentukan warna dot di panel System Log: biru (`REF`), hijau (`LOCK`, `ACK`), oranye (`SEND`, `SKIP`), merah (`ERR`), abu-abu (`UI`, `INFO`).

**Alasan**
- Operator bisa sekilas membedakan jenis pesan (info biasa vs. warning vs. error) tanpa membaca teks lengkap — color-coded dot berfungsi sebagai "traffic light" mini.
- Backward-compatible: default level `"INFO"` memastikan semua caller lama yang tidak menyebut level tetap jalan.

**Dampak pada `SerialComm`**
- `SerialComm._log()` diubah dari `_log(self, message)` menjadi `_log(self, message, level="SERIAL")`.
- Semua pemanggilan internal `_log()` di `SerialComm` sekarang menyertakan level: `"SEND"` (kirim command), `"ACK"` (balasan DONE), `"ERR"` (timeout/gagal), `"INFO"` (connect/Arduino debug line).

### Decision #064
Sidebar kanan dibagi menjadi **4 kartu independen** (ROI Preview, Detection, Inverse Kinematics, Serial), ditambah kartu **Mask Debug** (toggle `m`). Setiap kartu punya accent bar kiri berwarna yang berubah sesuai state:
- **Detection**: hijau (`locked`), oranye (`locking...`), none (no object)
- **IK**: biru (sedang computing / hasil tersedia), none (idle)
- **Serial**: hijau (connected), merah (disconnected)

**Alasan**
- Pemisahan per-kartu (bukan satu panel teks panjang) memudahkan operator menemukan informasi spesifik dengan cepat — tidak perlu scan seluruh teks.
- Accent bar kiri adalah konvensi Apple HIG untuk menunjukkan status/state tanpa menambah teks — lebih cepat diproses secara visual daripada membaca label.

### Decision #065
Footer menampilkan shortcut keyboard dengan **SF-style key badges**: setiap tombol dirender sebagai rounded rectangle kecil (`BG_ELEVATED`) dengan label di sebelahnya. Indikator Auto Mode (ON/OFF) di pojok kanan bawah.

**Alasan**
- Key badges lebih mudah dikenali daripada teks `q:Quit | r:Set Ref` — bentuk rounded rect langsung diasosiasikan dengan "tombol keyboard" oleh pengguna.
- Auto Mode indicator memberikan konfirmasi visual instan apakah sistem sedang dalam mode otomatis (reference sudah di-set) atau belum.

### Decision #066
`config.py` dibersihkan dari duplikasi class yang tertinggal dari milestone sebelumnya. Ditemukan dan dihapus:
- **Duplikat `WindowConfig`**: definisi pertama (tanpa `MAIN_WINDOW`) dan definisi kedua (dengan `MAIN_WINDOW`) — digabung jadi satu.
- **Duplikat `SerialConfig`**: definisi pertama (hanya `PORT`, `BAUDRATE`, `TIMEOUT`) dan definisi kedua (dengan `ACK_TIMEOUT`, `MAX_RETRIES`, `RETRY_DELAY`, `ACK_TOKEN`) — yang pertama dihapus, menyisakan yang lengkap.
- **Blok komentar instruksi manual** ("TAMBAHKAN ke config.py...") yang sudah tidak relevan — dihapus.

**Alasan**
- Duplikasi class di Python tidak menyebabkan bug runtime (definisi kedua otomatis menimpa yang pertama), tapi membingungkan saat dibaca dan berisiko saat diedit (bisa tidak sengaja mengedit definisi yang salah).
- Membersihkan sekarang selagi file masih kecil mencegah akumulasi technical debt yang sama seperti yang dicatat di Milestone 11.

**Dampak pada `DashboardConfig`**
- `CAMERA_DISPLAY_WIDTH`: 480 → **540** (lebih lega untuk Apple-style layout)
- `SIDE_PANEL_WIDTH`: 220 → **260** (lebih lapang untuk kartu-kartu sidebar)
- `LOG_LINE_HEIGHT`: 18 → 19 (menyesuaikan spacing)
- Field `LOG_FONT_SCALE` dihapus (tidak dipakai lagi — ukuran font sekarang di-hardcode per elemen)

---

## Perubahan File

| File | Status | Keterangan |
|---|---|---|
| `Python/dashboard.py` | **Rewrite total** | Apple HIG compositor (~550 baris), menggantikan v1 (~170 baris) dan v2 (~300 baris) |
| `Python/config.py` | **Edit** | Bersihkan duplikat `WindowConfig` & `SerialConfig`, hapus blok komentar usang, update `DashboardConfig` values |
| `Python/main.py` | **Edit** | Tambah `dashboard.update_state()` di loop, semua `log()` panggil dengan level, hapus komentar blok lama |
| `Python/serial_comm.py` | **Edit** | `_log()` jadi 2-argumen, semua internal call pakai level (`SEND`, `ACK`, `ERR`, `INFO`) |
| `Python/camera.py` | Tidak disentuh | — |
| `Python/detection.py` | Tidak disentuh | — |
| `Python/color.py` | Tidak disentuh | — |
| `Python/selection.py` | Tidak disentuh | — |
| `Python/dwell_lock.py` | Tidak disentuh | — |
| `Python/mapping.py` | Tidak disentuh | — |
| `Python/inverse_kinematics.py` | Tidak disentuh | — |
| `Python/serial_comm.py` | **Minor edit** | Hanya `_log()` signature + level parameter |
| `Arduino/FinalProgram/FinalProgram.ino` | Tidak disentuh | — |

---

## Detail Teknis: Komponen Dashboard

### Palet Warna (iOS Dark Mode)

| Token | Hex | RGB (BGR) | Penggunaan |
|---|---|---|---|
| `BG_ROOT` | `#1C1C1E` | `(28,28,30)` | Background utama |
| `BG_CARD` | `#2C2C2E` | `(44,44,46)` | Kartu sidebar |
| `BG_ELEVATED` | `#3A3A3C` | `(58,58,60)` | Badge keyboard, status pill |
| `BG_HEADER` | `#202022` | `(32,32,34)` | Header bar |
| `BG_LOG` | `#161618` | `(22,22,24)` | Panel System Log |
| `BLUE` | `#0A84FF` | `(255,132,10)` | System blue — IK card |
| `GREEN` | `#30D158` | `(88,209,48)` | Connected, locked, armed |
| `ORANGE` | `#FF9F0A` | `(10,159,255)` | Processing, sending, dwell |
| `RED` | `#FF453A` | `(58,69,255)` | Error, idle, disconnected |
| `LABEL` | `#F2F2F7` | `(247,242,242)` | Primary text |
| `SECONDARY` | `#AEAEB2` | `(178,174,174)` | Secondary text |
| `TERTIARY` | `#636366` | `(102,99,99)` | Tertiary labels |
| `SEPARATOR` | `#38383A` | `(58,56,56)` | Thin dividers |

> **Catatan**: OpenCV menyimpan warna dalam format **BGR**, bukan RGB. Semua konstanta warna di `dashboard.py` sudah ditulis dalam urutan BGR. Tabel di atas menampilkan hex asli iOS untuk referensi desain — nilai di kode adalah BGR.

### Typography

| Role | Font | Scale | Thickness | Contoh |
|---|---|---|---|---|
| Heading (title) | `HERSHEY_DUPLEX` | 0.6 | 1 | "Robotic Arm" |
| Card section title | `HERSHEY_SIMPLEX` | 0.38 | 1 | "DETECTION", "IK" |
| Card data value | `HERSHEY_SIMPLEX` | 0.42 | 1 | "BLACK", "85.3°" |
| Card data label | `HERSHEY_SIMPLEX` | 0.42 | 1 | "Color", "Base" |
| Log timestamp | `HERSHEY_SIMPLEX` | 0.35 | 1 | "14:32:01" |
| Log message | `HERSHEY_SIMPLEX` | 0.38 | 1 | Pesan log |
| Footer keys | `HERSHEY_SIMPLEX` | 0.38 | 1 | "q", "r", "m", "p" |
| Footer labels | `HERSHEY_SIMPLEX` | 0.35 | 1 | "Quit", "Set Ref" |

### Drawing Primitives Baru

- **`_rounded_rect(canvas, x, y, w, h, r, color, fill)`** — menggambar rounded rectangle dengan radius `r`, diimplementasikan sebagai 2 `cv2.rectangle` (badan) + 4 `cv2.ellipse` (sudut). Dipakai untuk semua kartu dan badge.
- **`_pill(canvas, x, y, w, h, color, fill)`** — shortcut ke `_rounded_rect` dengan `r = h // 2` (fully rounded ends), dipakai untuk status pill di header.

### Level Log & Warna Dot

| Level | Warna Dot | Makna | Sumber Pemanggil |
|---|---|---|---|
| `REF` | 🔵 Biru | Reference frame capture | `main.py` |
| `LOCK` | 🟢 Hijau | Objek locked, mulai proses | `main.py` |
| `SEND` | 🟠 Oranye | Command dikirim ke Arduino | `SerialComm` |
| `ACK` | 🟢 Hijau | Acknowledgment diterima | `SerialComm` |
| `ERR` | 🔴 Merah | Error / timeout / gagal | `main.py`, `SerialComm` |
| `SKIP` | 🟠 Oranye | Target di-skip (di luar workspace) | `main.py` |
| `UI` | ⚪ Abu-abu | Toggle UI (mask panel) | `Dashboard` |
| `INFO` | ⚪ Abu-abu | Informasi umum | `main.py`, `SerialComm` |

---

## Catatan / Technical Debt

- OpenCV tidak punya font family selection — `HERSHEY_DUPLEX` dan `HERSHEY_SIMPLEX` adalah aproksimasi terdekat ke San Francisco yang tersedia. Tidak bisa menggunakan font system asli (.ttf) tanpa library tambahan seperti `PIL/Pillow`.
- Rounded corners diimplementasikan manual (2 rect + 4 ellipse) — tidak ada `cv2.roundedRectangle()` native. Tidak ada dampak performa signifikan karena cuma dipanggil ~10 kali per frame untuk kartu statis.
- Ukuran kartu sidebar (260px) dan kamera (540px) di-hardcode di `DashboardConfig`. Total lebar dashboard = 800px + header 44px + footer 28px. Kalau layar laptop operator lebih kecil dari ~900px vertikal, panel log bisa terpotong — bisa diatasi dengan memperkecil `CAMERA_DISPLAY_WIDTH` atau `LOG_MAX_LINES`.
- State dashboard (`self._state`) adalah dictionary mutable yang di-update tiap frame — tidak ada mekanisme untuk mendeteksi perubahan (diffing) atau notifikasi. Semua panel di-render ulang penuh tiap frame, termasuk yang statis. Untuk 10 field state dan ~4 kartu, overhead tidak signifikan — tapi kalau dashboard berkembang jauh lebih kompleks, bisa dipertimbangkan simple dirty-flag per panel.
- `SerialComm._log()` sekarang menerima parameter `level` — kalau ada kode eksternal yang memanggil `SerialComm._log()` langsung (bukan lewat inject `logger`), perlu disesuaikan. Tidak ada caller seperti itu dalam codebase saat ini.
- Tool kalibrasi (`calibration_color.py`, `calibration_mapping.py`, `test_mapping.py`) masih pakai 3 window OpenCV terpisah — tidak menggunakan `Dashboard`. Sengaja tidak disentuh karena hanya dipakai sesekali saat setup/kalibrasi, bukan saat operasi rutin.

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
- ✅ Milestone 12 — Optimisasi *(Dashboard UI — Apple HIG single-window compositor, state-driven, color-coded log)*
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi
