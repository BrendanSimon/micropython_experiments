"""
Keypad module/class for MicroPython, using uasyncio module.
===========================================================

Notes
-----

    * Two uasync coroutines are created.
        1. Keypad.scan_coro -- scans keypad rows/columns and pushes key events to a queue.
        2. keypad_watcher -- watches the keypad for key events on the queue.

    * To run type:
        >>> import keypad_uasyncio as k
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

    * Pass the key and pin info to the class via function parameters.
    * Refactor into a common base class.
    * Unit tests :)
    * Video the keypad working.

"""

##============================================================================

import micropython

try:
    from hwconfig import Pin
except ImportError:
    from pyb import Pin

import uasyncio as asyncio
from uasyncio.queues import Queue

##============================================================================

class Keypad_uasyncio():
    """Class to scan a Keypad matrix (e.g. 16-keys as 4x4 matrix) and report
       key presses.
    """

    ## Key states
    KEY_UP      = 0
    KEY_DOWN    = 1

    #-------------------------------------------------------------------------

    def __init__(self, queue_size=0, start=False):
        self.init(queue_size=queue_size, start=start)

    #-------------------------------------------------------------------------

    def init(self, queue_size=0, start=False):
        """Initialise/Reinitialise the instance."""

        ## Create the queue to push key events to.
        self.queue = Queue(maxsize=queue_size)

        keys = [
                '1', '2', '3', 'A',
                '4', '5', '6', 'B',
                '7', '8', '9', 'C',
                '*', '0', '#', 'D',
               ]

        ## Initialise all keys to the UP state.
        self.keys = [ { 'char' : key, 'state' : self.KEY_UP } for key in keys ]

        ## Pin names for rows and columns.
        self.rows = [ 'PD1', 'PD3', 'PD5', 'PD7' ]
        self.cols = [ 'PD9', 'PD11', 'PD13', 'PD15' ]

        ## Initialise row pins as outputs.
        self.row_pins = [ Pin(pin_name, mode=Pin.OUT) for pin_name in self.rows ]

        ## Initialise column pins as inputs.
        self.col_pins = [ Pin(pin_name, mode=Pin.IN, pull=Pin.PULL_DOWN) for pin_name in self.cols ]

        self.row_scan_delay_ms = 40 // len(self.rows)

        self.running = start

    #-------------------------------------------------------------------------

    def start(self):
        """Start keypad scanning."""

        self.running = True

    #-------------------------------------------------------------------------

    def stop(self):
        """Stop the timer."""

        self.running = False

    #-------------------------------------------------------------------------

    def get_key(self):
        """Get last key pressed."""

        key = self.queue.get()
        return key

    #-------------------------------------------------------------------------

    def key_process(self, key_code, col_pin):
        """Process a key press or release."""

        key_event = None

        if col_pin.value():
            if self.keys[key_code]['state'] == self.KEY_UP:
                key_event = self.KEY_DOWN
                self.keys[key_code]['state'] = key_event
        else:
            if self.keys[key_code]['state'] == self.KEY_DOWN:
                key_event = self.KEY_UP
                self.keys[key_code]['state'] = key_event

        return key_event

    #-------------------------------------------------------------------------

    async def scan_coro(self):
        """A coroutine to scan each row and check column for key events."""

        while self.running:
            key_code = 0
            for row, row_pin in enumerate(self.row_pins):
                ## Assert row.
                row_pin.value(1)

                ## Delay between processing each row.
                await asyncio.sleep_ms(self.row_scan_delay_ms)

                ## Check for key events for each column of current row.
                for col, col_pin in enumerate(self.col_pins):
                    ## Process pin state.
                    key_event = self.key_process(key_code=key_code, col_pin=col_pin)
                    ## Process key event.
                    if key_event == self.KEY_DOWN:
                        key_char = self.keys[key_code]['char']
                        await self.queue.put(key_char)

                    key_code += 1

                ## Deassert row.
                row_pin.value(0)

##============================================================================

async def keypad_watcher(keypad):
    """A task to monitor a queue of key events and process them."""

    while True:
        key = await keypad.get_key()
        #key = await keypad.queue.get()
        print("keypad_watcher: got key:", key)

##============================================================================

def main_test():
    """Main test function."""

    print("main_test(): start")

    micropython.alloc_emergency_exception_buf(100)

    keypad = Keypad_uasyncio(queue_size=4, start=True)

    loop = asyncio.get_event_loop()
    loop.create_task(keypad.scan_coro())
    loop.create_task(keypad_watcher(keypad=keypad))
    loop.run_forever()

    print("main_test(): end")


##============================================================================

run = main_test

if __name__ == '__main__':
    main_test()
