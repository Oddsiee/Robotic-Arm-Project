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
        print("Tekan 'p' untuk print daftar objek (id + koordinat) ke console.")

        while True:

            frame, roi = camera.read()

            if frame is None:
                print("Error: Gagal membaca frame.")
                break

            camera.update_fps()

            objects = []
            mask = None

            if detection.has_reference():
                objects, mask = detection.detect(roi)

            roi_display = detection.draw_objects(roi, objects) if objects else roi

            frame = camera.draw_info(frame)
            frame = camera.draw_roi(frame)
            frame = detection.draw_status(frame, objects)

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

            if key == ord('p'):
                if objects:
                    for obj in objects:
                        cx, cy = obj["centroid"]
                        print(f"Object {obj['id']} ({cx},{cy})")
                else:
                    print("No Object")

    except Exception as e:

        print(f"Error: {e}")

    finally:

        camera.release()


if __name__ == "__main__":
    main()