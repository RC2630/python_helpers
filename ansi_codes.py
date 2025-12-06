from typing import Final

ANSI_NORMAL: Final[str] = "\033[0m"

ANSI_BLACK: Final[str] = "\033[30m"
ANSI_RED: Final[str] = "\033[31m"
ANSI_GREEN: Final[str] = "\033[32m"
ANSI_YELLOW: Final[str] = "\033[33m"
ANSI_BLUE: Final[str] = "\033[34m"
ANSI_MAGENTA: Final[str] = "\033[35m"
ANSI_CYAN: Final[str] = "\033[36m"
ANSI_WHITE: Final[str] = "\033[37m"

def black(s: str) -> str: return ANSI_BLACK + s + ANSI_NORMAL
def red(s: str) -> str: return ANSI_RED + s + ANSI_NORMAL
def green(s: str) -> str: return ANSI_GREEN + s + ANSI_NORMAL
def yellow(s: str) -> str: return ANSI_YELLOW + s + ANSI_NORMAL
def blue(s: str) -> str: return ANSI_BLUE + s + ANSI_NORMAL
def magenta(s: str) -> str: return ANSI_MAGENTA + s + ANSI_NORMAL
def cyan(s: str) -> str: return ANSI_CYAN + s + ANSI_NORMAL
def white(s: str) -> str: return ANSI_WHITE + s + ANSI_NORMAL

ANSI_BACKGROUND_BLACK: Final[str] = "\033[40m"
ANSI_BACKGROUND_RED: Final[str] = "\033[41m"
ANSI_BACKGROUND_GREEN: Final[str] = "\033[42m"
ANSI_BACKGROUND_YELLOW: Final[str] = "\033[43m"
ANSI_BACKGROUND_BLUE: Final[str] = "\033[44m"
ANSI_BACKGROUND_MAGENTA: Final[str] = "\033[45m"
ANSI_BACKGROUND_CYAN: Final[str] = "\033[46m"
ANSI_BACKGROUND_WHITE: Final[str] = "\033[47m"

def bg_black(s: str) -> str: return ANSI_BACKGROUND_BLACK + s + ANSI_NORMAL
def bg_red(s: str) -> str: return ANSI_BACKGROUND_RED + s + ANSI_NORMAL
def bg_green(s: str) -> str: return ANSI_BACKGROUND_GREEN + s + ANSI_NORMAL
def bg_yellow(s: str) -> str: return ANSI_BACKGROUND_YELLOW + s + ANSI_NORMAL
def bg_blue(s: str) -> str: return ANSI_BACKGROUND_BLUE + s + ANSI_NORMAL
def bg_magenta(s: str) -> str: return ANSI_BACKGROUND_MAGENTA + s + ANSI_NORMAL
def bg_cyan(s: str) -> str: return ANSI_BACKGROUND_CYAN + s + ANSI_NORMAL
def bg_white(s: str) -> str: return ANSI_BACKGROUND_WHITE + s + ANSI_NORMAL

ANSI_UNDERLINE: Final[str] = "\033[4m"
ANSI_BOLD: Final[str] = "\033[1m"
ANSI_ITALIC: Final[str] = "\033[3m"
ANSI_INVERSE: Final[str] = "\033[7m"
ANSI_STRIKETHROUGH: Final[str] = "\033[9m"

def underline(s: str) -> str: return ANSI_UNDERLINE + s + ANSI_NORMAL
def bold(s: str) -> str: return ANSI_BOLD + s + ANSI_NORMAL
def italic(s: str) -> str: return ANSI_ITALIC + s + ANSI_NORMAL
def inverse(s: str) -> str: return ANSI_INVERSE + s + ANSI_NORMAL
def strikethrough(s: str) -> str: return ANSI_STRIKETHROUGH + s + ANSI_NORMAL