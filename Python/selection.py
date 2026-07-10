import cv2


class Selection:
    """
    Bertanggung jawab memilih satu objek yang akan diproses dari
    sekian banyak objek hasil deteksi (Detection, Milestone 4).

    Rule pemilihan: objek dengan area contour terbesar (Decision #019).

    Kalau kandidat dengan area terbesar warnanya UNKNOWN (Color,
    Milestone 3), objek tersebut di-skip dan kandidat berikutnya
    (area terbesar selanjutnya) dicoba, sampai ketemu objek dengan
    warna valid (BLACK/WHITE) atau kandidat habis (Decision #020).
    """

    def __init__(self, color):

        # Dependency injection: Selection tidak membuat instance Color
        # sendiri, supaya satu instance Color yang sama dipakai
        # konsisten di seluruh sistem (Decision #021).
        self.color = color

    def select(self, roi, objects):
        """
        Args:
            roi: frame ROI saat ini, dipakai Color.classify().
            objects: list of objects dari Detection.detect()
                     (masing-masing punya id, centroid, bbox,
                     contour, area).

        Return:
            dict | None: objek terpilih (copy dari objek asli + key
            "color"), atau None kalau tidak ada objek dengan warna
            valid (BLACK/WHITE) di antara semua kandidat.
        """

        if not objects:
            return None

        # Urutkan kandidat dari area terbesar ke terkecil
        candidates = sorted(
            objects, key=lambda obj: obj["area"], reverse=True
        )

        for obj in candidates:

            label = self.color.classify(roi, obj["contour"])

            if label == self.color.UNKNOWN:
                continue

            selected = dict(obj)
            selected["color"] = label

            return selected

        # Semua kandidat UNKNOWN
        return None

    def draw_selected(self, frame, selected):

        if selected is None:
            return frame

        x, y, w, h = selected["bbox"]

        cv2.rectangle(
            frame, (x, y), (x + w, y + h),
            (0, 255, 0), 3
        )

        label = f"SELECTED #{selected['id']} {selected['color']}"

        cv2.putText(
            frame, label, (x, y - 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2
        )

        return frame