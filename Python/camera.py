import cv2
import time

from config import CameraConfig, ROIConfig, WindowConfig


class Camera:

    def __init__(self):

        # Camera configuration
        self.camera_index = CameraConfig.INDEX
        self.width = CameraConfig.WIDTH
        self.height = CameraConfig.HEIGHT
        self.window_name = WindowConfig.CAMERA_WINDOW

        # ROI configuration
        self.roi_x = ROIConfig.X
        self.roi_y = ROIConfig.Y
        self.roi_width = ROIConfig.WIDTH
        self.roi_height = ROIConfig.HEIGHT

        # Camera object
        self.cap = None

        # FPS
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0.0

    def open(self):

        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Webcam tidak dapat dibuka.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        # Membaca resolusi aktual kamera
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print("=" * 40)
        print("Robotic Arm Camera")
        print("=" * 40)
        print(f"Resolution : {self.width} x {self.height}")
        print(f"Target FPS : {CameraConfig.FPS}")
        print("Press 'q' to quit")
        print("=" * 40)

    def read(self):

        ret, frame = self.cap.read()

        if not ret:
            return None, None

        roi = self.crop_roi(frame)

        return frame, roi

    def crop_roi(self, frame):

        return frame[
            self.roi_y:self.roi_y + self.roi_height,
            self.roi_x:self.roi_x + self.roi_width
        ]

    def update_fps(self):

        self.frame_count += 1

        elapsed = time.time() - self.start_time

        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()

    def draw_info(self, frame):

        cv2.putText(
            frame,
            f"FPS : {self.fps:.1f}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Resolution : {self.width} x {self.height}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        return frame

    def draw_roi(self, frame):

        cv2.rectangle(
            frame,
            (self.roi_x, self.roi_y),
            (
                self.roi_x + self.roi_width,
                self.roi_y + self.roi_height
            ),
            (0, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "ROI",
            (self.roi_x, self.roi_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        return frame

    def show(self, frame):

        cv2.imshow(self.window_name, frame)

    def show_roi(self, roi):

        cv2.imshow(WindowConfig.ROI_WINDOW, roi)

    def get_key(self):

        return cv2.waitKey(1) & 0xFF

    def is_quit(self):

        return cv2.waitKey(1) & 0xFF == ord('q')

    def release(self):

        if self.cap is not None:
            self.cap.release()

        cv2.destroyAllWindows()