import lgpio
import time

STEP = 23
DIR = 24
ENABLE = 25

chip = lgpio.gpiochip_open(0)

lgpio.gpio_claim_output(chip, STEP, 0)
lgpio.gpio_claim_output(chip, DIR, 0)
lgpio.gpio_claim_output(chip, ENABLE, 0)

# Enable motor
lgpio.gpio_write(chip, ENABLE, 1)

# Direction
lgpio.gpio_write(chip, DIR, 1)

print("Motor moving")


delay = 0.00005   # 50 microseconds

while True:
    lgpio.gpio_write(chip, STEP, 1)
    time.sleep(delay)
    lgpio.gpio_write(chip, STEP, 0)
    time.sleep(delay)
    lgpio.gpio_write(chip, DIR, 1)

print("Done")

# Disable
lgpio.gpio_write(chip, ENABLE, 0)

lgpio.gpiochip_close(chip)