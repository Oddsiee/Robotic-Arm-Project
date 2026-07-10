import cv2
import numpy as np

from config import HSVConfig


class Color:
    """
    Bertanggung jawab untuk mengklasifikasikan warna objek (BLACK/WHITE)
    dari sebuah contour hasil deteksi (Detection).

    HSV thresholding dibatasi hanya pada area contour (bukan seluruh ROI),
    supaya piksel background/alas tidak ikut mempengaruhi keputusan warna.
    """

    BLACK = "BLACK"
    WHITE = "WHITE"
    UNKNOWN = "UNKNOWN"

    def __init__(self):
        pass

    def classify(self, roi, contour):

        # Mask khusus area contour ini saja
        contour_mask = np.zeros(roi.shape[:2], dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        black_mask = cv2.inRange(hsv, HSVConfig.BLACK_LOWER, HSVConfig.BLACK_UPPER)
        white_mask = cv2.inRange(hsv, HSVConfig.WHITE_LOWER, HSVConfig.WHITE_UPPER)

        # Hanya hitung piksel yang berada di dalam contour
        black_mask = cv2.bitwise_and(black_mask, contour_mask)
        white_mask = cv2.bitwise_and(white_mask, contour_mask)

        black_count = cv2.countNonZero(black_mask)
        white_count = cv2.countNonZero(white_mask)

        if black_count == 0 and white_count == 0:
            return Color.UNKNOWN

        return Color.BLACK if black_count >= white_count else Color.WHITE

    def draw_label(self, frame, contour, label):

        x, y, w, h = cv2.boundingRect(contour)

        if label == Color.BLACK:
            box_color = (0, 0, 0)
            text_color = (255, 255, 255)
        elif label == Color.WHITE:
            box_color = (255, 255, 255)
            text_color = (0, 0, 0)
        else:
            box_color = (0, 165, 255)
            text_color = (0, 165, 255)

        cv2.rectangle(frame, (x, y), (x + w, y + h), box_color, 2)

        cv2.putText(
            frame,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            text_color,
            2
        )

        return frame