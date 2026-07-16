import cv2

from camera import Camera
from detection import Detection
from color import Color
from selection import Selection
from mapping import Mapping
from inverse_kinematics import InverseKinematics, WorkspaceError
from dwell_lock import DwellLock
from serial_comm import SerialComm
from dashboard import Dashboard
from config import DetectionConfig, DwellLockConfig


def main():

    camera = Camera()
    detection = Detection()
    color = Color()
    selection = Selection(color)
    mapping = Mapping()
    ik = InverseKinematics()
    dwell_lock = DwellLock(DwellLockConfig.LOCK_DURATION, DwellLockConfig.POSITION_TOLERANCE)
    dashboard = Dashboard()

    # Dashboard di-inject sebagai logger ke SerialComm (dependency
    # injection, konsisten dengan pola project) - semua print internal
    # SerialComm (kirim, ack DONE, retry, error) otomatis tampil di
    # panel log dashboard, bukan cuma di terminal.
    serial_comm = SerialComm(logger=dashboard)

    try:

        camera.open()
        serial_comm.connect()

        dashboard.log(f"Tekan '{DetectionConfig.CAPTURE_REF_KEY}' saat ROI kosong untuk menangkap reference frame.", "INFO")
        dashboard.log(f"Setelah reference frame diset, objek yang diam >= {DwellLockConfig.LOCK_DURATION}s otomatis diproses.", "INFO")
        dashboard.log("Tekan 'p' untuk print objek terpilih ke log (debug).", "INFO")
        dashboard.log("Tekan 'm' untuk toggle panel Mask (debug).", "INFO")
        dashboard.log("Tekan 'q' untuk keluar.", "INFO")

        while True:

            frame, roi = camera.read()

            if frame is None:
                dashboard.log("Error: Gagal membaca frame.", "ERR")
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

            # ── Update dashboard state tiap frame ──
            dashboard.update_state(
                armed=detection.has_reference(),
                fps=camera.fps,
                selected=selected,
                locked=locked,
                remaining=remaining,
            )

            roi_display = detection.draw_objects(roi, objects) if objects else roi
            roi_display = selection.draw_selected(roi_display, selected)
            roi_display = dwell_lock.draw_status(roi_display, selected, locked, remaining)

            frame = camera.draw_info(frame)
            frame = camera.draw_roi(frame)
            frame = detection.draw_status(frame, objects)

            # Satu window: Camera + ROI (dengan status dwell-lock) +
            # Mask (toggle) + Log, menggantikan 3 window terpisah.
            composite = dashboard.render(frame, roi_display, mask)
            dashboard.show(composite)

            key = camera.get_key()

            if key == ord('q'):
                break

            if key == ord(DetectionConfig.CAPTURE_REF_KEY):
                detection.set_reference(roi)
                dwell_lock.reset()
                dashboard.log("Reference frame captured. Mode otomatis aktif.", "REF")

            if key == ord('m'):
                dashboard.toggle_mask()

            if key == ord('p'):
                if selected:
                    cx, cy = selected["centroid"]
                    dashboard.log(f"Selected: #{selected['id']} {selected['color']} ({cx},{cy})", "INFO")
                elif objects:
                    dashboard.log("Objects detected, but none with valid color (all UNKNOWN).", "INFO")
                else:
                    dashboard.log("No Object", "INFO")

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
                    dashboard.log(f"[SKIP] {e}", "SKIP")
                    dashboard.update_state(angles=None)
                    dwell_lock.reset()
                    continue

                # Update state: tampilkan IK angles di status card
                dashboard.update_state(
                    angles=(base_angle, shoulder_angle, elbow_angle),
                    processing=True,
                )

                dashboard.log(
                    f"Auto-pick: {selected['color']} pixel {selected['centroid']} "
                    f"-> robot ({x_cm:.2f},{y_cm:.2f})cm "
                    f"-> base={base_angle:.2f} shoulder={shoulder_angle:.2f} elbow={elbow_angle:.2f}",
                    "LOCK"
                )

                ok = serial_comm.send_angles_and_wait(
                    selected["color"], base_angle, shoulder_angle, elbow_angle
                )

                dashboard.update_state(
                    serial_ok=ok,
                    processing=False,
                    angles=None,
                    last_cmd=selected["color"] if ok else "",
                )

                dwell_lock.reset()

                if not ok:
                    dashboard.log("Komunikasi serial gagal setelah beberapa percobaan. Menghentikan program.", "ERR")
                    break

    except Exception as e:

        dashboard.log(f"Error: {e}")

    finally:

        serial_comm.close()
        camera.release()


if __name__ == "__main__":
    main()