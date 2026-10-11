import base64
import math
import os
import sys
from pathlib import Path

PASSWORDS_FILE = Path(__file__).resolve().parent.parent / 'Password-Files' / 'Passwords.txt'


class C:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


def _enable_windows_vt() -> bool:
    if os.name != 'nt':
        return True
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        return bool(kernel32.SetConsoleMode(
            handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING))
    except Exception:
        return False


def _detect_color() -> bool:
    if os.environ.get('NO_COLOR'):
        return False
    if not sys.stdout.isatty():
        return False
    return _enable_windows_vt()


_COLOR_ENABLED = _detect_color()


def set_color_enabled(value: bool):
    global _COLOR_ENABLED
    _COLOR_ENABLED = bool(value)


def color_enabled() -> bool:
    return _COLOR_ENABLED


def colorize(text: str, color: str) -> str:
    if not _COLOR_ENABLED:
        return text
    return f"{color}{text}{C.RESET}"


def bold(text: str) -> str:
    if not _COLOR_ENABLED:
        return text
    return f"{C.BOLD}{text}{C.RESET}"


def dim(text: str) -> str:
    if not _COLOR_ENABLED:
        return text
    return f"{C.DIM}{text}{C.RESET}"


def clear_screen():
    if not sys.stdout.isatty():
        return
    os.system('cls' if os.name == 'nt' else 'clear')


def strength_bar(score: int, width: int = 20) -> str:
    filled = int(width * score / 100)
    empty = width - filled
    if score >= 85:
        color = C.GREEN
    elif score >= 65:
        color = C.YELLOW
    else:
        color = C.RED
    if _COLOR_ENABLED:
        bar = f"{color}{'█' * filled}{C.DIM}{'░' * empty}{C.RESET}"
    else:
        bar = f"{'█' * filled}{'░' * empty}"
    return f"[{bar}] {score}%"


def estimate_crack_time(entropy_bits: float) -> str:
    if entropy_bits <= 0:
        return "instant"
    guesses_per_sec = 10_000_000_000
    log2_seconds = entropy_bits - math.log2(guesses_per_sec) - 1
    if log2_seconds < 0:
        seconds = 2 ** log2_seconds
        return f"{seconds:.1f} seconds"
    elif log2_seconds < math.log2(60):
        return f"{2 ** log2_seconds:.0f} seconds"
    elif log2_seconds < math.log2(3600):
        minutes = 2 ** (log2_seconds - math.log2(60))
        return f"{minutes:.0f} minutes"
    elif log2_seconds < math.log2(86400):
        hours = 2 ** (log2_seconds - math.log2(3600))
        return f"{hours:.0f} hours"
    elif log2_seconds < math.log2(31536000):
        days = 2 ** (log2_seconds - math.log2(86400))
        return f"{days:.0f} days"
    elif log2_seconds < math.log2(31536000 * 1000):
        years = 2 ** (log2_seconds - math.log2(31536000))
        return f"{years:.0f} years"
    elif log2_seconds < math.log2(31536000 * 1_000_000):
        thousands = 2 ** (log2_seconds - math.log2(31536000 * 1000))
        return f"{thousands:.0f} thousand years"
    elif log2_seconds < math.log2(31536000 * 1_000_000_000):
        millions = 2 ** (log2_seconds - math.log2(31536000 * 1_000_000))
        return f"{millions:.0f} million years"
    elif log2_seconds < math.log2(31536000 * 1_000_000_000_000):
        billions = 2 ** (log2_seconds - math.log2(31536000 * 1_000_000_000))
        return f"{billions:.0f} billion years"
    else:
        return "heat death of the universe"


def encode_password(password: str) -> str:
    return base64.b64encode(password.encode('utf-8')).decode('utf-8')


def decode_password(encoded: str) -> str:
    return base64.b64decode(encoded.encode('utf-8')).decode('utf-8')


def save_password(password: str):
    PASSWORDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PASSWORDS_FILE, 'a', encoding='utf-8') as f:
        f.write(encode_password(password) + '\n')


def load_passwords() -> list:
    if not PASSWORDS_FILE.exists():
        return []
    with open(PASSWORDS_FILE, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content:
        return []
    result = []
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            result.append(decode_password(line))
        except Exception:
            result.append(line)
    return result


def save_passwords(passwords: list):
    PASSWORDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = PASSWORDS_FILE.with_suffix('.tmp')
    with open(tmp, 'w', encoding='utf-8') as f:
        for pw in passwords:
            f.write(encode_password(pw) + '\n')
    os.replace(tmp, PASSWORDS_FILE)


def print_header():
    clear_screen()
    print()
    print(colorize("=" * 60, C.CYAN))
    print(colorize("              NeN-PASSWORD MANAGER", C.BOLD + C.WHITE))
    print(colorize("         Cybersecurity-grade password tool", C.DIM))
    print(colorize("=" * 60, C.CYAN))
    print()


def print_section(title: str, color: str = C.CYAN):
    print()
    print(colorize(f"  {title}", color))
    print(colorize("  " + "-" * 48, C.DIM))


def print_ok(msg: str):
    print(colorize(f"  [+] {msg}", C.GREEN))


def print_warn(msg: str):
    print(colorize(f"  [*] {msg}", C.YELLOW))


def print_error(msg: str):
    print(colorize(f"  [!] {msg}", C.RED))


def print_info(msg: str):
    print(colorize(f"  [i] {msg}", C.BLUE))
