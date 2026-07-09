from camera import Camera


def main():

    camera = Camera()

    try:

        camera.open()

        while True:

            frame, roi = camera.read()

            if frame is None:
                print("Error: Gagal membaca frame.")
                break

            camera.update_fps()

            frame = camera.draw_info(frame)

            frame = camera.draw_roi(frame)

            camera.show(frame)

            camera.show_roi(roi)

            if camera.is_quit():
                break

    except Exception as e:

        print(f"Error: {e}")

    finally:

        camera.release()


if __name__ == "__main__":
    main()
