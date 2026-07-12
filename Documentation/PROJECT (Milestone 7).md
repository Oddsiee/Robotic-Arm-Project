# PROJECT.md

# Robotic Arm Project

> Living document sebagai **single source of truth** selama pengembangan proyek.

---

## Ringkasan Update Milestone 7

- ✅ Milestone 7 selesai.
- Spesifikasi servo diklarifikasi: **claw, shoulder, elbow** pakai SG90 **180°** (positional, bisa langsung `write(angle)`), sedangkan **base** pakai SG90 **360°** (continuous rotation, hanya bisa dikontrol arah + kecepatan, tidak punya sudut absolut). Ini konsisten dengan behavior base servo yang sudah kelihatan dari kode teleop awal (`write(100)`/`write(80)`/`write(90)` untuk kiri/kanan/stop). Belum berdampak ke Milestone 7 karena protokol serial mengirim koordinat cm (bukan sudut servo), tapi **jadi catatan penting untuk Milestone 9 (Inverse Kinematics)** — output sudut base dari IK tidak bisa langsung di-`write()` ke servo continuous, perlu strategi tambahan (kemungkinan time-based rotation atau feedback/limit switch).
- Komunikasi Python ↔ Arduino bersifat **bidirectional dengan handshake blocking**: Python mengirim satu koordinat, lalu menunggu balasan `DONE` dari Arduino sebelum boleh mengirim koordinat berikutnya — bukan fire-and-forget.
- Kegagalan menerima `DONE` dalam batas waktu (`ACK_TIMEOUT`) ditangani dengan **retry beberapa kali** (`MAX_RETRIES`), dan kalau tetap gagal setelah semua percobaan habis, program **berhenti total** (bukan skip ke siklus berikutnya) — karena state fisik robot tidak bisa diasumsikan aman kalau komunikasi terputus.
- File `Python/serial.py` (kosong, dari rencana awal) di-**rename menjadi `serial_comm.py`**, karena nama `serial.py` bentrok dengan package `pyserial` — `import serial` di dalam project akan mengambil file lokal, bukan library aslinya.
- Class `SerialComm` menangani seluruh logika komunikasi serial: `connect()`/`close()` untuk koneksi, `send_and_wait()` sebagai satu-satunya entry point publik untuk mengirim koordinat (menggabungkan send + wait-ack + retry), konsisten dengan pola satu class satu tanggung jawab.
- Sketch prototipe lama `Arduino/RoboticArmPrototype/` (teleop manual per-karakter, dibuat sebelum arsitektur milestone ini disusun) **dihapus sepenuhnya**, dianggap tidak pernah ada. Bukan bagian dari arsitektur final.
- Dibuat sketch test terpisah, `Arduino/SerialTest.ino`, khusus menguji jalur komunikasi Milestone 7 — belum ada servo/IK sama sekali, hanya parsing koordinat + delay simulasi + balas `DONE`. Ditaruh lepas di root `Arduino/` (bukan di `ServoControl/`, `InverseKinematics/`, atau `FinalProgram/`, karena tidak ada satupun yang representatif untuk tahap ini).
- Parsing koordinat di sisi Arduino dilakukan **manual** (`indexOf`/`substring`/`toFloat()`), bukan `sscanf("%f")` — `sscanf` dengan format float seringkali tidak reliable di board AVR (Arduino Uno) karena keterbatasan implementasi `stdio`-nya.
- `main.py` diupdate: setelah objek terpilih (`Selection`, Milestone 5), key `s` memicu `mapping.pixel_to_robot()` (Milestone 6) untuk konversi pixel → cm, lalu `serial_comm.send_and_wait()` untuk mengirim ke Arduino. Trigger pengiriman tetap manual lewat keypress (bukan otomatis tiap frame), konsisten dengan pola key `p`/`r` yang sudah ada.
- Pengujian dilakukan: kirim koordinat dengan Arduino aktif (berhasil, `DONE` diterima), serta pengujian skenario gagal (memutus koneksi USB saat menunggu ack) untuk memverifikasi retry dan stop-on-failure bekerja sesuai desain.

---

## Keputusan Teknis Baru

