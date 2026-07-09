import cv2

from camera import Camera
from detection import Detection
from config import DetectionConfig, WindowConfig


def main():

    camera = Camera()
    detection = Detection()

    try:

        camera.open()

        print(f"Tekan '{DetectionConfig.CAPTURE_REF_KEY}' saat ROI kosong untuk menangkap reference frame.")

        while True:

            frame, roi = camera.read()

            if frame is None:
                print("Error: Gagal membaca frame.")
                break

            camera.update_fps()

            object_found = False
            contours = []
            mask = None

            if detection.has_reference():
                object_found, contours, mask = detection.detect(roi)

            roi_display = detection.draw_contours(roi, contours) if contours else roi

            frame = camera.draw_info(frame)
            frame = camera.draw_roi(frame)
            frame = detection.draw_status(frame, object_found)

            camera.show(frame)
            camera.show_roi(roi_display)

            if mask is not None:
                cv2.imshow(WindowConfig.MASK_WINDOW, mask)

            key = camera.get_key()

            if key == ord('q'):
                break

            if key == ord(DetectionConfig.CAPTURE_REF_KEY):
                detection.set_reference(roi)
                print("Reference frame captured.")

    except Exception as e:

        print(f"Error: {e}")

    finally:

        camera.release()


if __name__ == "__main__":
    main()