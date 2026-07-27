from gpiozero import DigitalOutputDevice

gpio = DigitalOutputDevice(16)
gpio2 = DigitalOutputDevice(8)
gpio3 = DigitalOutputDevice(25)

while True:
    vol = int(input("Enter GPIO state (0/1): "))
    print(f"Setting GPIO state to: {vol}")
    gpio.value = vol
    gpio2.value = vol
    gpio3.value = vol