class Colors:
    RESET = "\033[0m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    DEFAULT = "\033[39m"
    NONE = ""


if __name__ == "__main__":
    for c in dir(Colors):
        if c[0: 1] != "_" and c != "RESET":
            print(getattr(Colors, c) + c + Colors.RESET)
