from gpiozero import Button
from signal import pause

PIN = 16
press_count = 0

# Active-low input with pull-up enabled
switch = Button(PIN, pull_up=True)

def pressed():
    global press_count
    press_count += 1
    print(f"Switch is pressed: {press_count}")

switch.when_pressed = pressed

print("Monitoring GPIO 16...")
print("Press Ctrl+C to exit.")

pause()