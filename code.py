import board
import busio
# import time
import digitalio
import neopixel
import usb_midi
import adafruit_midi

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
from lcd.lcd import CursorMode

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=2, num_cols=16)

ledCount = 60
midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1])
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
pixels = neopixel.NeoPixel(board.A1, ledCount, auto_write=False, brightness=1)

# white + primary, and secondary colors repeated
palette = [[255, 0, 0],
           [0, 255, 0],
           [0, 0, 255],
           [255, 255, 0],
           [255, 0, 255],
           [0, 255, 255],
           [255, 0, 0],
           [0, 255, 0],
           [0, 0, 255],
           [255, 255, 0],
           [255, 0, 255],
           [0, 255, 255],
           [255, 0, 0],
           [0, 255, 0],
           [0, 0, 255]]

# white + primary, and secondary colors repeated
palette1 = [[255, 255, 255],
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 255, 0],
            [255, 0, 255],
            [0, 255, 255],
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 255, 0],
            [255, 0, 255],
            [0, 255, 255],
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255]]

# major scale notes
palette2 = [[255, 255, 255],
            [255, 0, 0],
            [255, 255, 255],
            [255, 0, 0],
            [255, 255, 255],
            [255, 255, 255],
            [255, 0, 0],
            [255, 255, 255],
            [255, 0, 0],
            [255, 255, 255],
            [255, 0, 0],
            [255, 255, 255]]

noteNames = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

clock_count = 0
beat_count = 0


def gamma_adjusted(r, g, b):
    gamma_table = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                   1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4,
                   4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8,
                   8, 8, 9, 9, 9, 10, 10, 10, 11, 11, 12, 12, 12, 13, 13, 14,
                   14, 15, 15, 15, 16, 16, 17, 17, 18, 18, 19, 19, 20, 20, 21, 22,
                   22, 23, 23, 24, 25, 25, 26, 26, 27, 28, 28, 29, 30, 30, 31, 32,
                   33, 33, 34, 35, 36, 36, 37, 38, 39, 40, 40, 41, 42, 43, 44, 45,
                   46, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                   61, 62, 63, 64, 65, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 78,
                   80, 81, 82, 83, 85, 86, 87, 89, 90, 91, 93, 94, 95, 97, 98, 99,
                   101, 102, 104, 105, 107, 108, 110, 111, 113, 114, 116, 117, 119, 121, 122, 124,
                   125, 127, 129, 130, 132, 134, 135, 137, 139, 141, 142, 144, 146, 148, 150, 151,
                   153, 155, 157, 159, 161, 163, 165, 166, 168, 170, 172, 174, 176, 178, 180, 182,
                   184, 186, 189, 191, 193, 195, 197, 199, 201, 204, 206, 208, 210, 212, 215, 217,
                   219, 221, 224, 226, 228, 231, 233, 235, 238, 240, 243, 245, 248, 250, 253, 255)
    return gamma_table[r], gamma_table[g], gamma_table[b]


def note_position(note):
    # center around middle C (note 60)
    offset = int((ledCount / 2) - 60)
    position = note + offset

    # truncate ends
    last_index = ledCount - 1
    if position < 0:
        position = 0
    elif position > last_index:
        position = last_index

    # reverse direction
    position = last_index - position
    return position


def note_color_velocity(note, velocity, channel):
    if velocity == 0:
        r = 0
        g = 0
        b = 0
    else:
        r = int(255 * msg.velocity / 127)
        g = 255 - r
        b = 0
    return gamma_adjusted(r, g, b)


def note_color_channel(note, velocity, channel):
    if velocity == 0:
        r = 0
        g = 0
        b = 0
    else:
        brightness = msg.velocity / 127
        r = int(palette[channel][0] * brightness)
        g = int(palette[channel][1] * brightness)
        b = int(palette[channel][2] * brightness)
    return gamma_adjusted(r, g, b)


def note_color_notes(note, velocity, channel):
    if velocity == 0:  # pseudo noteOff
        r = 0
        g = 0
        b = 0
    else:
        brightness = msg.velocity / 127
        note_number = note % 12
        r = int(palette[note_number][0] * brightness)
        g = int(palette[note_number][1] * brightness)
        b = int(palette[note_number][2] * brightness)
    return gamma_adjusted(r, g, b)


while True:
    msg = midi.receive()
    if msg is not None:
        if isinstance(msg, NoteOn):
            # flash the board led
            if msg.velocity == 0:
                led.value = False
            else:
                led.value = True
            color = note_color_notes(msg.note, msg.velocity, msg.channel)
            pixels[note_position(msg.note)] = (color[0], color[1], color[2])
            pixels.show()
            # lcd.clear()
            # lcd.print(str(msg.note) + ", " + noteNames[msg.note % 12])

        if isinstance(msg, NoteOff):
            led.value = False
            pixels[note_position(msg.note)] = (0, 0, 0)
            pixels.show()
