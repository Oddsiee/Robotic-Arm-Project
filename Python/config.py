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
        -0.008550255654884004, 0.004906254139413923, 4.555445386498193,
        -0.017464071369826202, -0.006900203197459619, 14.448876209971186,
        -0.001130122111242908, -0.0006667793878077274, 1.0,
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