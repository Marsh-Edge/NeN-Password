# NeN-Password

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.14-blue.svg)
![Tests](https://img.shields.io/badge/tests-117%20passing-brightgreen.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

A cybersecurity-grade password manager and strength analyzer built entirely with the Python standard library. Generate secure passwords, test their resilience against real-world attack patterns, and manage your vault -- all from the terminal.

---

## About

Weak passwords are the number one attack vector in credential breaches. Most password generators produce random strings with no feedback on actual security, and most password checkers only verify length and character variety.

NeN-Password solves both problems in one tool:

- **Generate** passwords using three distinct modes backed by cryptographically secure randomness
- **Analyze** passwords against 12+ real-world cybersecurity checks (sequential patterns, keyboard walks, dictionary words, leet-speak variants, common combos, and more)
- **Manage** a local vault with base64-obfuscated storage

Zero dependencies. Zero network calls. Runs entirely offline with Python's `secrets` module (PEP 506).

---

## Features

| Feature | Description |
|---|---|
| **Random Generation** | Cryptographically secure random passwords with configurable character sets and ambiguous character exclusion |
| **Passphrase Generation** | Diceware-style memorable passphrases from a 180-word curated dictionary with separator and number options |
| **PIN Generation** | Numeric PIN codes from 4 to 12 digits |
| **Strength Analysis** | 100-point scoring system with letter grades (A+ through F) |
| **Time-to-Crack Estimate** | Estimates brute-force time at 10 billion guesses/second |
| **Visual Strength Bar** | Color-coded progress bar showing password strength percentage |
| **Cybersecurity Checks** | 12+ attack pattern detectors including sequential, keyboard, dictionary, leet-speak, and date patterns |
| **Common Combo Detection** | Catches `password2024`, `admin123`, and similar predictable combinations |
| **Email/URL Detection** | Flags passwords containing email addresses or URLs |
| **Password Vault** | View, search, delete, and manage saved passwords with obfuscated storage |
| **Color UI** | ANSI color-coded terminal interface with clear visual hierarchy |
| **Session Logging** | Tracks all actions during a session with timestamped summary on exit |
| **Zero Dependencies** | Uses only the Python standard library -- no pip install required |

---

## Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.14 |
| Randomness | `secrets` module (PEP 506) |
| Storage | Base64 obfuscation via `base64` |
| Testing | pytest 8.4+ |
| Dependencies | None (stdlib only) |

---

## Project Structure

```
NeN-Password/
|
|-- app.py                  # Main entry point and menu loop
|-- app/
|   |-- __init__.py
|   |-- utils.py            # Shared utilities: colors, crack time, storage
|
|-- Generate/
|   |-- __init__.py
|   |-- generate.py         # 3-mode password generator
|
|-- Testing/
|   |-- __init__.py
|   |-- test.py             # Password strength analyzer (12+ checks)
|
|-- Manage/
|   |-- __init__.py
|   |-- management.py       # Vault: view, search, delete
|
|-- tests/
|   |-- __init__.py
|   |-- test_core.py        # 108 automated tests
|
|-- Password-Files/
|   |-- Passwords.txt       # Vault storage (base64 obfuscated)
|
|-- pytest.ini              # pytest configuration
|-- conftest.py             # pytest collection rules
|-- LICENSE                 # MIT License
|-- README.md
```

---

## Installation

NeN-Password requires only Python 3.14+ and has no external dependencies.

```bash
# Clone the repository
git clone https://github.com/Marsh-Edge/NeN-Password.git

# Navigate into the project
cd NeN-Password

# Run the application
python app.py
```

That's it. No virtual environment, no `pip install`, no configuration files.

---

## Usage

### Main Menu

When you launch the application, you'll see the main menu:

```
  [1]  Generate Password
  [2]  Test Password
  [3]  Password Vault
  [4]  Exit
```

### 1. Generate Password

Choose from three generation modes:

**Random Password** -- Standard secure random generation:

```
Select mode (1-3): 1
Desired length (8-128): 20
Disable any? Enter numbers (comma-separated), or Enter for all:
Exclude ambiguous characters (0/O, 1/l/I)? (y/n): n

  GENERATED PASSWORD
  kR8$mP2nQz!vR9wLbY4#

  Length:        20 characters
  Pool size:     95 characters
  Entropy:       131.6 bits
  Crack time:    billion years
```

**Passphrase** -- Memorable word-based passwords:

```
Select mode (1-3): 2
Number of words (3-8): 4
Separator style: [1] hyphen
Capitalize words? (y/n): y
Append a number? (y/n): y

  Crystal-Dawn-Spice-526
```

**PIN** -- Numeric codes:

```
Select mode (1-3): 3
PIN length (4-12, default: 6): 8

  72940183
```

### 2. Test Password

Enter any password for comprehensive security analysis:

```
Enter password to test: MyP@ssw0rd!

  Grade:    A   STRONG
  Score:    82/100
  Entropy:  72.5 bits
  Crack:    years
  Strength: [████████████░░░░░░░░] 82%

  ISSUES (1):
    - Leet-speak variant of 'password' detected

  STRENGTHS (4):
    + Length 11 meets recommended threshold
    + Uses all 4 character types
    + Strong entropy (72.5 bits)
    + No sequential or keyboard patterns detected

  RECOMMENDATIONS:
    -> Leet-speak substitutions (p@ssw0rd) are easily cracked
    -> Consider extending to 16+ characters
    -> Use a unique password for every account
```

### 3. Password Vault

Manage saved passwords:

```
  [1] View all passwords
  [2] Search passwords
  [3] Delete a password
  [4] Clear entire vault
```

Passwords are displayed masked by default (`kR8$m****wLbY4#`) and can be revealed on demand.

---

## Security Analysis

The password tester performs 12+ cybersecurity checks based on real-world attack patterns:

| Check | What It Detects | Penalty |
|---|---|---|
| **Sequential Patterns** | `abc`, `123`, `xyz`, `987` runs | -10 per pattern |
| **Keyboard Walks** | `qwerty`, `asdf`, `zxcv` and reverses | -10 per pattern |
| **Repeated Characters** | Single char appearing in 25%+ of password | -8 per char |
| **Repeated Patterns** | Structural repetition like `abab`, `xyzxyz` | -10 per pattern |
| **Common Passwords** | Top 100 most-used passwords globally | -50 instant fail |
| **Common Combos** | `password2024`, `admin123`, `qwerty999` | -15 per combo |
| **Dictionary Words** | Embedded common English words (4+ chars) | -6 per word |
| **Leet-Speak Variants** | `p@ssw0rd`, `h4ck3r`, `@dm1n` substitutions | -5 per word |
| **Date/Year Patterns** | Years (1950-2030), date formats `MM/DD/YYYY` | -5 per match |
| **Email/URL Detection** | Embedded email addresses or URLs | -8 per match |
| **Low Entropy** | Entropy below 60 bits flagged as critical | Score impact |
| **Two-Type Only** | Passwords using only 2 of 4 character types | -3 |

### Scoring System

| Component | Max Points |
|---|---|
| Length score | 40 |
| Composition score (4 character types) | 30 |
| Entropy score | 30 |
| **Total** | **100** |

| Grade | Score Range | Meaning |
|---|---|---|
| A+ | 95-100 | Excellent |
| A | 85-94 | Strong |
| B | 75-84 | Moderate |
| C | 65-74 | Weak |
| D | 50-64 | Very Weak |
| F | 0-49 | Critical |

---

## Testing

Run the full test suite with:

```bash
python -m pytest -v
```

The suite contains **117 tests** across 20 test classes:

| Test Class | Tests | Coverage |
|---|---|---|
| `TestRandomGeneration` | 15 | Length, charset isolation, ambiguous exclusion, uniqueness, pool size |
| `TestPassphraseGeneration` | 13 | Word count, separators, capitalization, number/special append, no-duplicate dictionary |
| `TestPinGeneration` | 7 | Length bounds, digit-only validation |
| `TestSequentialCheck` | 6 | Forward, reverse, long runs, no-match |
| `TestKeyboardCheck` | 5 | QWERTY, ASDF, reverse, multi-row |
| `TestRepeatedChars` | 4 | Threshold detection, boundary cases |
| `TestRepeatedPatterns` | 3 | `abab`, `xyzxyz`, no-pattern |
| `TestCommonPassword` | 3 | Known-bad and unique passwords |
| `TestDictionaryWords` | 3 | Embedded words, clean passwords |
| `TestLeetSpeak` | 4 | `p4ssw0rd`, `@dm1n`, `adm1n` variants |
| `TestDatePatterns` | 3 | Year detection, date formats |
| `TestCommonCombos` | 3 | `password2024`, `admin123` |
| `TestEmailUrl` | 3 | Email and URL embedding |
| `TestPasswordStrength` | 18 | Full scoring, edge cases, grade boundaries |
| `TestBase64Storage` | 4 | Encode/decode roundtrip, Unicode |
| `TestFileStorage` | 1 | Save/load file roundtrip |
| `TestEstimateCrackTime` | 4 | Zero, low, high entropy, type safety |
| `TestStrengthBar` | 3 | 0%, 50%, 100% bars |
| `TestMaskPassword` | 4 | Short/long masking, length preservation |
| `TestEdgeCases` | 8 | Min/max lengths, long passwords, special-only |

---

## Roadmap

### Completed

- [x] Three generation modes (Random, Passphrase, PIN)
- [x] Cryptographically secure randomness (PEP 506)
- [x] 12+ cybersecurity analysis checks
- [x] 100-point scoring with letter grades
- [x] Time-to-crack estimation
- [x] Visual strength bar
- [x] ANSI color-coded terminal UI
- [x] Base64-obfuscated password vault
- [x] Vault search and management
- [x] Ambiguous character exclusion
- [x] Session logging with summary
- [x] 117 automated tests

### Under Consideration

- [ ] Clipboard integration with auto-clear
- [ ] Export/import passwords (CSV, JSON)
- [ ] Password age tracking
- [ ] Custom word lists for passphrase generation
- [ ] Configurable crack-time assumptions
- [ ] Windows Terminal color profile detection

---

## Contributing

Contributions are welcome. To keep the project consistent:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-check`)
3. Add tests for any new functionality
4. Ensure all tests pass (`python -m pytest -v`)
5. Submit a pull request

### Code Style

- Follow existing patterns in the codebase
- Use `secrets` for any randomness (never `random`)
- Add tests in `tests/test_core.py` for new features
- Keep the zero-dependency constraint

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

```
MIT License -- Copyright (c) 2026 Edge Quantum
```

---

## Author

**Edge Quantum** ([@Marsh-Edge](https://github.com/Marsh-Edge))

---

## Acknowledgments

- [PEP 506](https://peps.python.org/pep-0506/) -- Python's `secrets` module for cryptographic randomness
- [Python Standard Library](https://docs.python.org/3/library/) -- All functionality built on stdlib
- NIST SP 800-63B -- Password strength guidelines
- [Have I Been Pwned](https://haveibeenpwned.com/) -- Inspiration for common password detection
