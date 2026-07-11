import cv2
import numpy as np

from config import DetectionConfig


class Detection:

    def __init__(self):

        # Reference frame (kondisi ROI kosong / tanpa objek)
        self.reference_frame = None

    def set_reference(self, roi):

        self.reference_frame = self._preprocess(roi)

    def has_reference(self):

        return self.reference_frame is not None

    def _preprocess(self, roi):

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        k = DetectionConfig.BLUR_KERNEL

        blurred = cv2.GaussianBlur(gray, (k, k), 0)

        return blurred

    def detect(self, roi):
        """
        Mendeteksi seluruh objek valid pada ROI.

        Return:
            objects (list[dict]): setiap objek berisi
                - id       : nomor urut (kiri -> kanan)
                - centroid : (cx, cy)
                - contour  : contour asli
                - area     : luas contour
            mask (ndarray | None)
        """

        if self.reference_frame is None:
            return [], None

        current = self._preprocess(roi)

        # Background Subtraction
        diff = cv2.absdiff(self.reference_frame, current)

        # Threshold
        _, thresh = cv2.threshold(
            diff,
            DetectionConfig.DIFF_THRESHOLD,
            255,
            cv2.THRESH_BINARY
        )

        # Morphology (buang noise kecil, tutup lubang kecil)
        kernel = np.ones(
            (DetectionConfig.MORPH_KERNEL, DetectionConfig.MORPH_KERNEL),
            np.uint8
        )

        mask = cv2.morphologyEx(
            thresh, cv2.MORPH_OPEN, kernel,
            iterations=DetectionConfig.MORPH_ITERATIONS
        )
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE, kernel,
            iterations=DetectionConfig.MORPH_ITERATIONS
        )

        # Contour Detection
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        valid_contours = [
            c for c in contours
            if cv2.contourArea(c) >= DetectionConfig.MIN_CONTOUR_AREA
        ]

        objects = self._build_objects(valid_contours)

        return objects, mask

    def _build_objects(self, contours):
        """
        Menghitung centroid tiap contour valid (Decision #013),
        lalu mengurutkan objek dari kiri ke kanan berdasarkan
        koordinat x centroid (Decision #012) supaya penomoran
        konsisten antar frame.
        """

        raw = []

        for c in contours:

            M = cv2.moments(c)

            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Bounding box: kotak pembungkus objek. Semua pixel yang
            # ada di dalam kotak ini dianggap milik objek yang sama.
            x, y, w, h = cv2.boundingRect(c)

            raw.append({
                "centroid": (cx, cy),
                "bbox": (x, y, w, h),
                "contour": c,
                "area": cv2.contourArea(c)
            })

        raw.sort(key=lambda obj: obj["centroid"][0])

        objects = []

        for i, obj in enumerate(raw, start=1):
            objects.append({
                "id": i,
                "centroid": obj["centroid"],
                "bbox": obj["bbox"],
                "contour": obj["contour"],
                "area": obj["area"]
            })

        return objects

    def draw_status(self, frame, objects):

        if not self.has_reference():
            text = f"Press '{DetectionConfig.CAPTURE_REF_KEY}' to set reference"
            color = (0, 255, 255)
        elif len(objects) > 0:
            text = f"Objects Found: {len(objects)}"
            color = (0, 255, 0)
        else:
            text = "No Object"
            color = (0, 0, 255)

        cv2.putText(
            frame, text, (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 2
        )

        return frame

    def draw_objects(self, roi, objects):
        """
        Menggambar bounding box tiap objek, titik centroid di
        tengahnya, dan label nomor + koordinat (format: #id (x,y)).

        Bounding box = kotak pembungkus objek (dari cv2.boundingRect).
        Semua pixel di dalam kotak ini dianggap milik objek tersebut.
        """

        roi_drawn = roi.copy()

        for obj in objects:

            x, y, w, h = obj["bbox"]
            cx, cy = obj["centroid"]

            # Kotak pembungkus objek
            cv2.rectangle(
                roi_drawn, (x, y), (x + w, y + h),
                (255, 0, 255), 2
            )

            # Titik tengah (centroid) objek
            cv2.circle(roi_drawn, (cx, cy), 4, (0, 255, 0), -1)

            label = f"#{obj['id']} ({cx},{cy})"

            cv2.putText(
                roi_drawn, label, (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

        return roi_drawn