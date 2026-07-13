import math as mt


class InverseKinematics:
    """
    Menghitung sudut base, shoulder, elbow dari koordinat robot (cm).

    Rumus di dalam compute() adalah hasil kalibrasi fisik Odi
    (trial-and-error di hardware asli, tervalidasi presisi di seluruh
    titik ekstrim ROI). JANGAN diubah tanpa validasi ulang di hardware.
    """

    def __init__(self):

        # Konstanta geometri arm (hasil kalibrasi fisik)
        self.tinggi = 8.3
        self.L1 = 6.8
        self.L2 = 11.64

    def compute(self, x_cm, y_cm):
        """
        Input : x_cm, y_cm — koordinat robot (cm), hasil Mapping.pixel_to_robot()
        Return: (base_angle, shoulder_angle, elbow_angle) dalam derajat, float biasa
        """

        Tinggi = self.tinggi
        L1 = self.L1
        L2 = self.L2

        l = mt.sqrt(x_cm**2 + y_cm**2)
        h = mt.sqrt(l**2 + Tinggi**2)
        x = (h**2 - (L2**2 - L1**2)) / (2 * h)

        # menghitung shoulder angle
        theta = mt.degrees(mt.acos(x / L1))
        k = mt.degrees(mt.atan(l / Tinggi))
        sudutbuang = theta + k
        sudutingin = 155 - sudutbuang
        shoulder_angle = 100 - sudutingin

        # menghitung elbow angle
        alfa = mt.degrees(mt.acos((L1**2 + L2**2 - h**2) / (2 * L1 * L2)))
        A = alfa - 87
        elbow_angle = 90 - A  # Ubah tanda kalo putarnya salah

        # menghitung base angle
        base_angle = mt.degrees(mt.atan2(y_cm, x_cm))

        return float(base_angle), float(shoulder_angle), float(elbow_angle)