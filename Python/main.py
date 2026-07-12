import cv2

from camera import Camera
from detection import Detection
from color import Color
from selection import Selection
from mapping import Mapping
from serial_comm import SerialComm
from config import DetectionConfig, WindowConfig


def main():

    camera = Camera()
    detection = Detection()
    color = Color()
    selection = Selection(color)
    mapping = Mapping()
    serial_comm = SerialComm()

    try:

        camera.open()
        serial_comm.connect()

        print(f"Tekan '{DetectionConfig.CAPTURE_REF_KEY}' saat ROI kosong untuk menangkap reference frame.")
        print("Tekan 'p' untuk print objek terpilih ke console.")
        print("Tekan 's' untuk kirim objek terpilih ke Arduino via serial.")

        while True:

            frame, roi = camera.read()

            if frame is None:
                print("Error: Gagal membaca frame.")
                break

            camera.update_fps()

            objects = []
            mask = None
            selected = None

            if detection.has_reference():
                objects, mask = detection.detect(roi)

            if objects:
                selected = selection.select(roi, objects)

            roi_display = detection.draw_objects(roi, objects) if objects else roi
            roi_display = selection.draw_selected(roi_display, selected)

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
                if selected:
                    cx, cy = selected["centroid"]
                    print(f"Selected: #{selected['id']} {selected['color']} ({cx},{cy})")
                elif objects:
                    print("Objects detected, but none with valid color (all UNKNOWN).")
                else:
                    print("No Object")

            if key == ord('s'):

                if selected:

                    x_cm, y_cm = mapping.pixel_to_robot(selected["centroid"])
                    print(f"Mapping: pixel {selected['centroid']} -> robot ({x_cm:.2f}, {y_cm:.2f}) cm")

                    ok = serial_comm.send_and_wait(selected["color"], x_cm, y_cm)

                    if not ok:
                        print("Komunikasi serial gagal setelah beberapa percobaan. Menghentikan program.")
                        break

                elif objects:
                    print("Ada objek terdeteksi, tapi tidak ada yang warnanya valid (semua UNKNOWN).")
                else:
                    print("Tidak ada objek untuk dikirim.")

    except Exception as e:

        print(f"Error: {e}")

    finally:

        serial_comm.close()
        camera.release()


if __name__ == "__main__":
    main()