import os

# ANSI colors
COLORS = {
    'reset': '\033[0m',
    'yellow': '\033[38;2;255;255;128m',
    'purple': '\033[38;2;149;128;255m',
    'red': '\033[38;2;235;64;52m',
    'green': '\033[38;2;138;255;124m',
    'orange': '\033[38;2;255;202;117m',
    'blue': '\033[38;2;128;255;234m',
    'pink': '\033[38;2;255;128;191m',
    'gray': '\033[38;2;114;140;167m',
    'magenta': '\033[38;2;133;116;244m',
    'cyan': '\033[38;2;128;255;234m',
    'white': '\033[97m'
}

def fdir(filename):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)