### Decision #029
Base servo menggunakan SG90 **360° continuous rotation**, berbeda dari claw/shoulder/elbow yang SG90 **180° positional**. Konsekuensi teknisnya ditunda untuk ditangani di **Milestone 9 (Inverse Kinematics)**, tidak mengubah apapun di Milestone 7.

**Alasan**
- Protokol serial Milestone 7 mengirim koordinat robot dalam cm (Decision di Milestone 0, Section 8), bukan sudut servo — jadi tipe servo base belum relevan di layer ini.
- Mencatatnya sekarang mencegah asumsi keliru di Milestone 8/9 bahwa semua servo bisa dikontrol dengan cara yang sama.

### Decision #030
Komunikasi serial menggunakan **handshake blocking**: Python menunggu ack `"DONE"` dari Arduino sebelum mengirim koordinat berikutnya, bukan one-way/fire-and-forget.

**Alasan**
- Siklus operasi robot (Home → Detect → Pick → Drop → Home) sudah didefinisikan sebagai proses sekuensial (Milestone 0, Section 9) — mengirim koordinat baru sebelum Arduino selesai dengan koordinat sebelumnya berisiko menimbulkan gerakan yang tumpang tindih atau tidak terduga secara fisik.
- Ack eksplisit memberi Python kepastian tentang state Arduino, bukan asumsi berdasarkan delay tetap di sisi Python.

### Decision #031
Kegagalan menerima ack ditangani dengan **retry (`MAX_RETRIES` kali) lalu stop program** jika semua percobaan gagal — bukan skip ke siklus berikutnya.

**Alasan**
- Retry menutup kemungkinan glitch sesaat di komunikasi serial (noise kabel, byte terlewat) yang wajar terjadi dan tidak selalu berarti masalah serius.
- Skip-dan-lanjut dianggap terlalu berisiko untuk sistem yang menggerakkan motor fisik: kalau Arduino tidak merespons, Python tidak tahu apakah Arduino masih di tengah gerakan atau macet total, sehingga mengirim koordinat baru dalam kondisi tidak pasti bisa berbahaya secara fisik.

### Decision #032
`Python/serial.py` (placeholder kosong) di-**rename menjadi `serial_comm.py`**.

**Alasan**
- Nama `serial.py` bentrok langsung dengan package pip `pyserial`, yang di-import dengan `import serial` — Python akan memprioritaskan file lokal di atas package terinstall, menyebabkan `pyserial` tidak pernah benar-benar terpanggil.

### Decision #033
Sketch prototipe teleop manual `Arduino/RoboticArmPrototype/` **dihapus sepenuhnya** dari project, digantikan oleh `Arduino/SerialTest.ino` sebagai sketch test khusus Milestone 7.

**Alasan**
- `RoboticArmPrototype` dibuat untuk keperluan eksplorasi awal (kontrol servo manual per-karakter via keyboard), tidak dirancang mengikuti protokol serial (`B,x,y`/`W,x,y`) maupun arsitektur milestone yang sudah ditetapkan — mencampurnya dengan alur produksi hanya akan membingungkan.
- Sketch produksi yang sebenarnya (parsing koordinat → IK → servo) baru akan ditulis di Milestone 8/9; sketch test Milestone 7 sengaja dibuat minimal (tanpa servo) supaya fokus murni menguji jalur komunikasi.

### Decision #034
`Arduino/SerialTest.ino` ditaruh lepas di **root `Arduino/`**, bukan di dalam `ServoControl/`, `InverseKinematics/`, atau `FinalProgram/`.

**Alasan**
- Struktur folder Arduino sudah ditetapkan hanya berisi 3 folder tersebut; tidak ada satupun yang representatif untuk sketch yang murni menguji komunikasi serial tanpa servo/IK.
- Diterima sebagai solusi sementara — kalau ke depannya (Milestone 8/9) root `Arduino/` mulai terasa berantakan dengan banyak sketch lepas, bisa dipindah ke folder sendiri kapan saja tanpa mengubah logic-nya.

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
- ⏳ Milestone 8 — Kontrol Servo
- ⏳ Milestone 9 — Inverse Kinematics
- ⏳ Milestone 10 — Pick and Place
- ⏳ Milestone 11 — Integrasi Vision + Robot
- ⏳ Milestone 12 — Optimisasi
- ⏳ Milestone 13 — Pengujian
- ⏳ Milestone 14 — Dokumentasi