"""ANSI escape codes for the terminals that support it."""

COLOR_RESET = "\x1B[0m"
COLOR_HIGHLIGHT = "\x1B[38;5;%dm\x1B[48;5;%dm" % (223, 58)
COLOR_ERROR = "\x1B[38;5;%dm\x1B[48;5;%dm" % (196, 52)
COLOR_PROMPT = "\x1B[38;5;%dm\x1B[48;5;%dm" % (194, 64)
