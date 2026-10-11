import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils import (
    C, colorize, print_section, print_ok, print_warn,
    print_error, print_info, estimate_crack_time, strength_bar,
)

COMMON_PASSWORDS = {
    'password', '123456', '12345678', 'qwerty', 'abc123', 'monkey',
    'letmein', 'dragon', '111111', 'baseball', 'iloveyou', 'trustno1',
    'sunshine', 'master', 'welcome', 'shadow', 'ashley', 'football',
    'jesus', 'michael', 'ninja', 'mustang', 'password1', 'admin',
    'qwerty123', '1q2w3e4r', '123321', 'password123', 'superman',
    'batman', 'starwars', 'princess', 'login', 'passw0rd', 'p@ssword',
    'changeme', 'secret', 'temp123', 'test123', 'demo', 'guest',
    'letmein123', 'welcome1', 'admin123', 'root', 'toor', 'passwd',
    'qwerty12345', '123qwe', 'qwe123', '1qaz2wsx', 'zaqxsw', '000000',
    'password12', 'passw0rd1', 'qazwsx', 'abc1234', 'abcdef', 'abcdefg',
    '123456789', '1234567890', '0987654321', 'access', 'hello123',
    'charlie', 'donald', 'loveme', 'flower', 'hottie', 'solo',
    'prince', 'whatever', 'qwe12345', 'trustme', 'buster', 'soccer',
    'thomas', 'hunter', 'ranger', 'batman1', 'spiderman', 'matrix',
    'hammer', 'silver', 'phoenix', 'camaro', 'freedom', 'spirit',
    'daniel', 'robert', 'andrew', 'joshua', 'matthew', 'nicole',
    'jordan', 'amanda', 'ashley1', 'jessica', 'password!', 'pass!',
    'p@ssword1', 'qwerty1', 'letmein1', 'master12', 'admin1',
}

COMMON_WORDS = [
    'password', 'admin', 'login', 'welcome', 'master', 'shadow',
    'hello', 'world', 'access', 'secure', 'crypto', 'key', 'pass',
    'user', 'guest', 'test', 'demo', 'sample', 'changeme', 'secret',
    'qwerty', 'asdf', 'zxcv', 'passwd', 'football', 'baseball',
    'hockey', 'soccer', 'monkey', 'dragon', 'summer', 'winter',
    'spring', 'autumn', 'freedom', 'usa', 'america', 'london',
    'paris', 'letmein', 'sunshine', 'iloveyou', 'trustno1', 'starwars',
    'princess', 'batman', 'superman', 'spiderman', 'ironman', 'naruto',
    'info', 'mail', 'support', 'help', 'service', 'data', 'signin',
    'account', 'userid', 'username', 'computer', 'internet', 'network',
    'system', 'server', 'router', 'google', 'amazon', 'microsoft',
    'apple', 'linux', 'python', 'java', 'master', 'ninja', 'pirate',
    'diamond', 'crystal', 'golden', 'silver', 'midnight', 'rainbow',
    'thunder', 'lightning', 'stardust', 'moonlight', 'sunset', 'sunrise',
    'ocean', 'mountain', 'forest', 'river', 'island', 'castle', 'palace',
    'garden', 'valley', 'prince', 'princess', 'knight', 'dragon',
]

SEQUENTIAL_PATTERNS = [
    'abcdefghijklmnopqrstuvwxyz',
    '0123456789',
    'zyxwvutsrqponmlkjihgfedcba',
    '0987654321',
]

KEYBOARD_ROWS = [
    'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
    'qwertzuiop', 'azertyuiop',
    '1234567890',
]

_LEET_TRANSLATIONS = {
    '0': 'o', '2': 'z', '3': 'e', '4': 'a',
    '5': 's', '6': 'g', '7': 't', '8': 'b', '9': 'g',
    '@': 'a', '$': 's', '!': 'i', '+': 't',
    '€': 'e', '£': 'l', '¥': 'y', '§': 's',
}
LEET_MAP_ONE_AS_L = str.maketrans({**_LEET_TRANSLATIONS, '1': 'l'})
LEET_MAP_ONE_AS_I = str.maketrans({**_LEET_TRANSLATIONS, '1': 'i'})

EMAIL_PATTERN = re.compile(
    r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
)
URL_PATTERN = re.compile(
    r'https?://[^\s]+|www\.[^\s]+'
)


