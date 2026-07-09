import Python.serial as serial
import time
import keyboard

ser = serial.Serial('COM5', 9600)  # GANTI sesuai port kamu
time.sleep(2)  # PENTING: kasih waktu Arduino restart dulu

print("Tekan 'y' untuk toggle servo (tekan ESC untuk keluar)")

while True:
    if keyboard.is_pressed('y'):
        ser.write(b'y')
        print("Sinyal terkirim!")
        while keyboard.is_pressed('y'):
            pass
    if keyboard.is_pressed('esc'):
        break

ser.close()