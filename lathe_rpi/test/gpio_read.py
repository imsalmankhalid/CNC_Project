from gpiozero import DigitalInputDevice
from time import sleep

gpio16 = DigitalInputDevice(16, pull_up=True)
gpio8 = DigitalInputDevice(8, pull_up=True)

last16 = gpio16.value
last8 = gpio8.value

print(f"GPIO16 = {last16}, GPIO8 = {last8}")

while True:
    val16 = gpio16.value
    val8 = gpio8.value

    if val16 != last16 or val8 != last8:
        print(f"GPIO16 = {val16}, GPIO8 = {val8}")
        last16 = val16
        last8 = val8

    sleep(0.01)