from dataclasses import dataclass


# ==========================================================
# Camera Configuration
# ==========================================================

@dataclass(frozen=True)
class CameraConfig:
    INDEX: int = 1
    WIDTH: int = 1280
    HEIGHT: int = 720
    FPS: int = 30


# ==========================================================
# Window Configuration
# ==========================================================

@dataclass(frozen=True)
class WindowConfig:
    CAMERA_WINDOW: str = "Robotic Arm Camera"
    ROI_WINDOW: str = "ROI"
    MASK_WINDOW: str = "Mask"


# ==========================================================
# ROI (Region of Interest)
# ==========================================================

@dataclass(frozen=True)
class ROIConfig:
    #Naik untuk ke kanan, turun untuk ke kiri
    X: int = 200
    #Naik untuk turun, turun untuk naik
    Y: int = 45
    WIDTH: int = 780
    HEIGHT: int = 366


# ==========================================================
# Object Detection (Milestone 2)
# ==========================================================

@dataclass(frozen=True)
class DetectionConfig:

    # Preprocessing (Gaussian blur, harus ganjil)
    BLUR_KERNEL: int = 19

    # Background subtraction
    DIFF_THRESHOLD: int = 16

    # Morphology
    MORPH_KERNEL: int = 8
    MORPH_ITERATIONS: int = 2

    # Contour filtering
    MIN_CONTOUR_AREA: int = 500

    # Keyboard shortcut untuk menangkap reference frame
    CAPTURE_REF_KEY: str = "r"


# ==========================================================
# HSV Threshold (Milestone 3)
# ==========================================================

@dataclass(frozen=True)
class HSVConfig:

    BLACK_LOWER: tuple = (16, 23, 0)
    BLACK_UPPER: tuple = (180, 255, 85)

    WHITE_LOWER: tuple = (0, 19, 149)
    WHITE_UPPER: tuple = (119, 255, 255)


# ==========================================================
# Serial Communication (Milestone 7)
# ==========================================================

@dataclass(frozen=True)
class SerialConfig:

    PORT: str = "COM3"
    BAUDRATE: int = 115200
    TIMEOUT: float = 1.0


# ==========================================================
# Camera Mapping (Milestone 6)
# ==========================================================

@dataclass(frozen=True)
class MappingConfig:

    # Matriks homography 3x3 (row-major, 9 elemen), hasil kalibrasi
    # via cv2.getPerspectiveTransform. Default identity = placeholder.
    HOMOGRAPHY_MATRIX: tuple = ( 
        -0.021360002752026905, -0.0002797024488239314, 8.5058115133451,
        6.785965451184588e-06, 0.02082410696384706, 9.16391150847448,
        1.3998777055323363e-05, -2.6069606878315492e-05, 1.0,
    )


# ==========================================================
# Robot Geometry (Milestone 8 & 9)
# ==========================================================

@dataclass(frozen=True)
class RobotConfig:

    LINK1: float = 8.0
    LINK2: float = 6.0
    LINK3: float = 4.0
    GRIPPER: float = 10.0


# ==========================================================
# Servo Configuration
# ==========================================================

@dataclass(frozen=True)
class ServoConfig:

    BASE_HOME: int = 90
    SHOULDER_HOME: int = 90
    ELBOW_HOME: int = 90
    GRIPPER_OPEN: int = 90
    GRIPPER_CLOSE: int = 20

# ==========================================================
# Serial Communication (Milestone 7)
# ==========================================================

@dataclass(frozen=True)
class SerialConfig:

    PORT: str = "COM5"          # placeholder, update manual sesuai port Arduino kamu
    BAUDRATE: int = 115200
    TIMEOUT: float = 1.0        # timeout per-read pyserial (level koneksi)

    ACK_TIMEOUT: float = 5.0    # total waktu tunggu balasan "DONE"
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 0.5    # jeda antar percobaan retry
    ACK_TOKEN: str = "DONE"