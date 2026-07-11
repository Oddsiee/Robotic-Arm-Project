from camera import Camera
from detection import Detection
from mapping import Mapping
from config import DetectionConfig

CAPTURE_KEY = "c"
QUIT_KEY = "q"


def main():

    camera = Camera()
    detection = Detection()
    mapping = Mapping()

    try:

        camera.open()

        print("=" * 50)
        print("Validasi Mapping")
        print("=" * 50)
        print(f"Tekan '{DetectionConfig.CAPTURE_REF_KEY}' saat ROI kosong untuk reference frame.")
        print("Taruh objek di titik mana pun di ROI (bukan salah satu titik kalibrasi),")
        print(f"lalu tekan '{CAPTURE_KEY}' untuk lihat hasil mapping-nya.")
        print("Bandingkan sama posisi asli yang kamu ukur di kertas grid.")
        print(f"Tekan '{QUIT_KEY}' untuk keluar.")
        print("=" * 50)

        while True:

            frame, roi = camera.read()

            if frame is None:
                print("Error: Gagal membaca frame.")
                break

            objects = []

            if detection.has_reference():
                objects, mask = detection.detect(roi)
                roi_display = detection.draw_objects(roi, objects) if objects else roi
            else:
                roi_display = roi

            frame = camera.draw_roi(frame)
            camera.show(frame)
            camera.show_roi(roi_display)

            key = camera.get_key()

            if key == ord(QUIT_KEY):
                break

            if key == ord(DetectionConfig.CAPTURE_REF_KEY):
                detection.set_reference(roi)
                print("Reference frame captured.")

            if key == ord(CAPTURE_KEY):

                if len(objects) == 0:
                    print("Tidak ada objek terdeteksi.")
                    continue

                if len(objects) > 1:
                    print("Lebih dari satu objek terdeteksi, sisakan satu.")
                    continue

                centroid = objects[0]["centroid"]
                x_cm, y_cm = mapping.pixel_to_robot(centroid)

                print(f"Pixel {centroid} -> Robot ({x_cm:.2f}, {y_cm:.2f}) cm")

    except Exception as e:

        print(f"Error: {e}")

    finally:

        camera.release()


if __name__ == "__main__":
    main()