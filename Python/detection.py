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

        if self.reference_frame is None:
            return False, [], None

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

        object_found = len(valid_contours) > 0

        return object_found, valid_contours, mask

    def draw_status(self, frame, object_found):

        if not self.has_reference():
            text = f"Press '{DetectionConfig.CAPTURE_REF_KEY}' to set reference"
            color = (0, 255, 255)
        elif object_found:
            text = "Object Found"
            color = (0, 255, 0)
        else:
            text = "No Object"
            color = (0, 0, 255)

        cv2.putText(
            frame, text, (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
        )

        return frame

    def draw_contours(self, roi, contours):

        roi_drawn = roi.copy()

        cv2.drawContours(roi_drawn, contours, -1, (255, 0, 255), 2)

        return roi_drawn