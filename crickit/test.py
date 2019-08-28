#!/usr/bin/python3

# Drive NeoPixels on the NeoPixels Block on Crickit FeatherWing
import logging
import time
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel

num_pixels = 64  # Number of pixels driven from Crickit NeoPixel terminal

#pixels = NeoPixel(crickit.seesaw, 20, 50)
#BLACK = (0, 0, 0)
#pixels.fill(BLACK)
# The following line sets up a NeoPixel strip on Seesaw pin 20 for Feather
pixels = NeoPixel(crickit.seesaw, 20, num_pixels)
BLACK = (0, 0, 0)
pixels.fill(BLACK)
time.sleep(0.2)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        #pixels.show()
    time.sleep(0.5)

def rainbow_cycle(wait):
    for j in range(16):
        for i in range(6):
            for k in range(6):
                idx = (i)*8 + (k+2)
                rc_index = (idx * 256 // num_pixels) + (j*4)
                #print("pixels[%d] = %d" % (idx, rc_index))
                time.sleep(0.002)
                pixels[idx] = wheel(rc_index & 255)
        #pixels.show()
        #time.sleep(wait)

RED = (128, 0, 0)
YELLOW = (128, 75, 0)
GREEN = (0, 128, 0)
CYAN = (0, 128, 128)
BLUE = (0, 0, 128)
PURPLE = (90, 0, 128)


try:
    pixels.brightness = 50
    while True:
        #print("fill")
        #pixels.fill(RED)
        #pixels.show()
        # Increase or decrease to change the speed of the solid color change.
        #time.sleep(1)
        #pixels.fill(GREEN)
        #pixels.show()
        #time.sleep(1)
        #pixels.fill(BLUE)
        #pixels.show()
        #time.sleep(1)

        #print("chase")
        #color_chase(RED, 0.1)  # Increase the number to slow down the color chase
        #color_chase(YELLOW, 0.1)
        #color_chase(GREEN, 0.1)
        #color_chase(CYAN, 0.1)
        #color_chase(BLUE, 0.1)
        #color_chase(PURPLE, 0.1)

        print("rainbow")
        rainbow_cycle(0)  # Increase the number to slow down the rainbow
except Exception as ex:
    logging.error("Exception occurred", exc_info=True)
except KeyboardInterrupt:
    logging.info("exit")

pixels.fill(BLACK)
#pixels.show()