def _check_sequential(password: str) -> list:
    issues = []
    lower = password.lower()
    seen = set()
    for seq in SEQUENTIAL_PATTERNS:
        for length in range(3, min(7, len(seq) + 1)):
            for i in range(len(seq) - length + 1):
                chunk = seq[i:i + length]
                if chunk not in seen and chunk in lower:
                    issues.append(chunk)
                    seen.add(chunk)
    return issues


def _check_keyboard(password: str) -> list:
    issues = []
    lower = password.lower()
    seen = set()
    for row in KEYBOARD_ROWS:
        for length in range(3, min(7, len(row) + 1)):
            for i in range(len(row) - length + 1):
                chunk = row[i:i + length]
                if chunk not in seen and chunk in lower:
                    issues.append(chunk)
                    seen.add(chunk)
                rev = chunk[::-1]
                if rev not in seen and rev in lower:
                    issues.append(rev)
                    seen.add(rev)
    return issues


def _check_repeated_chars(password: str) -> list:
    issues = []
    for char in set(password):
        count = password.count(char)
        ratio = count / len(password)
        if count > 2 and ratio >= 0.25:
            issues.append((char, count))
    return issues


def _check_repeated_patterns(password: str) -> list:
    issues = []
    seen = set()
    for plen in range(2, min(7, len(password) // 2 + 1)):
        for i in range(len(password) - 2 * plen + 1):
            pattern = password[i:i + plen]
            if pattern not in seen and pattern == password[i + plen:i + 2 * plen]:
                issues.append(pattern)
                seen.add(pattern)
    return issues


def _is_common_password(password: str) -> bool:
    return password.lower() in COMMON_PASSWORDS


def _check_common_combos(password: str) -> list:
    issues = []
    lower = password.lower()
    common_base = ['password', 'admin', 'login', 'welcome', 'master',
                   'letmein', 'monkey', 'dragon', 'qwerty', 'trustno',
                   'shadow', 'sunshine', 'princess', 'football', 'baseball',
                   'iloveyou', 'batman', 'superman', 'ninja', 'mustang']
    for base in common_base:
        for year in ['2024', '2023', '2025', '2026', '2022', '2021', '2020', '2019',
                     '123', '456', '789', '000', '111', '999']:
            if base + year in lower or lower == base + year:
                issues.append(f"'{base}{year}'")
                break
    return issues


def _find_dictionary_words(password: str) -> list:
    lower = password.lower()
    found = []
    for word in sorted(COMMON_WORDS, key=len, reverse=True):
        if len(word) < 4:
            continue
        if word in lower:
            found.append(word)
            lower = lower.replace(word, '', 1)
    return found


def _detect_leetspeak(password: str) -> list:
    found = []
    variants = [
        password.lower().translate(LEET_MAP_ONE_AS_L),
        password.lower().translate(LEET_MAP_ONE_AS_I),
    ]
    for deleet in variants:
        for word in sorted(COMMON_WORDS, key=len, reverse=True):
            if len(word) < 4:
                continue
            if word in deleet:
                found.append(word)
                deleet = deleet.replace(word, '', 1)
    return list(dict.fromkeys(found))


def _check_date_patterns(password: str) -> list:
    issues = []
    patterns = [
        r'(?:19|20)\d{2}',
    ]
    for pat in patterns:
        for m in re.findall(pat, password):
            y = int(m)
            if 1950 <= y <= 2030:
                issues.append(m)
    for m in re.findall(r'\d{2}[/-]\d{2}[/-]\d{4}', password):
        issues.append(m)
    for m in re.findall(r'\d{4}[/-]\d{2}[/-]\d{2}', password):
        issues.append(m)
    return issues


def _check_email_url(password: str) -> list:
    issues = []
    if EMAIL_PATTERN.search(password):
        issues.append("contains an email address")
    if URL_PATTERN.search(password):
        issues.append("contains a URL")
    return issues


def _check_only_two_types(password: str) -> bool:
    types = 0
    if re.search(r'[a-z]', password):
        types += 1
    if re.search(r'[A-Z]', password):
        types += 1
    if re.search(r'[0-9]', password):
        types += 1
    if re.search(r'[^a-zA-Z0-9]', password):
        types += 1
    return types <= 2


def test_password(password: str) -> dict:
    if not password:
        return {
            'score': 0, 'grade': 'F', 'length': 0,
            'issues': ['No password provided.'],
            'warnings': [], 'strengths': [], 'entropy_bits': 0,
            'crack_time': 'instant',
            'has_uppercase': False, 'has_lowercase': False,
            'has_digits': False, 'has_special': False,
            'categories': 0, 'suggestions': ['Enter a password to test.'],
            'base_score': 0, 'penalty': 0,
        }

    length = len(password)
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'[0-9]', password))
    has_special = bool(re.search(r'[^a-zA-Z0-9]', password))
    categories = sum([has_lower, has_upper, has_digit, has_special])

    pool = 0
    if has_lower:
        pool += 26
    if has_upper:
        pool += 26
    if has_digit:
        pool += 10
    if has_special:
        pool += len("!@#$%^&*()-_=+[]{}|;:,.<>?")
    entropy = length * math.log2(pool) if pool > 0 else 0
    raw_entropy = round(entropy, 2)
    crack_time = estimate_crack_time(entropy)

    if length < 8:
        length_score = 0
    elif length < 10:
        length_score = 8
    elif length < 12:
        length_score = 15
    elif length < 14:
        length_score = 22
    elif length < 16:
        length_score = 28
    elif length < 18:
        length_score = 32
    elif length < 20:
        length_score = 36
    elif length < 25:
        length_score = 38
    else:
        length_score = 40

    comp_score = min(30, categories * 7.5)

    if entropy >= 120:
        entropy_score = 30
    elif entropy >= 100:
        entropy_score = 25
    elif entropy >= 80:
        entropy_score = 20
    elif entropy >= 60:
        entropy_score = 12
    elif entropy >= 40:
        entropy_score = 5
    else:
        entropy_score = 0

    base_score = length_score + comp_score + entropy_score

    issues = []
    warnings = []
    strengths = []
    penalty = 0

    if length < 8:
        issues.append(f"CRITICAL: Only {length} characters — trivially brute-forced.")
        penalty += 20
    elif length < 12:
        issues.append(f"Length {length} is below 12-char minimum for security.")
        penalty += 10
    elif length < 16:
        warnings.append(f"Length {length} is borderline. 16+ recommended.")
    else:
        strengths.append(f"Length {length} — meets 16+ recommended threshold.")

    if categories < 4:
        missing = []
        if not has_lower:
            missing.append("lowercase")
        if not has_upper:
            missing.append("uppercase")
        if not has_digit:
            missing.append("digits")
        if not has_special:
            missing.append("special chars")
        if len(missing) == 1:
            issues.append(f"Missing {missing[0]} — reduced search space.")
        elif len(missing) > 1:
            issues.append(f"Missing {', '.join(missing[:-1])} and {missing[-1]} — severely limited diversity.")
            penalty += 5
    else:
        strengths.append("Uses all 4 character types.")

    if _check_only_two_types(password) and length < 20:
        warnings.append("Only 2 character types — consider adding more diversity.")
        penalty += 3

    seq_patterns = _check_sequential(password)
    for pat in seq_patterns:
        issues.append(f"Sequential pattern: '{pat}' — easily automated.")
        penalty += 10

    kb_patterns = _check_keyboard(password)
    for pat in kb_patterns:
        issues.append(f"Keyboard walk: '{pat}' — top cracking pattern.")
        penalty += 10

    repeated = _check_repeated_chars(password)
    for char, count in repeated:
        issues.append(f"Character '{char}' appears {count}x ({count / length * 100:.0f}%) — weakens entropy.")
        penalty += 8

    rep_pats = _check_repeated_patterns(password)
    for pat in rep_pats:
        issues.append(f"Repeating pattern '{pat}' — structural weakness.")
        penalty += 10

    if _is_common_password(password):
        issues.append("IMMEDIATE FAIL: Known most-common password.")
        penalty += 50

    combos = _check_common_combos(password)
    for combo in combos:
        issues.append(f"Common password+number combo: {combo}")
        penalty += 15

    dict_words = _find_dictionary_words(password)
    for word in dict_words[:3]:
        warnings.append(f"Dictionary word '{word}' — vulnerable to dictionary attacks.")
        penalty += 6

    leet_words = _detect_leetspeak(password)
    for word in leet_words[:3]:
        warnings.append(f"Leet-speak variant of '{word}' — trivially cracked.")
        penalty += 5

    date_matches = _check_date_patterns(password)
    for dm in date_matches:
        warnings.append(f"Date/year pattern '{dm}' — commonly tried.")
        penalty += 5

    email_url = _check_email_url(password)
    for eu in email_url:
        issues.append(f"Password {eu} — never embed personal data.")
        penalty += 8

    if raw_entropy < 40:
        issues.append(f"Very low entropy ({raw_entropy} bits) — critical brute-force risk.")
    elif raw_entropy < 60:
        issues.append(f"Low entropy ({raw_entropy} bits) — weak brute-force resistance.")
    elif raw_entropy < 80:
        warnings.append(f"Moderate entropy ({raw_entropy} bits) — adequate but not strong.")
    else:
        strengths.append(f"Strong entropy ({raw_entropy} bits) — excellent resistance.")

    if length >= 20 and categories == 4:
        strengths.append("Excellent length with full character diversity.")
    if raw_entropy >= 100:
        strengths.append("Entropy exceeds 100 bits — high security.")
    if not repeated and not rep_pats:
        strengths.append("No repeated characters or patterns detected.")
    if not seq_patterns and not kb_patterns:
        strengths.append("No sequential or keyboard patterns detected.")

    final_score = max(0, min(100, base_score - penalty))

    if final_score >= 95:
        grade = 'A+'
    elif final_score >= 85:
        grade = 'A'
    elif final_score >= 75:
        grade = 'B'
    elif final_score >= 65:
        grade = 'C'
    elif final_score >= 50:
        grade = 'D'
    else:
        grade = 'F'

    suggestions = _generate_suggestions(password, issues, warnings, grade)

    return {
        'score': final_score,
        'grade': grade,
        'length': length,
        'entropy_bits': raw_entropy,
        'crack_time': crack_time,
        'has_uppercase': has_upper,
        'has_lowercase': has_lower,
        'has_digits': has_digit,
        'has_special': has_special,
        'categories': categories,
        'issues': issues,
        'warnings': warnings,
        'strengths': strengths,
        'suggestions': suggestions,
        'base_score': base_score,
        'penalty': penalty,
    }


