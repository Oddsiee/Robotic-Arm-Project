import math as mt


class WorkspaceError(Exception):
    """
    Target (x_cm, y_cm) tidak bisa diproses dengan aman:
    - Di luar jangkauan geometris lengan (domain trig invalid), ATAU
    - Sudut hasil IK di luar batas fisik servo (0-180, SG90 positional).

    Dipakai supaya main.py (mode otomatis, Milestone 11) bisa skip
    satu siklus deteksi tanpa crash / tanpa mengirim sudut yang bisa
    merusak servo secara fisik.
    """
    pass


class InverseKinematics:
    """
    Menghitung sudut base, shoulder, elbow dari koordinat robot (cm).

    Rumus di dalam compute() adalah hasil kalibrasi fisik Odi
    (trial-and-error di hardware asli, tervalidasi presisi di seluruh
    titik ekstrim ROI). JANGAN diubah tanpa validasi ulang di hardware.

    Milestone 11: ditambah validasi batas workspace (Decision #056) -
    logika rumus IK itu sendiri TIDAK disentuh sama sekali.
    """

    # Batas fisik servo (SG90 180 positional, Milestone 8 revisi).
    # Asumsi sementara: sama rata 0-180 untuk ketiga servo. Kalau ada
    # batas fisik lebih sempit (mis. shoulder mentok badan robot di
    # sudut tertentu), sesuaikan konstanta ini - tidak perlu ubah rumus.
    BASE_MIN, BASE_MAX = 0.0, 180.0
    SHOULDER_MIN, SHOULDER_MAX = 0.0, 180.0
    ELBOW_MIN, ELBOW_MAX = 0.0, 180.0

    def __init__(self):

        # Konstanta geometri arm (hasil kalibrasi fisik)
        self.tinggi = 8.3
        self.L1 = 7
        self.L2 = 12

    def compute(self, x_cm, y_cm):
        """
        Input : x_cm, y_cm - koordinat robot (cm), hasil Mapping.pixel_to_robot()
        Return: (base_angle, shoulder_angle, elbow_angle) dalam derajat, float biasa

        Raises:
            WorkspaceError - target di luar jangkauan geometris ATAU
                              sudut hasil di luar batas fisik servo.
        """

        Tinggi = self.tinggi
        L1 = self.L1
        L2 = self.L2

        l = mt.sqrt(x_cm**2 + y_cm**2)
        h = mt.sqrt(l**2 + Tinggi**2)
        x = (h**2 - (L2**2 - L1**2)) / (2 * h)

        # --- Domain check: shoulder ---
        cos_theta = x / L1
        if not (-1.0 <= cos_theta <= 1.0):
            raise WorkspaceError(
                f"Target ({x_cm:.2f},{y_cm:.2f})cm di luar jangkauan lengan "
                f"(shoulder domain invalid, cos_theta={cos_theta:.3f})"
            )

        # menghitung shoulder angle
        theta = mt.degrees(mt.acos(cos_theta))
        k = mt.degrees(mt.atan(l / Tinggi))
        sudutbuang = theta + k
        sudutingin = 155 - sudutbuang
        shoulder_angle = 90 - sudutingin

        # --- Domain check: elbow ---
        cos_alfa = (L1**2 + L2**2 - h**2) / (2 * L1 * L2)
        if not (-1.0 <= cos_alfa <= 1.0):
            raise WorkspaceError(
                f"Target ({x_cm:.2f},{y_cm:.2f})cm di luar jangkauan lengan "
                f"(elbow domain invalid, cos_alfa={cos_alfa:.3f})"
            )

        # menghitung elbow angle
        alfa = mt.degrees(mt.acos(cos_alfa))
        A = alfa - 87
        elbow_angle = 90 - A  # Ubah tanda kalo putarnya salah

        # menghitung base angle
        base_calculation = mt.degrees(mt.atan2(y_cm, x_cm))
        if base_calculation < 90:
            base_angle = base_calculation + 5
        else:
            base_angle = base_calculation +  (base_calculation/8) #koreksi overshoot

        # --- Servo limit check (Decision #056, Milestone 11) ---
        self._check_limit("base", base_angle, self.BASE_MIN, self.BASE_MAX)
        self._check_limit("shoulder", shoulder_angle, self.SHOULDER_MIN, self.SHOULDER_MAX)
        self._check_limit("elbow", elbow_angle, self.ELBOW_MIN, self.ELBOW_MAX)

        return float(base_angle), float(shoulder_angle), float(elbow_angle)

    def _check_limit(self, name, angle, lo, hi):

        if not (lo <= angle <= hi):
            raise WorkspaceError(
                f"{name}_angle={angle:.2f} di luar batas servo [{lo}, {hi}]"
            )