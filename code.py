import board
import busio
import digitalio
import neopixel
import usb_midi
import adafruit_midi
import rotaryio
from lib import palettes

from lib.gamma import gamma_adjusted

from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop
from adafruit_midi.midi_continue import Continue
from adafruit_midi.timing_clock import TimingClock

from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface

print("starting midiflasher")
i2c = busio.I2C(sda=board.GP0, scl=board.GP1)
lcd = LCD(I2CPCF8574Interface(i2c, 0x27), num_rows=2, num_cols=16)

led_count = 60
midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], midi_out=usb_midi.ports[1])
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
pixels = neopixel.NeoPixel(board.A1, led_count, auto_write=True, brightness=1)
encoder = rotaryio.IncrementalEncoder(board.GP10, board.GP11)
btn = digitalio.DigitalInOut(board.GP9)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP
button_previous = btn.value

note_names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
metronome_knob_modes = ("color", "brightness", "position")
metronome_knob_index = 0
metronome_knob_mode = metronome_knob_modes[metronome_knob_index]
clock_count = 0
beat_count = 0
# encoder_previous_position = None
clock_offset = int((led_count / 2) - 12)  # 24 steps offset from center
clock_current_pixel = 0
clock_previous_pixel = 0
clock_flag = False
metronome_palette = palettes.palette_6
metronome_palette_position = 0
metronome_brightness = 128

lcd.clear()
# lcd.print("midi flasher")


def note_position(note):
    # center around middle C (note 60)
    offset = int((led_count / 2) - 60)
    index = note + offset

    # truncate ends
    last_index = led_count - 1
    if index < 0:
        index = 0
    elif index > last_index:
        index = last_index

    # reverse direction
    index = last_index - index
    return index


def note_color_velocity(note, velocity, channel):
    if velocity == 0:
        r = 0
        g = 0
        b = 0
    else:
        r = int(255 * velocity / 127)
        g = 255 - r
        b = 0
    return gamma_adjusted((r, g, b))


def note_color_channel(note, velocity, channel):
    if velocity == 0:
        r = 0
        g = 0
        b = 0
    else:
        brightness = velocity / 127
        r = int(palettes.palette_16[channel][0] * brightness)
        g = int(palettes.palette_16[channel][1] * brightness)
        b = int(palettes.palette_16[channel][2] * brightness)
    return gamma_adjusted((r, g, b))


def note_color_notes(note, velocity, channel):
    if velocity == 0:  # pseudo noteOff
        r = 0
        g = 0
        b = 0
    else:
        brightness = velocity / 127
        note_number = note % 12
        r = int(palettes.palette_12[note_number][0] * brightness)
        g = int(palettes.palette_12[note_number][1] * brightness)
        b = int(palettes.palette_12[note_number][2] * brightness)
    return gamma_adjusted((r, g, b))


knob_current_position = encoder.position
knob_previous_position = knob_current_position

lcd.print("Color: " + str(metronome_palette_position))

while True:
    # read the button and set the mode
    button_current = btn.value
    if button_current != button_previous:
        if not button_current:
            print("BTN is down")
            metronome_knob_index += 1
            if metronome_knob_index >= len(metronome_knob_modes):
                metronome_knob_index = 0
            metronome_knob_mode = metronome_knob_modes[metronome_knob_index]
            lcd.clear()
            # lcd.print(metronome_knob_mode)
            if metronome_knob_mode == "color":
                lcd.print("Color: " + str(metronome_palette_position))
            elif metronome_knob_mode == "brightness":
                lcd.print("Brightness: " + str(metronome_brightness))
            elif metronome_knob_mode == "position":
                lcd.print("Position: " + str(clock_offset))

        else:
            # lcd.clear()
            # lcd.print("BTN is up")
            print("BTN is up")

    button_previous = button_current

    # read the knob and change a value according to the mode
    knob_current_position = encoder.position
    if knob_current_position != knob_previous_position:
        # lcd.home()
        # lcd.clear()
        # set the metronome color
        if metronome_knob_mode == "color":
            if knob_current_position > knob_previous_position:
                metronome_palette_position += 1
                if metronome_palette_position >= len(metronome_palette):
                    metronome_palette_position = 0
            elif knob_current_position < knob_previous_position:
                metronome_palette_position -= 1
                if metronome_palette_position < 0:
                    metronome_palette_position = len(metronome_palette) - 1
            lcd.set_cursor_pos(0, 7)
            lcd.print(str(metronome_palette_position))
            # print(metronome_palette_position)
        elif metronome_knob_mode == "brightness":
            if knob_current_position > knob_previous_position:
                metronome_brightness += 4
                if metronome_brightness >= 255:
                    metronome_brightness = 255
            elif knob_current_position < knob_previous_position:
                metronome_brightness -= 4
                if metronome_brightness < 0:
                    metronome_brightness = 0
            lcd.set_cursor_pos(0, 12)
            lcd.print(str(metronome_brightness) + "  ")
            # print(metronome_brightness)
        elif metronome_knob_mode == "position":
            if knob_current_position > knob_previous_position:
                clock_offset -= 1
                if clock_offset < 0:
                    clock_offset = 0
            elif knob_current_position < knob_previous_position:
                clock_offset += 1
                if clock_offset + 24 >= led_count:
                    clock_offset = led_count - 24
            lcd.set_cursor_pos(0, 10)
            lcd.print(str(clock_offset) + " ")

        knob_previous_position = knob_current_position

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
            # lcd.clear()
            # lcd.print(str(msg.note) + ", " + noteNames[msg.note % 12])
        elif isinstance(msg, NoteOff):
            led.value = False
            pixels[note_position(msg.note)] = (0, 0, 0)
        elif isinstance(msg, Start):
            clock_flag = True
            clock_count = 1
            beat_count = 1
            clock_current_pixel = clock_offset
            pixels[clock_current_pixel] = (255, 255, 255)
            clock_previous_pixel = clock_current_pixel
        elif isinstance(msg, Stop):
            clock_count = 0
            beat_count = 0
            pixels[clock_current_pixel] = (0, 0, 0)
            clock_flag = False
        elif isinstance(msg, Continue):
            clock_flag = True
        elif isinstance(msg, TimingClock):
            pixels[clock_previous_pixel] = (0, 0, 0)
            odd = True  # used to reverse direction every other beat
            if (beat_count % 2) == 0:
                odd = False
            if clock_flag:  # make sure a start or continue event was received
                # first clock cycle - increment beat counter and flash a light
                if clock_count == 0:
                    # increment  the beat counter
                    beat_count += 1
                    if odd:
                        clock_current_pixel = 23
                    else:
                        clock_current_pixel = 0
                    clock_current_pixel += clock_offset
                    pixels[clock_current_pixel] = (255, 255, 255)
                else:
                    # other clock cycle - move the dot and use alternate color
                    if odd:
                        clock_current_pixel = clock_count
                    else:
                        clock_current_pixel = 24 - clock_count
                    clock_current_pixel += clock_offset
                    brightness = metronome_brightness / 255
                    pixels[clock_current_pixel] = gamma_adjusted(
                        tuple([int(c * brightness) for c in metronome_palette[metronome_palette_position]])
                    )
                clock_previous_pixel = clock_current_pixel

                # increment clock counter and reset it on the beat
                clock_count += 1
                if clock_count == 24:
                    clock_count = 0
