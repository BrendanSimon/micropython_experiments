"""
LED array example using asyncio.

This example continually fades a LED on and off, and switches to a
quicker flash for a small period when a button is pressed.

The LED and BUTTON objects are imported from the board/hardware config module.
You need to copy the config file for your board to a suitable location.

Tested on the Olimex E407 board, with a 4x5 keypad and 8 LED array.
http://www.ebay.com/sch/sis.html?_nkw=4x4+keyboard+buttons+Keypad+matrix+LED+Marquee+Independent+keyboard+Smart+car&_trksid=p2047675.m4100
See `examples/hwapi/hwconfig_OLIMEX_E407.py` for an example config module
"""


from hwconfig import LED, BUTTON
from machine import Pin, Signal

import uasyncio


#
# LEDs on Keypad/LED board connection to PE connector.
#
LED_0 = Signal(Pin("E15", Pin.OUT), inverted=True)
LED_1 = Signal(Pin("E14", Pin.OUT), inverted=True)
LED_2 = Signal(Pin("E13", Pin.OUT), inverted=True)
LED_3 = Signal(Pin("E12", Pin.OUT), inverted=True)
LED_4 = Signal(Pin("E11", Pin.OUT), inverted=True)
LED_5 = Signal(Pin("E10", Pin.OUT), inverted=True)
LED_6 = Signal(Pin("E9", Pin.OUT), inverted=True)
LED_7 = Signal(Pin("E8", Pin.OUT), inverted=True)

#
# List of LEDs.
#
LEDS = [ LED_0, LED_1, LED_2, LED_3, LED_4, LED_5, LED_6, LED_7 ]


async def cycle_leds(cycle_count, delay):
    """A task to fade the LED on and off."""

    on_idx = cycle_count & 7
    on_led = LEDS[on_idx]

    # Turn all LEDs off.
    for led in LEDS:
        led.off()

    # Turn next LED on.
    on_led.on()

    await uasyncio.sleep_ms(delay)


async def flash_leds(delay):
    """A task to flash the LEDs."""

    # Turn all LEDs on.
    for led in LEDS:
        led.on()

    await uasyncio.sleep_ms(delay)

    # Turn all LEDs off.
    for led in LEDS:
        led.off()

    await uasyncio.sleep_ms(delay)


async def update_leds():
    """A task to flash or fade the LED depending global count variable."""

    global flash_count
    flash_count = 0

    delay = 100
    cycle_count = 0
    cycle_dir = 1

    while True:
        if flash_count > 0:
            await flash_leds(delay)
            flash_count -= 1
        else:
            await cycle_leds(cycle_count, delay)
            cycle_count += cycle_dir
            if cycle_count > 7:
                cycle_count = 6
                cycle_dir = -1
            elif cycle_count < 0:
                cycle_count = 1
                cycle_dir = 1


async def check_button():
    """A task to continually check if button is pressed and set a global count variable."""

    global flash_count

    while True:
        await uasyncio.sleep_ms(100)
        if BUTTON.value():
            flash_count = 10


def main():
    loop = uasyncio.get_event_loop()
    loop.create_task(check_button())
    loop.create_task(update_leds())
    loop.run_forever()


if __name__ == '__main__':
    main()
