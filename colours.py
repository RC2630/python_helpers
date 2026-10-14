from typing import Final, Any

ANSI_NORMAL: Final[str] = "\033[0m"

ANSI_BLACK: Final[str] = "\033[30m"
ANSI_RED: Final[str] = "\033[31m"
ANSI_GREEN: Final[str] = "\033[32m"
ANSI_YELLOW: Final[str] = "\033[33m"
ANSI_BLUE: Final[str] = "\033[34m"
ANSI_MAGENTA: Final[str] = "\033[35m"
ANSI_CYAN: Final[str] = "\033[36m"
ANSI_WHITE: Final[str] = "\033[37m"

def black(s: Any) -> str: return ANSI_BLACK + str(s) + ANSI_NORMAL
def red(s: Any) -> str: return ANSI_RED + str(s) + ANSI_NORMAL
def green(s: Any) -> str: return ANSI_GREEN + str(s) + ANSI_NORMAL
def yellow(s: Any) -> str: return ANSI_YELLOW + str(s) + ANSI_NORMAL
def blue(s: Any) -> str: return ANSI_BLUE + str(s) + ANSI_NORMAL
def magenta(s: Any) -> str: return ANSI_MAGENTA + str(s) + ANSI_NORMAL
def cyan(s: Any) -> str: return ANSI_CYAN + str(s) + ANSI_NORMAL
def white(s: Any) -> str: return ANSI_WHITE + str(s) + ANSI_NORMAL

ANSI_BACKGROUND_BLACK: Final[str] = "\033[40m"
ANSI_BACKGROUND_RED: Final[str] = "\033[41m"
ANSI_BACKGROUND_GREEN: Final[str] = "\033[42m"
ANSI_BACKGROUND_YELLOW: Final[str] = "\033[43m"
ANSI_BACKGROUND_BLUE: Final[str] = "\033[44m"
ANSI_BACKGROUND_MAGENTA: Final[str] = "\033[45m"
ANSI_BACKGROUND_CYAN: Final[str] = "\033[46m"
ANSI_BACKGROUND_WHITE: Final[str] = "\033[47m"

def bg_black(s: Any) -> str: return ANSI_BACKGROUND_BLACK + str(s) + ANSI_NORMAL
def bg_red(s: Any) -> str: return ANSI_BACKGROUND_RED + str(s) + ANSI_NORMAL
def bg_green(s: Any) -> str: return ANSI_BACKGROUND_GREEN + str(s) + ANSI_NORMAL
def bg_yellow(s: Any) -> str: return ANSI_BACKGROUND_YELLOW + str(s) + ANSI_NORMAL
def bg_blue(s: Any) -> str: return ANSI_BACKGROUND_BLUE + str(s) + ANSI_NORMAL
def bg_magenta(s: Any) -> str: return ANSI_BACKGROUND_MAGENTA + str(s) + ANSI_NORMAL
def bg_cyan(s: Any) -> str: return ANSI_BACKGROUND_CYAN + str(s) + ANSI_NORMAL
def bg_white(s: Any) -> str: return ANSI_BACKGROUND_WHITE + str(s) + ANSI_NORMAL

ANSI_UNDERLINE: Final[str] = "\033[4m"
ANSI_BOLD: Final[str] = "\033[1m"
ANSI_ITALIC: Final[str] = "\033[3m"
ANSI_INVERSE: Final[str] = "\033[7m"
ANSI_STRIKETHROUGH: Final[str] = "\033[9m"

def underline(s: Any) -> str: return ANSI_UNDERLINE + str(s) + ANSI_NORMAL
def bold(s: Any) -> str: return ANSI_BOLD + str(s) + ANSI_NORMAL
def italic(s: Any) -> str: return ANSI_ITALIC + str(s) + ANSI_NORMAL
def inverse(s: Any) -> str: return ANSI_INVERSE + str(s) + ANSI_NORMAL
def strikethrough(s: Any) -> str: return ANSI_STRIKETHROUGH + str(s) + ANSI_NORMAL