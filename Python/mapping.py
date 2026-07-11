import numpy as np
import cv2

from config import MappingConfig


class Mapping:
    """
    Menerjemahkan koordinat pixel (centroid dari Detection) menjadi
    koordinat robot dalam cm menggunakan homography (transformasi
    perspektif 3x3).

    Homography dipilih (bukan model linear scale+offset per axis)
    karena kamera tidak terpasang benar-benar top-down, sehingga ada
    distorsi perspektif ringan yang tidak bisa dikompensasi hanya
    dengan scale + offset independen per axis (Decision #023,
    Milestone 6 - revisi).
    """

    def __init__(self):
        self.matrix = np.array(
            MappingConfig.HOMOGRAPHY_MATRIX, dtype=np.float64
        ).reshape(3, 3)

    def pixel_to_robot(self, centroid):
        """
        centroid: (px, py) dalam koordinat pixel ROI.
        return  : (x_cm, y_cm) dalam koordinat robot.
        """
        px, py = centroid

        point = np.array([[[px, py]]], dtype=np.float64)
        transformed = cv2.perspectiveTransform(point, self.matrix)

        x_cm, y_cm = transformed[0][0]

        return (float(x_cm), float(y_cm))