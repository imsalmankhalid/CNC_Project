import time
import board
from adafruit_ads1x15 import ADS1015, AnalogIn, ads1x15

# Create the I2C bus
i2c = board.I2C()

# Create the ADC object using the I2C bus
ads = ADS1015(i2c)

# Create single-ended input on channel 0
chan = AnalogIn(ads, ads1x15.Pin.A0)

# Create differential input between channel 0 and 1
# chan = AnalogIn(ads, ads1x15.Pin.A0, ads1x15.Pin.A1)

print("Reading A0... Press Ctrl+C to stop.\n")

# Configuration for the bar
BAR_LENGTH = 30
MAX_VOLTAGE = 3.3  # Change to 5.0 if your potentiometer is wired to 5V

try:
    while True:
        # Get the current reading
        voltage = chan.voltage
        raw_val = chan.value
        
        # Keep voltage within safe bounds for the math calculation
        safe_voltage = max(0.0, min(voltage, MAX_VOLTAGE))
        
        # Calculate how much of the bar to fill
        filled_length = int(round(BAR_LENGTH * safe_voltage / MAX_VOLTAGE))
        
        # Construct the bar characters
        bar = '█' * filled_length + '-' * (BAR_LENGTH - filled_length)
        
        # Format the output line: raw value, voltage, and the visual bar
        # \r moves the cursor back to the start of the line so it overwrites itself
        output = f"\rRaw: {raw_val:>5} | V: {voltage:>5.3f}V [{bar}]"
        
        print(output, end="", flush=True)
        time.sleep(0.1)  # Sped up slightly to 0.1s for a smoother bar animation

except KeyboardInterrupt:
    print("\n\nExiting program.")
