import cv2

from camera import Camera
from detection import Detection
from color import Color
from selection import Selection
from mapping import Mapping
from inverse_kinematics import InverseKinematics, WorkspaceError
from dwell_lock import DwellLock
from serial_comm import SerialComm
from config import DetectionConfig, WindowConfig, DwellLockConfig


def main():

    camera = Camera()
    detection = Detection()
    color = Color()
    selection = Selection(color)
    mapping = Mapping()
    ik = InverseKinematics()
    dwell_lock = DwellLock(DwellLockConfig.LOCK_DURATION, DwellLockConfig.POSITION_TOLERANCE)
    serial_comm = SerialComm()

    try:

        camera.open()
        serial_comm.connect()

        print(f"Tekan '{DetectionConfig.CAPTURE_REF_KEY}' saat ROI kosong untuk menangkap reference frame.")
        print(f"Setelah reference frame diset, objek yang diam >= {DwellLockConfig.LOCK_DURATION}s otomatis diproses.")
        print("Tekan 'p' untuk print objek terpilih ke console (debug).")
        print("Tekan 'q' untuk keluar.")

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

            # Update dwell lock TIAP frame (walau selected None), supaya
            # timer reset begitu objek hilang/berpindah (Decision #058).
            locked, remaining = dwell_lock.update(selected)

            roi_display = detection.draw_objects(roi, objects) if objects else roi
            roi_display = selection.draw_selected(roi_display, selected)
            roi_display = dwell_lock.draw_status(roi_display, selected, locked, remaining)

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
                dwell_lock.reset()
                print("Reference frame captured. Mode otomatis aktif.")

            if key == ord('p'):
                if selected:
                    cx, cy = selected["centroid"]
                    print(f"Selected: #{selected['id']} {selected['color']} ({cx},{cy})")
                elif objects:
                    print("Objects detected, but none with valid color (all UNKNOWN).")
                else:
                    print("No Object")

            # ==================================================
            # Mode Otomatis (Milestone 11, Decision #055 + #058)
            #
            # Diproses HANYA kalau objek sudah "locked" oleh DwellLock
            # (diam di posisi+warna yang sama >= LOCK_DURATION detik).
            # Mencegah sistem memicu pick-and-place saat objek masih
            # bergerak / tangan operator masih di ROI.
            #
            # send_angles_and_wait() sifatnya blocking (nunggu "DONE"),
            # jadi loop ini otomatis "pause" sendiri selama Arduino
            # menjalankan siklus fisiknya (Decision #030/#031 tetap
            # berlaku).
            # ==================================================
            if locked:

                x_cm, y_cm = mapping.pixel_to_robot(selected["centroid"])

                try:
                    base_angle, shoulder_angle, elbow_angle = ik.compute(x_cm, y_cm)
                except WorkspaceError as e:
                    # Target di luar jangkauan geometris atau di luar
                    # batas fisik servo (Decision #056) - skip siklus
                    # ini. Reset lock supaya wajib nunggu dwell-time
                    # baru lagi sebelum retry (bukan spam tiap frame).
                    print(f"[SKIP] {e}")
                    dwell_lock.reset()
                    continue

                print(
                    f"Auto-pick: {selected['color']} pixel {selected['centroid']} "
                    f"-> robot ({x_cm:.2f},{y_cm:.2f})cm "
                    f"-> base={base_angle:.2f} shoulder={shoulder_angle:.2f} elbow={elbow_angle:.2f}"
                )

                ok = serial_comm.send_angles_and_wait(
                    selected["color"], base_angle, shoulder_angle, elbow_angle
                )

                # Reset lock setelah satu siklus selesai (berhasil atau
                # gagal) - siklus berikutnya wajib mulai dwell-time baru.
                dwell_lock.reset()

                if not ok:
                    print("Komunikasi serial gagal setelah beberapa percobaan. Menghentikan program.")
                    break

    except Exception as e:

        print(f"Error: {e}")

    finally:

        serial_comm.close()
        camera.release()


if __name__ == "__main__":
    main()