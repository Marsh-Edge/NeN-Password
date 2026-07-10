import math
import secrets
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils import (
    C, colorize, bold, dim, print_section, print_ok, print_warn, print_error,
    print_info, estimate_crack_time, save_password, strength_bar,
)

PASSPHRASE_WORDS = [
    "alpha", "amber", "arctic", "atlas", "azure", "badge", "bamboo", "basin",
    "beacon", "birch", "blade", "blaze", "bloom", "bolt", "bone", "brave",
    "brick", "brook", "canyon", "cedar", "charm", "chase", "cipher", "claim",
    "cliff", "cloud", "coral", "crest", "crystal", "cumin", "dagger", "dawn",
    "delta", "diadem", "eagle", "ember", "ember", "falcon", "fawn", "flame",
    "flint", "forge", "frost", "garnet", "glacier", "gleam", "granite", "grove",
    "hawk", "haven", "helix", "heron", "hydra", "ivory", "jade", "jungle",
    "keystone", "knight", "lance", "lark", "lemon", "linen", "lotus", "lunar",
    "lynx", "maple", "marble", "marsh", "mason", "melon", "mirage", "moss",
    "nectar", "noble", "north", "ocean", "olive", "onyx", "orbit", "osprey",
    "pearl", "phoenix", "plume", "polar", "prism", "prose", "quartz", "quest",
    "raven", "ridge", "river", "rocky", "rover", "ruby", "sage", "salmon",
    "scout", "shade", "shadow", "sheriff", "silva", "silver", "slope", "solar",
    "sonic", "spark", "spear", "spice", "spine", "spring", "stag", "stone",
    "storm", "sugar", "summit", "swift", "talon", "tiger", "timber", "titan",
    "torch", "tower", "transit", "tribal", "trout", "tsunami", "tulip", "ultra",
    "unity", "valor", "vault", "venom", "vigor", "viper", "vivid", "vortex",
    "waltz", "warden", "wheat", "whirl", "whisper", "wild", "wings", "winter",
    "wolfe", "xenon", "yacht", "yield", "young", "youth", "zenith", "zephyr",
    "zinc", "zone", "nimbus", "fable", "pixel", "raven", "steel", "brisk",
    "cobra", "creek", "dune", "fern", "glyph", "helix", "iron", "jade",
    "karma", "luna", "mage", "noble", "orbit", "prism", "rune", "sage",
    "torque", "vex", "wisp", "yarn",
]

SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?"
AMBIGUOUS_CHARS = "il1Lo0O"


def generate_random(length: int, use_lower: bool = True, use_upper: bool = True,
                    use_digits: bool = True, use_special: bool = True,
                    exclude_ambiguous: bool = False) -> str:
    if length < 8:
        raise ValueError("Length must be at least 8.")

    charsets = {}
    if use_lower:
        chars = string.ascii_lowercase
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in AMBIGUOUS_CHARS)
        if chars:
            charsets['lowercase'] = chars
    if use_upper:
        chars = string.ascii_uppercase
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in AMBIGUOUS_CHARS)
        if chars:
            charsets['uppercase'] = chars
    if use_digits:
        chars = string.digits
        if exclude_ambiguous:
            chars = ''.join(c for c in chars if c not in AMBIGUOUS_CHARS)
        if chars:
            charsets['digits'] = chars
    if use_special:
        charsets['special'] = SPECIAL_CHARS

    if not charsets:
        raise ValueError("At least one character set must be selected.")

    pool = ''.join(charsets.values())
    guaranteed = [secrets.choice(cs) for cs in charsets.values()]
    remaining = [secrets.choice(pool) for _ in range(length - len(guaranteed))]
    result = guaranteed + remaining
    secrets.SystemRandom().shuffle(result)
    return ''.join(result)


def generate_passphrase(word_count: int = 4, separator: str = "-",
                        capitalize: bool = True, add_number: bool = True,
                        add_special: bool = False) -> str:
    if word_count < 3:
        raise ValueError("Word count must be at least 3.")

    words = [secrets.choice(PASSPHRASE_WORDS) for _ in range(word_count)]

    if capitalize:
        words = [w.capitalize() for w in words]

    result = separator.join(words)

    if add_number:
        num = str(secrets.randbelow(900) + 100)
        result += separator + num

    if add_special:
        sp = secrets.choice("!@#$%^&*")
        result += sp

    return result


def generate_pin(length: int = 6) -> str:
    if length < 4:
        raise ValueError("PIN length must be at least 4.")
    if length > 12:
        raise ValueError("PIN length must be at most 12.")
    return ''.join(secrets.choice(string.digits) for _ in range(length))


