import sys
import threading
import datetime
import time

import serial

from colors import Colors


class SerialBridge(threading.Thread):
    def __init__(self, ser_from, ser_to, chunk=128):
        super().__init__()
        self.ser_from = ser_from
        self.ser_to = ser_to
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
            dat = self.ser_from.read(self.chunk)
            if dat:
                if self.dump:
                    self.show_dump(dat)
                self.ser_to.write(dat)

    def show_dump(self, dat):
        ts = datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]

        dump = ""
        for i in range(0, len(dat), 16):
            h = ' '.join('{:02X}'.format(c) for c in dat[i:i + 16])
            a = ''.join('{}'.format(0x20 <= c <= 0x7e and chr(c) or '.') for c in dat[i:i + 16])
            dump += f"\n  {i:08X}  {h:<47s}  |{a}|"

        print(f"{self.prefix}[{ts}] {self.name} {len(dat)} bytes{dump}{self.postfix}")


if __name__ == '__main__':
    COM1 = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    COM2 = sys.argv[2] if len(sys.argv) > 2 else "COM4"
    SPEED1 = sys.argv[3] if len(sys.argv) > 3 else "38400"
    SPEED2 = sys.argv[4] if len(sys.argv) > 4 else SPEED1
    DUMP = True

    ser1 = serial.Serial(COM1, SPEED1, timeout=0.1)
    ser2 = serial.Serial(COM2, SPEED2, timeout=0.1)

    bridge1 = SerialBridge(ser1, ser2)
    bridge1.set_dump(DUMP, COM1 + " -> " + COM2, Colors.GREEN, Colors.RESET)
    bridge1.start()
    bridge2 = SerialBridge(ser2, ser1)
    bridge2.set_dump(DUMP, COM1 + " <- " + COM2, Colors.RED, Colors.RESET)
    bridge2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    bridge1.stop()
    bridge1.join()
    bridge2.stop()
    bridge2.join()
