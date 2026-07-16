# Python/serial_comm.py

import time
import serial as pyserial

from config import SerialConfig


COLOR_CODE = {
    "BLACK": "B",
    "WHITE": "W",
}


class SerialComm:
    """
    Bertanggung jawab atas komunikasi serial Python <-> Arduino.

    Protokol lama (Milestone 7, koordinat cm -> IK dihitung di Arduino):
        Python -> Arduino : "B,x,y\n" atau "W,x,y\n"

    Protokol baru (Milestone 9, IK dihitung di Python):
        Python -> Arduino : "B,base,shoulder,elbow\n" atau "W,base,shoulder,elbow\n"
        Arduino -> Python : "DONE\n" setelah selesai memproses satu siklus

    Handshake tetap blocking: kirim, tunggu ack "DONE", retry, atau stop
    kalau semua retry gagal (Decision #030, #031).

    logger (opsional): objek dengan method .log(message) - di-inject
    dari main.py (instance Dashboard) supaya semua pesan komunikasi
    serial (kirim, ack DONE, retry, error) tampil di panel log UI,
    bukan cuma di terminal. Kalau tidak di-inject (None), fallback ke
    print() biasa - SerialComm tetap bisa dipakai standalone/testing
    tanpa Dashboard, tidak ada perubahan behavior untuk caller lama.
    """

    def __init__(self, logger=None):
        self.port = SerialConfig.PORT
        self.baudrate = SerialConfig.BAUDRATE
        self.timeout = SerialConfig.TIMEOUT
        self.conn = None
        self.logger = logger

    def _log(self, message, level="SERIAL"):

        if self.logger is not None:
            self.logger.log(message, level)
        else:
            print(message)

    def connect(self):

        self.conn = pyserial.Serial(self.port, self.baudrate, timeout=self.timeout)

        # Beri waktu Arduino restart setelah koneksi serial dibuka
        time.sleep(2)
        self.conn.reset_input_buffer()

        self._log(f"Connected to Arduino on {self.port} ({self.baudrate} baud).", "INFO")

    def close(self):

        if self.conn is not None and self.conn.is_open:
            self.conn.close()

    def _send(self, color, x_cm, y_cm):

        code = COLOR_CODE.get(color)

        if code is None:
            raise ValueError(f"Warna tidak valid untuk protokol serial: {color}")

        message = f"{code},{x_cm:.2f},{y_cm:.2f}\n"
        self.conn.write(message.encode("utf-8"))

        return message

    def _send_angles(self, color, base_angle, shoulder_angle, elbow_angle):

        code = COLOR_CODE.get(color)

        if code is None:
            raise ValueError(f"Warna tidak valid untuk protokol serial: {color}")

        message = f"{code},{base_angle:.2f},{shoulder_angle:.2f},{elbow_angle:.2f}\n"
        self.conn.write(message.encode("utf-8"))

        return message

    def _wait_ack(self):
        """
        Menunggu balasan dari Arduino sampai token ACK_TOKEN diterima,
        atau ACK_TIMEOUT (total, bukan per-read) terlampaui.
        """

        deadline = time.time() + SerialConfig.ACK_TIMEOUT

        while time.time() < deadline:

            line = self.conn.readline().decode("utf-8", errors="ignore").strip()

            if line == SerialConfig.ACK_TOKEN:
                return True

            if line:
                self._log(f"Arduino: {line}", "INFO")

        return False

    def send_and_wait(self, color, x_cm, y_cm):
        """
        [Protokol lama - Milestone 7] Mengirim koordinat cm, IK dihitung
        di Arduino. Dipertahankan kalau masih dibutuhkan untuk testing.
        """

        for attempt in range(1, SerialConfig.MAX_RETRIES + 1):

            message = self._send(color, x_cm, y_cm)
            self._log(f"[Attempt {attempt}/{SerialConfig.MAX_RETRIES}] Send: {message.strip()}", "SEND")

            if self._wait_ack():
                self._log("ACK received.", "ACK")
                return True

            self._log(f"ACK timeout (>{SerialConfig.ACK_TIMEOUT}s).", "ERR")

            if attempt < SerialConfig.MAX_RETRIES:
                time.sleep(SerialConfig.RETRY_DELAY)

        self._log("Semua percobaan gagal. Koneksi serial dianggap tidak stabil.", "ERR")
        return False

    def send_angles_and_wait(self, color, base_angle, shoulder_angle, elbow_angle):
        """
        [Protokol baru - Milestone 9] Mengirim tiga sudut hasil
        InverseKinematics.compute(), menunggu ack "DONE", dengan retry
        sampai MAX_RETRIES kali (Decision #030, #031 tetap berlaku,
        cuma isi pesannya yang berubah dari koordinat cm ke sudut).

        Return:
            True  -> ack diterima, aman lanjut ke siklus berikutnya.
            False -> semua percobaan gagal, caller (main.py) harus
                     menghentikan program.
        """

        for attempt in range(1, SerialConfig.MAX_RETRIES + 1):

            message = self._send_angles(color, base_angle, shoulder_angle, elbow_angle)
            self._log(f"[Attempt {attempt}/{SerialConfig.MAX_RETRIES}] Send: {message.strip()}", "SEND")

            if self._wait_ack():
                self._log("ACK received.", "ACK")
                return True

            self._log(f"ACK timeout (>{SerialConfig.ACK_TIMEOUT}s).", "ERR")

            if attempt < SerialConfig.MAX_RETRIES:
                time.sleep(SerialConfig.RETRY_DELAY)

        self._log("Semua percobaan gagal. Koneksi serial dianggap tidak stabil.", "ERR")
        return False