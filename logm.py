import os
import time

from colors import Colors


def get_color(s):
    if s.startswith("[I"):
        return Colors.GREEN
    elif s.startswith("[E"):
        return Colors.RED
    elif s.startswith("[F"):
        return Colors.RED
    elif s.startswith("[V"):
        return Colors.CYAN
    elif s.startswith("  "):
        return Colors.NONE
    elif s.startswith("["):
        return Colors.YELLOW
    elif s.startswith(">"):
        return Colors.MAGENTA
    return Colors.RESET


def monitor_file(filename, encoding="cp949", start_pos=0):
    with open(filename, "r", encoding=encoding) as f:
        while True:
            try:
                line = f.readline()
                if line:
                    color = get_color(line[start_pos:])
                    print(f"{color}{line}", end="")
                else:
                    time.sleep(.1)
            except UnicodeDecodeError as e:
                print(e)


if __name__ == '__main__':
    monitor_file(
        filename=os.path.join("C:\\Users\\S9_User\\Desktop", "session.log"),
        encoding="utf-8",
        start_pos=len("[00:00:00.000]"),
    )