def calc_pool_size(use_lower: bool, use_upper: bool, use_digits: bool,
                   use_special: bool, exclude_ambiguous: bool = False) -> int:
    pool = 0
    if use_lower:
        base = string.ascii_lowercase
        if exclude_ambiguous:
            base = ''.join(c for c in base if c not in AMBIGUOUS_CHARS)
        pool += len(base)
    if use_upper:
        base = string.ascii_uppercase
        if exclude_ambiguous:
            base = ''.join(c for c in base if c not in AMBIGUOUS_CHARS)
        pool += len(base)
    if use_digits:
        base = string.digits
        if exclude_ambiguous:
            base = ''.join(c for c in base if c not in AMBIGUOUS_CHARS)
        pool += len(base)
    if use_special:
        pool += len(SPECIAL_CHARS)
    return pool


def _show_result(password: str, pool_info: str = "", entropy_bits: float = 0):
    length = len(password)
    if entropy_bits == 0 and pool_info:
        try:
            pool_size = int(pool_info.split(":")[1].strip().split()[0])
            entropy_bits = length * math.log2(pool_size) if pool_size > 0 else 0
        except (IndexError, ValueError):
            pass

    crack_time = estimate_crack_time(entropy_bits)

    print()
    print(colorize("=" * 56, C.CYAN))
    print(colorize("           GENERATED PASSWORD", C.BOLD + C.WHITE))
    print(colorize("=" * 56, C.CYAN))
    print()
    print(f"  {colorize(password, C.BOLD + C.GREEN)}")
    print()
    print(colorize("-" * 56, C.DIM))
    print(f"  Length:        {colorize(str(length), C.WHITE)} characters")
    if pool_info:
        print(f"  {pool_info}")
    print(f"  Entropy:       {colorize(f'{entropy_bits:.1f} bits', C.WHITE)}")
    print(f"  Crack time:    {colorize(crack_time, C.YELLOW if 'year' not in crack_time and 'universe' not in crack_time else C.GREEN)}")
    print(f"  Strength:      {strength_bar(min(100, int(entropy_bits / 1.5)))}")
    print(colorize("=" * 56, C.CYAN))


def run():
    print_section("PASSWORD GENERATOR", C.CYAN + C.BOLD)
    print(colorize("  Cryptographically secure generation (PEP 506)", C.DIM))
    print(colorize("  Three modes: Random, Passphrase, PIN", C.DIM))
    print()

    print(f"  {colorize('[1]', C.BOLD + C.WHITE)} Random Password")
    print(f"  {colorize('[2]', C.BOLD + C.WHITE)} Passphrase (memorable)")
    print(f"  {colorize('[3]', C.BOLD + C.WHITE)} PIN (numeric)")
    print()

    mode = input(f"  Select mode {colorize('(1-3)', C.DIM)}: ").strip()

    password = ""

    if mode == '1':
        password = _run_random_mode()
    elif mode == '2':
        password = _run_passphrase_mode()
    elif mode == '3':
        password = _run_pin_mode()
    else:
        print_error("Invalid option. Defaulting to Random mode.")
        password = _run_random_mode()

    if not password:
        return None

    print()
    save_choice = input(f"  Save to vault? {colorize('(y/n)', C.DIM)}: ").strip().lower()
    if save_choice == 'y':
        save_password(password)
        print_ok("Password saved to vault (base64 obfuscated).")

    input(f"\n  {colorize('Press Enter to return...', C.DIM)}")
    return password


