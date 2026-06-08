import time
from gpiozero import RotaryEncoder



# Define the pins using the BCM GPIO numbers (not the physical pin numbers)
# Physical Pin 29 = GPIO 5
# Physical Pin 31 = GPIO 6
PIN_A = 5
PIN_B = 6

print("Initializing AMT103-V Encoder...")
print(f"Tracking Pin A (GPIO {PIN_A}) and Pin B (GPIO {PIN_B})")

# Initialize the encoder
# max_steps=0 removes bounds so it can rotate infinitely positive or negative
encoder = RotaryEncoder(PIN_A, PIN_B, max_steps=0)

print("Encoder ready! Spin the shaft... (Press Ctrl+C to exit)\n")

# Keep track of the last known position to prevent terminal spam
last_steps = None

try:
    while True:
        # Read the current step position
        current_steps = encoder.steps
        
        # Only print when the encoder is turned
        if current_steps != last_steps:
            # Determine spinning direction
            if last_steps is not None:
                direction = "Clockwise ↻" if current_steps > last_steps else "Counter-Clockwise ↺"
            else:
                direction = "Initialized"
                
            print(f"Position Count: {current_steps:<5} | Direction: {direction}")
            last_steps = current_steps
            
        time.sleep(0.01)  # Keeps CPU usage low

except KeyboardInterrupt:
    print("\nTesting stopped by user.")