def _generate_suggestions(password: str, issues: list, warnings: list, grade: str) -> list:
    suggestions = []

    if grade == 'F':
        suggestions.append("CRITICAL: Do NOT use this password. Generate a new one immediately.")
    elif grade == 'D':
        suggestions.append("Dangerously weak. Strongly recommend replacement.")
    elif grade == 'C':
        suggestions.append("Below acceptable security standards. Improve it.")

    if len(password) < 12:
        suggestions.append("Increase length to at least 12 characters (16+ recommended).")
    elif len(password) < 16:
        suggestions.append("Consider extending to 16+ characters.")

    suggestions.append("Use a mix of uppercase, lowercase, digits, and special characters.")

    if any('Sequential' in i or 'sequential' in i for i in issues):
        suggestions.append("Avoid sequential patterns like 'abc' or '123'.")
    if any('Keyboard' in i or 'keyboard' in i for i in issues):
        suggestions.append("Avoid keyboard-walk patterns like 'qwerty' or 'asdf'.")
    if any('Dictionary' in w or 'dictionary' in w for w in warnings):
        suggestions.append("Avoid dictionary words and common names.")
    if any('Leet' in w or 'leet' in w for w in warnings):
        suggestions.append("Leet-speak substitutions (p@ssw0rd) are easily cracked.")
    if any('repeat' in i.lower() for i in issues):
        suggestions.append("Avoid repeating characters or patterns.")
    if any('common password' in i.lower() for i in issues):
        suggestions.append("Never use known common passwords.")
    if any('email' in i.lower() or 'url' in i.lower() for i in issues):
        suggestions.append("Never embed email addresses or URLs in passwords.")
    if any('date' in w.lower() for w in warnings):
        suggestions.append("Avoid embedding dates or years.")

    if grade in ('A', 'A+'):
        suggestions.append("Strong password. Continue using good practices.")
    elif grade == 'B':
        suggestions.append("Decent but could be improved with more diversity.")

    suggestions.append("Use a unique password for every account.")

    return suggestions


