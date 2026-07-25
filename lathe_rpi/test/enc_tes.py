import time
from gpiozero import RotaryEncoder


# Define the pins using the BCM GPIO numbers (not the physical pin numbers)
# Encoder 1: GPIO 13 / 19
# Encoder 2: GPIO 5  / 6
PIN_A1 = 13
PIN_B1 = 19
PIN_A2 = 5
PIN_B2 = 6

print("Initializing AMT103-V Encoders...")
print(f"Encoder1 -> A: GPIO {PIN_A1}, B: GPIO {PIN_B1}")
print(f"Encoder2 -> A: GPIO {PIN_A2}, B: GPIO {PIN_B2}")

# Initialize both encoders (max_steps=0 for unbounded rotation)
enc1 = RotaryEncoder(PIN_A1, PIN_B1, max_steps=0)
enc2 = RotaryEncoder(PIN_A2, PIN_B2, max_steps=0)

print("Encoders ready! Spin the shafts... (Press Ctrl+C to exit)\n")

# Keep track of last positions to avoid spamming the terminal
last1 = None
last2 = None

try:
    while True:
        v1 = enc1.steps
        v2 = enc2.steps

        lines = []

        if v1 != last1:
            if last1 is not None:
                d1 = "CW ↻" if v1 > last1 else "CCW ↺"
            else:
                d1 = "Initialized"
            lines.append(f"Enc1: {v1:<6} | {d1}")
            last1 = v1

        if v2 != last2:
            if last2 is not None:
                d2 = "CW ↻" if v2 > last2 else "CCW ↺"
            else:
                d2 = "Initialized"
            lines.append(f"Enc2: {v2:<6} | {d2}")
            last2 = v2

        if lines:
            print("  ".join(lines))

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nEncoder testing stopped by user.")

