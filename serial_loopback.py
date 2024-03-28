import threading
import datetime
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

    def set_dump(self, enable, name='', prefix='', postfix=''):
        self.dump = enable
        self.name = name
        self.prefix = prefix
        self.postfix = postfix

    def run(self):
        while True:
            dat = self.ser.read(self.chunk)
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
    COM = "COM3"
    SPEED = 115200
    TIMEOUT = 0.1

    ser = serial.Serial(COM, SPEED, timeout=TIMEOUT)

    loopback = SerialLoopback(ser)
    loopback.set_dump(True, f'{COM} received')
    loopback.start()
