import os
import time
from PIL import Image
import numpy as np

import board
import digitalio

class GC9A01:
    def __init__(self, spi, cs, dc, rst=None):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        
        self.cs.direction = digitalio.Direction.OUTPUT
        self.dc.direction = digitalio.Direction.OUTPUT
        self.cs.value = True
        
        if self.rst:
            self.rst.direction = digitalio.Direction.OUTPUT
            self.rst.value = True
            time.sleep(0.1)
            self.rst.value = False
            time.sleep(0.1)
            self.rst.value = True
            time.sleep(0.1)

        self.init_display()

    def command(self, cmd, data=None):
        while not self.spi.try_lock():
            pass
        self.cs.value = False
        self.dc.value = False
        self.spi.write(bytearray([cmd]))
        if data:
            self.dc.value = True
            self.spi.write(data)
        self.cs.value = True
        self.spi.unlock()

    def init_display(self):
        # Standard GC9A01 initialization sequence
        self.command(0xEF)
        self.command(0xEB, b'\x14')
        self.command(0xFE)
        self.command(0xEF)
        self.command(0xEB, b'\x14')
        self.command(0x84, b'\x40')
        self.command(0x85, b'\xFF')
        self.command(0x86, b'\xFF')
        self.command(0x87, b'\xFF')
        self.command(0x88, b'\x0A')
        self.command(0x89, b'\x21')
        self.command(0x8A, b'\x00')
        self.command(0x8B, b'\x80')
        self.command(0x8C, b'\x01')
        self.command(0x8D, b'\x01')
        self.command(0x8E, b'\xFF')
        self.command(0x8F, b'\xFF')
        self.command(0xB6, b'\x00\x20')
        self.command(0x36, b'\x08') # MADCTL
        self.command(0x3A, b'\x05') # COLMOD 16bit
        self.command(0x90, b'\x08\x08\x08\x08')
        self.command(0xBD, b'\x06')
        self.command(0xBC, b'\x00')
        self.command(0xFF, b'\x60\x01\x04')
        self.command(0xC3, b'\x13')
        self.command(0xC4, b'\x13')
        self.command(0xC9, b'\x22')
        self.command(0xBE, b'\x11')
        self.command(0xE1, b'\x10\x0E')
        self.command(0xDF, b'\x21\x0c\x02')
        self.command(0xF0, b'\x45\x09\x08\x08\x26\x2A')
        self.command(0xF1, b'\x43\x70\x72\x36\x37\x6F')
        self.command(0xF2, b'\x45\x09\x08\x08\x26\x2A')
        self.command(0xF3, b'\x43\x70\x72\x36\x37\x6F')
        self.command(0xED, b'\x1B\x0B')
        self.command(0xAE, b'\x77')
        self.command(0xCD, b'\x63')
        self.command(0x70, b'\x07\x07\x04\x0E\x0F\x09\x07\x08\x03')
        self.command(0xE8, b'\x34')
        self.command(0x62, b'\x18\x0D\x71\xED\x70\x70\x18\x0F\x71\xEF\x70\x70')
        self.command(0x63, b'\x18\x11\x71\xF1\x70\x70\x18\x13\x71\xF3\x70\x70')
        self.command(0x64, b'\x28\x29\xF1\x01\xF1\x00\x07')
        self.command(0x66, b'\x3C\x00\xCD\x67\x45\x45\x10\x00\x00\x00')
        self.command(0x67, b'\x00\x3C\x00\x00\x00\x01\x54\x10\x32\x98')
        self.command(0x74, b'\x10\x85\x80\x00\x00\x4E\x00')
        self.command(0x98, b'\x3e\x07')
        self.command(0x35, b'\x00')
        self.command(0x21) # INVOFF / INVON
        self.command(0x11) # Sleep out
        time.sleep(0.12)
        self.command(0x29) # Display ON
        time.sleep(0.02)

    def draw_image(self, img_pil):
        # Convert PIL image to RGB565 bytes
        img_array = np.array(img_pil).astype(np.uint16)
        r = (img_array[:,:,0] >> 3) << 11
        g = (img_array[:,:,1] >> 2) << 5
        b = (img_array[:,:,2] >> 3)
        rgb565 = r | g | b
        # Swap bytes for SPI endianness
        rgb565 = ((rgb565 & 0xFF) << 8) | (rgb565 >> 8)
        pixels = rgb565.tobytes()

        # Set address window
        self.command(0x2A, b'\x00\x00\x00\xEF') # 0 to 239
        self.command(0x2B, b'\x00\x00\x00\xEF') # 0 to 239
        self.command(0x2C, pixels)

def main():
    cs1_pin = digitalio.DigitalInOut(board.D17)
    cs2_pin = digitalio.DigitalInOut(board.D27)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = digitalio.DigitalInOut(board.D24)

    spi = board.SPI()
    while not spi.try_lock():
        pass
    spi.configure(baudrate=64000000)
    spi.unlock()

    display_left = GC9A01(spi, cs=cs1_pin, dc=dc_pin, rst=reset_pin)
    display_right = GC9A01(spi, cs=cs2_pin, dc=dc_pin, rst=reset_pin)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    swirl_path = os.path.join(base_dir, "assets", "swirl.png")

    if not os.path.exists(swirl_path):
        print("Error: Missing swirl.png in assets folder.")
        return

    # Load image and resize to display
    img = Image.open(swirl_path).convert("RGB")
    img = img.resize((240, 240))

    # Push to both displays
    display_left.draw_image(img)
    display_right.draw_image(img)
    
    print("Boot splash image pushed.")

if __name__ == "__main__":
    main()
