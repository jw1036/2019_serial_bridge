import serial
import datetime
import threading


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

    def set_dump(self, enable, name='', prefix='', postfix=''):
        self.dump = enable
        self.name = name
        self.prefix = prefix
        self.postfix = postfix

    def run(self):
        while True:
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
    COM1 = "COM8"
    COM2 = "COM7"
    SPEED1 = 38400
    SPEED2 = 38400
    TIMEOUT = 0.1

    ser1 = serial.Serial(COM1, SPEED1, timeout=TIMEOUT)
    ser2 = serial.Serial(COM2, SPEED2, timeout=TIMEOUT)

    sb1 = SerialBridge(ser1, ser2)
    sb1.set_dump(True, COM1 + " -> " + COM2, "\x1b[31m", "\x1b[0m")
    sb1.start()
    sb2 = SerialBridge(ser2, ser1)
    sb2.set_dump(True, COM1 + " <- " + COM2, "\x1b[34m", "\x1b[0m")
    sb2.start()

