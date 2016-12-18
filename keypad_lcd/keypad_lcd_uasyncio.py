"""
Keypad_LCD module/class for MicroPython, using uasyncio module.
===========================================================

Notes
-----

    * Two uasync coroutines are created.
        1. Keypad.scan_coro -- scans keypad rows/columns and pushes key events to a queue.
        2. keypad_watcher -- watches the keypad for key events on the queue.

    * To run type:
        >>> import keypad_lcd_uasyncio as k
        >>> k.run()

    * Need to have the following modules installed (via upip or manually)
        - micropython-uasyncio
        - micropython-uasyncio.queues
        - micropython-uasyncio.core ???
        - micropython-collections

Testing
-------

    * Tested on an Olimex E407 board (STM32F407 micro-controller)
    https://www.olimex.com/Products/ARM/ST/STM32-E407

    * with 16-key (4x4 matrix) membrane keypad, similar to this (bought on eBay).
    https://www.youtube.com/watch?v=wRse5uqvPZs

To Do
-----

    * Unit tests :-/
    * Video the keypad_lcd working :)

"""

##============================================================================

import micropython

import uasyncio as asyncio

## could probably create Keypad and LCD instances in hwconfig file ??

from keypad_uasyncio import Keypad_uasyncio

# try:
#     from machine import I2C
# except ImportErrror:
#     from pyb import I2C
#from machine import I2C
from pyb import I2C

from pyb_i2c_lcd import I2cLcd

##============================================================================

async def keypad_lcd_task(lcd, keypad):
    """A task to monitor a queue of key events and process them."""

    str = "\n".join( [ "+------------------+",
                       "keypad_lcd_uasyncio ",
                       "   Please wait ...  ",
                       "+------------------+",
                       ] )
    lcd.putstr(str)
    await asyncio.sleep_ms(2000)
    lcd.clear()
    lcd.putstr("Press a key ...\n> ")

    while True:
        key = await keypad.get_key()
        #key = await keypad.queue.get()
        print("keypad_watcher: got key:", key)
        lcd.putchar(key)

##============================================================================

def main_test():
    """Main test function."""

    print("main_test(): start")

    micropython.alloc_emergency_exception_buf(100)

    ## Create the LCD instance.
    i2c = I2C(1, I2C.MASTER)
    lcd = I2cLcd(i2c, 0x27, 4, 20)

    ## Create the keypad instance.
    keypad = Keypad_uasyncio(queue_size=4, start=True)

    ## Get a handle to the asyncio event loop.
    loop = asyncio.get_event_loop()

    ## Add the keypad scanning and keypad watcher coroutines.
    loop.create_task(keypad.scan_coro())
    loop.create_task(keypad_lcd_task(lcd=lcd, keypad=keypad))

    ## Start running the coroutines
    loop.run_forever()

    print("main_test(): end")

##============================================================================

run = main_test

if __name__ == '__main__':
    main_test()
