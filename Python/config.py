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
    X: int = 250
    Y: int = 100
    WIDTH: int = 800
    HEIGHT: int = 500


# ==========================================================
# Object Detection (Milestone 2)
# ==========================================================

@dataclass(frozen=True)
class DetectionConfig:

    # Preprocessing (Gaussian blur, harus ganjil)
    BLUR_KERNEL: int = 11

    # Background subtraction
    DIFF_THRESHOLD: int = 23

    # Morphology
    MORPH_KERNEL: int = 5
    MORPH_ITERATIONS: int = 2

    # Contour filtering
    MIN_CONTOUR_AREA: int = 50

    # Keyboard shortcut untuk menangkap reference frame
    CAPTURE_REF_KEY: str = "r"


# ==========================================================
# HSV Threshold (Milestone 3)
# ==========================================================

@dataclass(frozen=True)
class HSVConfig:

    BLACK_LOWER: tuple = (0, 65, 0)
    BLACK_UPPER: tuple = (180, 255, 101)

    WHITE_LOWER: tuple = (36, 0, 141)
    WHITE_UPPER: tuple = (180, 255, 255)


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

    PIXEL_TO_CM_X: float = 1.0
    PIXEL_TO_CM_Y: float = 1.0


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