def show_results(r: dict):
    grade_info = {
        'A+': ('EXCELLENT', C.GREEN),
        'A': ('STRONG', C.GREEN),
        'B': ('MODERATE', C.YELLOW),
        'C': ('WEAK', C.YELLOW),
        'D': ('VERY WEAK', C.RED),
        'F': ('CRITICAL', C.RED),
    }

    label, grade_color = grade_info.get(r['grade'], ('UNKNOWN', C.WHITE))

    print()
    print(colorize("=" * 58, C.CYAN))
    print(colorize("          PASSWORD STRENGTH ANALYSIS", C.BOLD + C.WHITE))
    print(colorize("=" * 58, C.CYAN))
    print()

    grade_display = colorize(f"  {r['grade']}", C.BOLD + grade_color)
    label_display = colorize(label, grade_color)
    print(f"  Grade:    {grade_display}  {label_display}")
    print(f"  Score:    {colorize(str(r['score']) + '/100', C.WHITE)}")
    entropy_text = f"{r['entropy_bits']} bits"
    print(f"  Entropy:  {colorize(entropy_text, C.WHITE)}")
    crack_color = C.YELLOW if 'year' not in r['crack_time'] and 'universe' not in r['crack_time'] else C.GREEN
    print(f"  Crack:    {colorize(r['crack_time'], crack_color)}")
    print(f"  Strength: {strength_bar(r['score'])}")
    print()

    print(colorize("  " + "-" * 52, C.DIM))
    print(f"  Length:     {colorize(str(r['length']), C.WHITE)} characters")

    cats = []
    cats.append(colorize("Upper", C.GREEN) if r['has_uppercase'] else colorize("no upper", C.RED))
    cats.append(colorize("Lower", C.GREEN) if r['has_lowercase'] else colorize("no lower", C.RED))
    cats.append(colorize("Digit", C.GREEN) if r['has_digits'] else colorize("no digit", C.RED))
    cats.append(colorize("Special", C.GREEN) if r['has_special'] else colorize("no special", C.RED))
    print(f"  Char sets:  {', '.join(cats)} ({r['categories']}/4)")
    penalty_text = f"-{r['penalty']}"
    print(f"  Base score: {r['base_score']}  |  Penalties: {colorize(penalty_text, C.RED)}  |  Final: {r['score']}")
    print(colorize("  " + "-" * 52, C.DIM))

    if r['issues']:
        print()
        n_issues = len(r['issues'])
        print(f"  {colorize(f'ISSUES ({n_issues})', C.RED + C.BOLD)}:")
        for issue in r['issues']:
            print(f"    {colorize('-', C.RED)} {issue}")

    if r['warnings']:
        print()
        n_warnings = len(r['warnings'])
        print(f"  {colorize(f'WARNINGS ({n_warnings})', C.YELLOW + C.BOLD)}:")
        for warn in r['warnings']:
            print(f"    {colorize('*', C.YELLOW)} {warn}")

    if r['strengths']:
        print()
        n_strengths = len(r['strengths'])
        print(f"  {colorize(f'STRENGTHS ({n_strengths})', C.GREEN + C.BOLD)}:")
        for s in r['strengths']:
            print(f"    {colorize('+', C.GREEN)} {s}")

    if r['suggestions']:
        print()
        print(f"  {colorize('RECOMMENDATIONS:', C.CYAN + C.BOLD)}:")
        for s in r['suggestions'][:5]:
            print(f"    {colorize('->', C.CYAN)} {s}")

    print()
    print(colorize("=" * 58, C.CYAN))


