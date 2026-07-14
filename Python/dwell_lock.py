import time
import cv2


class DwellLock:
    """
    Melacak apakah objek terpilih (hasil Selection.select()) sudah
    "diam" di posisi & warna yang sama selama minimal LOCK_DURATION
    detik, sebelum dianggap boleh diproses (Decision #058, Milestone 11).

    Debounce ini mencegah sistem memicu pick-and-place saat objek masih
    bergerak, atau tangan operator masih ada di ROI.

    Tidak bergantung pada class lain - cuma nerima dict `selected` dari
    Selection, konsisten dengan pola dependency-injected sederhana yang
    sudah dipakai InverseKinematics (Milestone 9).
    """

    def __init__(self, lock_duration, position_tolerance):

        self.lock_duration = lock_duration
        self.position_tolerance = position_tolerance

        self._anchor_centroid = None
        self._anchor_color = None
        self._start_time = None

    def update(self, selected):
        """
        Args:
            selected: dict hasil Selection.select(), atau None.

        Return:
            (locked, remaining):
                locked    - True kalau objek sudah diam >= lock_duration
                            detik di posisi & warna yang sama.
                remaining - sisa detik sebelum locked (float), atau None
                            kalau tidak ada objek yang sedang di-track.
        """

        if selected is None:
            self.reset()
            return False, None

        centroid = selected["centroid"]
        color = selected["color"]

        if not self._is_same_target(centroid, color):
            # Objek baru / berpindah / ganti warna -> mulai hitung ulang
            self._anchor_centroid = centroid
            self._anchor_color = color
            self._start_time = time.time()
            return False, self.lock_duration

        elapsed = time.time() - self._start_time
        remaining = max(0.0, self.lock_duration - elapsed)

        if elapsed >= self.lock_duration:
            return True, 0.0

        return False, remaining

    def reset(self):

        self._anchor_centroid = None
        self._anchor_color = None
        self._start_time = None

    def _is_same_target(self, centroid, color):

        if self._anchor_centroid is None or self._start_time is None:
            return False

        if color != self._anchor_color:
            return False

        dx = centroid[0] - self._anchor_centroid[0]
        dy = centroid[1] - self._anchor_centroid[1]
        distance = (dx**2 + dy**2) ** 0.5

        return distance <= self.position_tolerance

    def draw_status(self, frame, selected, locked, remaining):

        if selected is None:
            return frame

        x, y, w, h = selected["bbox"]

        if locked:
            text = "LOCKED - processing"
            text_color = (0, 255, 0)
        else:
            text = f"Locking... {remaining:.1f}s"
            text_color = (0, 165, 255)

        cv2.putText(
            frame, text, (x, y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, text_color, 2
        )

        return frame