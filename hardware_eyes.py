import time
import math
import random
import os
from PIL import Image

import board
import digitalio
import adafruit_rgb_display.gc9a01 as gc9a01

# Configuration for CS and DC pins
# Left Eye
cs1_pin = digitalio.DigitalInOut(board.CE0)
# Right Eye
cs2_pin = digitalio.DigitalInOut(board.CE1)
# Shared DC & Reset
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)

# Setup SPI bus
spi = board.SPI()

# Initialize displays
# Note: BAUD rate can be adjusted for better framerate if needed
display_left = gc9a01.GC9A01(spi, cs=cs1_pin, dc=dc_pin, rst=reset_pin, baudrate=64000000)
display_right = gc9a01.GC9A01(spi, cs=cs2_pin, dc=dc_pin, rst=reset_pin, baudrate=64000000)

WIDTH = 240
HEIGHT = 240
DISPLAY_SIZE = 240
MAX_OFFSET = 60

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sclera_path = os.path.join(base_dir, "assets", "sclera.png")
    iris_path = os.path.join(base_dir, "assets", "iris.png")

    if not os.path.exists(sclera_path) or not os.path.exists(iris_path):
        print("Error: Missing image assets in the 'assets' folder.")
        return

    # Load images
    sclera_img = Image.open(sclera_path).convert("RGB")
    iris_img = Image.open(iris_path).convert("RGBA")

    sclera_img = sclera_img.resize((DISPLAY_SIZE, DISPLAY_SIZE))
    iris_img = iris_img.resize((100, 100))
    iris_radius = 50

    target_x, target_y = 0, 0
    current_x, current_y = 0, 0
    last_move = time.time()
    move_interval = random.uniform(0.5, 2.0)

    print("Running dual GC9A01 eyes. Press Ctrl+C to stop.")

    while True:
        now = time.time()
        if now - last_move > move_interval:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, MAX_OFFSET)
            target_x = math.cos(angle) * distance
            target_y = math.sin(angle) * distance
            last_move = now
            move_interval = random.uniform(0.5, 2.0)

        # Interpolate eye movement for smoothness
        current_x += (target_x - current_x) * 0.2
        current_y += (target_y - current_y) * 0.2

        # Create a fresh frame from sclera
        frame = sclera_img.copy()

        # Calculate iris position
        paste_x = int((DISPLAY_SIZE / 2) - iris_radius + current_x)
        paste_y = int((DISPLAY_SIZE / 2) - iris_radius + current_y)

        # Paste iris with alpha transparency mask
        frame.paste(iris_img, (paste_x, paste_y), mask=iris_img)

        # To improve framerate, we send the same frame to both displays since they look identical
        display_left.image(frame)
        display_right.image(frame)

if __name__ == "__main__":
    main()