def show_diff(old: str, new: str):
    if old == new:
        print_info("No changes made.")
        return

    print()
    print_info("CHANGES MADE:")
    print(f"  Old ({len(old)} chars): {colorize(old, C.RED)}")
    print(f"  New ({len(new)} chars): {colorize(new, C.GREEN)}")

    added = len(new) - len(old)
    if added > 0:
        print(f"  {colorize(f'+{added} chars added', C.GREEN)}")
    elif added < 0:
        print(f"  {colorize(f'{abs(added)} chars removed', C.RED)}")

    changes = sum(1 for a, b in zip(old, new) if a != b)
    changes += abs(len(old) - len(new))
    if changes > 0:
        print(f"  {changes} position(s) changed.")


def run(last_password: str = None):
    pw = None
    was_modified = False

    print_section("PASSWORD TESTER", C.CYAN + C.BOLD)
    print(colorize("  Rigorous cybersecurity analysis", C.DIM))
    print()

    if last_password:
        use = input(f"  Use last generated password? {colorize('(y/n)', C.DIM)}: ").strip().lower()
        if use == 'y':
            pw = last_password
            print_info(f"Using: {pw}")

    if pw is None:
        pw = input(f"  Enter password to test: ").strip()
        while not pw:
            print_error("Password cannot be empty.")
            pw = input(f"  Enter password to test: ").strip()

    results = test_password(pw)
    show_results(results)

    if results['grade'] not in ('A+', 'A'):
        fix = input(f"\n  Improve this password? {colorize('(y/n)', C.DIM)}: ").strip().lower()
        if fix == 'y':
            was_modified = True
            new_pw = input("  Enter new password: ").strip()
            while not new_pw:
                print_error("Password cannot be empty.")
                new_pw = input("  Enter new password: ").strip()
            show_diff(pw, new_pw)
            pw = new_pw
            results = test_password(pw)
            show_results(results)

    input(f"\n  {colorize('Press Enter to return...', C.DIM)}")
    return pw, was_modified


if __name__ == '__main__':
    run()