def _run_random_mode() -> str:
    print_section("RANDOM PASSWORD", C.CYAN)

    while True:
        try:
            raw = input(f"  Desired length {colorize('(8-128)', C.DIM)}: ").strip()
            length = int(raw)
            if length < 8:
                print_warn("Minimum length is 8 characters.")
                continue
            if length > 128:
                print_warn("Maximum length is 128 characters.")
                continue
            break
        except ValueError:
            print_error("Enter a valid number.")
            continue

    print()
    print_info("Character sets (all enabled by default):")
    print(f"    {colorize('[1]', C.WHITE)} Lowercase letters  (a-z)")
    print(f"    {colorize('[2]', C.WHITE)} Uppercase letters  (A-Z)")
    print(f"    {colorize('[3]', C.WHITE)} Digits             (0-9)")
    print(f"    {colorize('[4]', C.WHITE)} Special characters (!@#$...)")
    print()

    choices = input(f"  Disable any? Enter numbers {colorize('(comma-separated)', C.DIM)}, or Enter for all: ").strip()
    disabled = set(c.strip() for c in choices.split(',') if c.strip())

    use_lower = '1' not in disabled
    use_upper = '2' not in disabled
    use_digits = '3' not in disabled
    use_special = '4' not in disabled

    if not any([use_lower, use_upper, use_digits, use_special]):
        print_warn("All sets disabled. Enabling all.")
        use_lower = use_upper = use_digits = use_special = True

    disabled_names = []
    if not use_lower:
        disabled_names.append("lowercase")
    if not use_upper:
        disabled_names.append("uppercase")
    if not use_digits:
        disabled_names.append("digits")
    if not use_special:
        disabled_names.append("special")
    if disabled_names:
        print_warn(f"Disabling {', '.join(disabled_names)} reduces entropy.")

    print()
    excl = input(f"  Exclude ambiguous characters (0/O, 1/l/I)? {colorize('(y/n)', C.DIM)}: ").strip().lower()
    exclude_ambiguous = excl == 'y'

    password = generate_random(length, use_lower, use_upper, use_digits, use_special, exclude_ambiguous)

    pool_size = 0
    if use_lower:
        cs = string.ascii_lowercase
        if exclude_ambiguous:
            cs = ''.join(c for c in cs if c not in AMBIGUOUS_CHARS)
        pool_size += len(cs)
    if use_upper:
        cs = string.ascii_uppercase
        if exclude_ambiguous:
            cs = ''.join(c for c in cs if c not in AMBIGUOUS_CHARS)
        pool_size += len(cs)
    if use_digits:
        cs = string.digits
        if exclude_ambiguous:
            cs = ''.join(c for c in cs if c not in AMBIGUOUS_CHARS)
        pool_size += len(cs)
    if use_special:
        pool_size += len(SPECIAL_CHARS)

    entropy = length * math.log2(pool_size) if pool_size > 0 else 0
    pool_info = f"  Pool size:      {colorize(str(pool_size), C.WHITE)} characters"
    _show_result(password, pool_info, entropy)
    return password


def _run_passphrase_mode() -> str:
    print_section("PASSPHRASE GENERATOR", C.CYAN)
    print_info("Generates memorable word-based passwords (Diceware-style)")
    print()

    while True:
        try:
            raw = input(f"  Number of words {colorize('(3-8)', C.DIM)}: ").strip()
            word_count = int(raw)
            if word_count < 3:
                print_warn("Minimum 3 words.")
                continue
            if word_count > 8:
                print_warn("Maximum 8 words.")
                continue
            break
        except ValueError:
            print_error("Enter a valid number.")
            continue

    print()
    print_info("Separator style:")
    print(f"    {colorize('[1]', C.WHITE)} hyphen     (word-word-word)")
    print(f"    {colorize('[2]', C.WHITE)} dot        (word.word.word)")
    print(f"    {colorize('[3]', C.WHITE)} underscore (word_word_word)")
    print(f"    {colorize('[4]', C.WHITE)} space      (word word word)")
    print()

    sep_choice = input(f"  Select separator {colorize('(1-4)', C.DIM)}: ").strip()
    separators = {'1': '-', '2': '.', '3': '_', '4': ' '}
    separator = separators.get(sep_choice, '-')

    cap = input(f"  Capitalize words? {colorize('(y/n, default: y)', C.DIM)}: ").strip().lower()
    capitalize = cap != 'n'

    num = input(f"  Append a number? {colorize('(y/n, default: y)', C.DIM)}: ").strip().lower()
    add_number = num != 'n'

    sp = input(f"  Append a special char? {colorize('(y/n, default: n)', C.DIM)}: ").strip().lower()
    add_special = sp == 'y'

    password = generate_passphrase(word_count, separator, capitalize, add_number, add_special)

    pool_size = len(PASSPHRASE_WORDS)
    entropy = word_count * math.log2(pool_size)
    if add_number:
        entropy += math.log2(900)
    if add_special:
        entropy += math.log2(len("!@#$%^&*"))

    pool_info = f"  Word pool:      {colorize(str(pool_size), C.WHITE)} words"
    _show_result(password, pool_info, entropy)
    return password


def _run_pin_mode() -> str:
    print_section("PIN GENERATOR", C.CYAN)
    print_info("Generates numeric PIN codes")
    print()

    while True:
        try:
            raw = input(f"  PIN length {colorize('(4-12, default: 6)', C.DIM)}: ").strip()
            if not raw:
                length = 6
                break
            length = int(raw)
            if length < 4:
                print_warn("Minimum 4 digits.")
                continue
            if length > 12:
                print_warn("Maximum 12 digits.")
                continue
            break
        except ValueError:
            print_error("Enter a valid number.")
            continue

    password = generate_pin(length)

    entropy = length * math.log2(10)
    pool_info = f"  Pool size:      {colorize('10', C.WHITE)} digits (0-9)"
    _show_result(password, pool_info, entropy)
    return password


if __name__ == '__main__':
    run()
