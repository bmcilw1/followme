import Adafruit_BBIO.PWM as PWM
import time

pin1 = "P9_14"

PWM.start(pin1, 30, 4000)

time.sleep(5)

PWM.stop(pin1)
PWM.cleanup()