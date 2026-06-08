import time
import os
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def create_bar(voltage, max_voltage=3.3, bar_length=30):
    """Generates a text-based progress bar based on current voltage."""
    # Ensure voltage stays within bounds for the calculation
    voltage = max(0.0, min(voltage, max_voltage))
    
    # Calculate percentage and fill length
    percent = (voltage / max_voltage) * 100
    filled_length = int(round(bar_length * voltage / max_voltage))
    
    # Create the visual bar string
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    return f"[{bar}] {percent:5.1f}% ({voltage:.3f}V)"

def main():
    try:
        # Initialize I2C bus and the ADS1115 chip
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        
        # Define channel A0
        chan = AnalogIn(ads, ADS.P0)
        
        print("Reading potentiometer on A0. Press Ctrl+C to exit.\n")
        
        while True:
            # Generate the progress bar string
            # Note: Change max_voltage to 5.0 if your pot is tied to 5V instead of 3.3V
            bar_output = create_bar(chan.voltage, max_voltage=3.3)
            
            # Print the bar and return the cursor to the start of the line (\r)
            # end="" prevents jumping to a new line, creating an active animation
            print(f"\r{bar_output}", end="", flush=True)
            
            # Small delay to keep the terminal responsive
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\nExiting program.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
