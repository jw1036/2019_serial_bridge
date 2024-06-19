import os
import re
import sys
import threading
import datetime
import time

import serial


class SerialLoopback(threading.Thread):
    def __init__(self, ser, chunk=128):
        super().__init__()
        self.ser = ser
        self.chunk = chunk
        self.dump = False
        self.name = ''
        self.prefix = ''
        self.postfix = ''
        self.stop_event = threading.Event()

    def set_dump(self, enable, name='', prefix='', postfix=''):
        self.dump = enable
        self.name = name
        self.prefix = prefix
        self.postfix = postfix

    def stop(self):
        self.stop_event.set()

    def run(self):
        while not self.stop_event.isSet():
            dat = self.ser.read(self.chunk)
            if dat and dat[:1] == b"\n":
                dat = dat + self.ser.read(self.chunk)
                while True:
                    mo = re.search(br"\n(\w+):(\d+)\n", dat)
                    if not mo:
                        break

                    print(mo.string)

                    if mo.group(1) == b"set_speed":
                        self.ser.baudrate = mo.group(2)
                    elif mo.group(1) == b"send_chunk":
                        chunk = bytearray(int(mo.group(2)))
                        for i in range(len(chunk)):
                            chunk[i] = i % 256
                        self.ser.write(chunk)

                    dat = dat.replace(mo.string, b"", 1)

            if dat:
                if self.dump:
                    self.show_dump(dat)
                self.ser.write(dat)

    def show_dump(self, dat):
        ts = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

        dump = ""
        for i in range(0, len(dat), 16):
            h = ' '.join('{:02X}'.format(c) for c in dat[i:i + 16])
            a = ''.join('{}'.format(0x20 <= c <= 0x7e and chr(c) or '.') for c in dat[i:i + 16])
            dump += f"\n  {i:08X}  {h:<47s}  |{a}|"

        print(f"{self.prefix}[{ts}] {self.name} {len(dat)} bytes{dump}{self.postfix}")


if __name__ == '__main__':
    COM = sys.argv[1] if len(sys.argv) > 1 else "COM4"
    SPEED = sys.argv[2] if len(sys.argv) > 2 else "115200"
    DUMP = sys.argv[3] if len(sys.argv) > 3 else False

    ser = serial.Serial(COM, SPEED, timeout=0.1)

    loopback = SerialLoopback(ser)
    loopback.set_dump(DUMP, f'{COM} received')

    try:
        loopback.run()
    except KeyboardInterrupt:
        pass
