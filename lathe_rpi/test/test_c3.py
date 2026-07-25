#!/usr/bin/env python3

import gpiod
import time

LINE = 12

with gpiod.request_lines(
    "/dev/gpiochip0",
    consumer="gpio-monitor",
    config={
        LINE: gpiod.LineSettings()
    }
) as request:
    count = 0
    while True:
        value = request.get_value(LINE)

        if value == gpiod.line.Value.INACTIVE:
            count = count + 1
            print(count)

        time.sleep(0.1)