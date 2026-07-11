import numpy as np
import cv2

from camera import Camera
from detection import Detection
from config import DetectionConfig

CAPTURE_KEY = "c"
QUIT_KEY = "q"

CORNER_LABELS = [
    "Titik 1 (kiri-atas ROI)",
    "Titik 2 (kanan-atas ROI)",
    "Titik 3 (kanan-bawah ROI)",
    "Titik 4 (kiri-bawah ROI)",
]


def prompt_robot_coordinate(label):

    print(f"\n--- {label} ---")
    print("Masukkan koordinat robot (cm), diukur dari pusat servo base.")
    print("  X+ : ke arah drop area putih (kanan)")
    print("  Y+ : menjauh dari base, ke arah workspace/ROI")

    while True:
        try:
            x_cm = float(input("  x_cm: "))
            y_cm = float(input("  y_cm: "))
            return x_cm, y_cm
        except ValueError:
            print("  Input tidak valid, masukkan angka.")


def fit_homography(pixel_points, robot_points):
    """
    Exact solve homography dari 4 pasang titik korespondensi
    (pixel -> robot cm) via cv2.getPerspectiveTransform.
    """

    src = np.array(pixel_points, dtype=np.float32)
    dst = np.array(robot_points, dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(src, dst)

    return matrix


def print_result(matrix):

    flat = matrix.flatten().tolist()

    print("\n" + "=" * 50)
    print("Salin nilai berikut ke MappingConfig di config.py:")
    print("=" * 50)
    print("    HOMOGRAPHY_MATRIX: tuple = (")
    print(f"        {flat[0]}, {flat[1]}, {flat[2]},")
    print(f"        {flat[3]}, {flat[4]}, {flat[5]},")
    print(f"        {flat[6]}, {flat[7]}, {flat[8]},")
    print("    )")
    print("=" * 50)


def main():

    camera = Camera()
    detection = Detection()

    pixel_points = []
    robot_points = []

    try:

        camera.open()

        print("=" * 50)
        print("Kalibrasi Camera-to-Robot Mapping (Homography)")
        print("=" * 50)
        print(f"Tekan '{DetectionConfig.CAPTURE_REF_KEY}' saat ROI kosong untuk menangkap reference frame.")
        print("Lalu untuk tiap titik kalibrasi:")
        print("  1. Taruh objek fisik tepat di titik itu.")
        print(f"  2. Tekan '{CAPTURE_KEY}' untuk menangkap centroid pixel-nya.")
        print("  3. Masukkan koordinat robot (cm) titik itu lewat console.")
        print(f"Ulangi untuk ke-4 titik pojok ROI. Tekan '{QUIT_KEY}' untuk keluar kapan saja.")
        print("=" * 50)

        corner_index = 0

        while corner_index < len(CORNER_LABELS):

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
                print("Kalibrasi dibatalkan.")
                camera.release()
                return

            if key == ord(DetectionConfig.CAPTURE_REF_KEY):
                detection.set_reference(roi)
                print("Reference frame captured.")

            if key == ord(CAPTURE_KEY):

                if not detection.has_reference():
                    print("Reference frame belum diambil.")
                    continue

                if len(objects) == 0:
                    print("Tidak ada objek terdeteksi. Pastikan objek ada di ROI.")
                    continue

                if len(objects) > 1:
                    print("Lebih dari satu objek terdeteksi. Sisakan satu objek saja di ROI.")
                    continue

                centroid = objects[0]["centroid"]
                print(f"Centroid pixel tertangkap: {centroid}")

                x_cm, y_cm = prompt_robot_coordinate(CORNER_LABELS[corner_index])

                pixel_points.append(centroid)
                robot_points.append((x_cm, y_cm))

                corner_index += 1

        matrix = fit_homography(pixel_points, robot_points)

        print_result(matrix)

    except Exception as e:

        print(f"Error: {e}")

    finally:

        camera.release()


if __name__ == "__main__":
    main()