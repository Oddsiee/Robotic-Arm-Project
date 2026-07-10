import cv2

from camera import Camera
from config import HSVConfig, WindowConfig


TRACKBAR_WINDOW = "HSV Calibration"


def nothing(x):
    pass


def create_trackbars():

    cv2.namedWindow(TRACKBAR_WINDOW)
    cv2.resizeWindow(TRACKBAR_WINDOW, 400, 500)

    # BLACK
    cv2.createTrackbar("B H MIN", TRACKBAR_WINDOW, HSVConfig.BLACK_LOWER[0], 180, nothing)
    cv2.createTrackbar("B S MIN", TRACKBAR_WINDOW, HSVConfig.BLACK_LOWER[1], 255, nothing)
    cv2.createTrackbar("B V MIN", TRACKBAR_WINDOW, HSVConfig.BLACK_LOWER[2], 255, nothing)
    cv2.createTrackbar("B H MAX", TRACKBAR_WINDOW, HSVConfig.BLACK_UPPER[0], 180, nothing)
    cv2.createTrackbar("B S MAX", TRACKBAR_WINDOW, HSVConfig.BLACK_UPPER[1], 255, nothing)
    cv2.createTrackbar("B V MAX", TRACKBAR_WINDOW, HSVConfig.BLACK_UPPER[2], 255, nothing)

    # WHITE
    cv2.createTrackbar("W H MIN", TRACKBAR_WINDOW, HSVConfig.WHITE_LOWER[0], 180, nothing)
    cv2.createTrackbar("W S MIN", TRACKBAR_WINDOW, HSVConfig.WHITE_LOWER[1], 255, nothing)
    cv2.createTrackbar("W V MIN", TRACKBAR_WINDOW, HSVConfig.WHITE_LOWER[2], 255, nothing)
    cv2.createTrackbar("W H MAX", TRACKBAR_WINDOW, HSVConfig.WHITE_UPPER[0], 180, nothing)
    cv2.createTrackbar("W S MAX", TRACKBAR_WINDOW, HSVConfig.WHITE_UPPER[1], 255, nothing)
    cv2.createTrackbar("W V MAX", TRACKBAR_WINDOW, HSVConfig.WHITE_UPPER[2], 255, nothing)


def read_trackbars():

    black_lower = (
        cv2.getTrackbarPos("B H MIN", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("B S MIN", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("B V MIN", TRACKBAR_WINDOW),
    )
    black_upper = (
        cv2.getTrackbarPos("B H MAX", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("B S MAX", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("B V MAX", TRACKBAR_WINDOW),
    )
    white_lower = (
        cv2.getTrackbarPos("W H MIN", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("W S MIN", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("W V MIN", TRACKBAR_WINDOW),
    )
    white_upper = (
        cv2.getTrackbarPos("W H MAX", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("W S MAX", TRACKBAR_WINDOW),
        cv2.getTrackbarPos("W V MAX", TRACKBAR_WINDOW),
    )

    return black_lower, black_upper, white_lower, white_upper


def print_result(black_lower, black_upper, white_lower, white_upper):

    print("=" * 50)
    print("Salin nilai berikut ke HSVConfig di config.py:")
    print("=" * 50)
    print(f"    BLACK_LOWER: tuple = {black_lower}")
    print(f"    BLACK_UPPER: tuple = {black_upper}")
    print()
    print(f"    WHITE_LOWER: tuple = {white_lower}")
    print(f"    WHITE_UPPER: tuple = {white_upper}")
    print("=" * 50)


def main():

    camera = Camera()

    try:

        camera.open()
        create_trackbars()

        print("=" * 50)
        print("Kalibrasi HSV Threshold")
        print("=" * 50)
        print("Geser trackbar sampai window 'Black Mask' dan 'White")
        print("Mask' hanya menyala putih di area objek yang sesuai.")
        print("Tekan 's' untuk cetak nilai ke console.")
        print("Tekan 'q' untuk keluar.")
        print("=" * 50)

        while True:

            frame, roi = camera.read()

            if frame is None:
                print("Error: Gagal membaca frame.")
                break

            black_lower, black_upper, white_lower, white_upper = read_trackbars()

            hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

            black_mask = cv2.inRange(hsv, black_lower, black_upper)
            white_mask = cv2.inRange(hsv, white_lower, white_upper)

            camera.show(camera.draw_roi(frame))
            camera.show_roi(roi)
            cv2.imshow("Black Mask", black_mask)
            cv2.imshow("White Mask", white_mask)

            key = camera.get_key()

            if key == ord('q'):
                break

            if key == ord('s'):
                print_result(black_lower, black_upper, white_lower, white_upper)

    except Exception as e:

        print(f"Error: {e}")

    finally:

        camera.release()


if __name__ == "__main__":
    main()