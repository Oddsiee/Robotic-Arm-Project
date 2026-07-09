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
# HSV Threshold (Milestone 3)
# ==========================================================

@dataclass(frozen=True)
class HSVConfig:

    # Placeholder
    BLACK_LOWER: tuple = (0, 0, 0)
    BLACK_UPPER: tuple = (180, 255, 60)

    WHITE_LOWER: tuple = (0, 0, 180)
    WHITE_UPPER: tuple = (180, 50, 255)


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
