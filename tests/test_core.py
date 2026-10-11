import string
import tempfile
import math
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Generate.generate import (
    generate_random, generate_passphrase, generate_pin,
    PASSPHRASE_WORDS, SPECIAL_CHARS, AMBIGUOUS_CHARS,
    calc_pool_size,
)
from Testing.test import (
    test_password as analyze_password,
    _check_sequential, _check_keyboard,
    _check_repeated_chars, _check_repeated_patterns,
    _is_common_password, _find_dictionary_words,
    _detect_leetspeak, _check_date_patterns,
    _check_common_combos, _check_email_url,
    _check_only_two_types,
)
from app.utils import (
    encode_password, decode_password, estimate_crack_time,
    strength_bar, save_passwords, load_passwords,
    colorize, bold, dim, clear_screen, C,
)
from app import utils as app_utils
from Manage.management import _mask_password


@pytest.fixture
def restore_color():
    original = app_utils.color_enabled()
    yield
    app_utils.set_color_enabled(original)


class TestRandomGeneration:
    def test_length_is_correct(self):
        pw = generate_random(20)
        assert len(pw) == 20

    def test_minimum_length(self):
        pw = generate_random(8)
        assert len(pw) == 8

    def test_rejects_too_short(self):
        with pytest.raises(ValueError):
            generate_random(7)

    def test_max_length(self):
        pw = generate_random(128)
        assert len(pw) == 128

    def test_all_lowercase_when_only_lower(self):
        pw = generate_random(16, use_lower=True, use_upper=False, use_digits=False, use_special=False)
        assert pw.islower()

    def test_all_uppercase_when_only_upper(self):
        pw = generate_random(16, use_lower=False, use_upper=True, use_digits=False, use_special=False)
        assert pw.isupper()

    def test_all_digits_when_only_digits(self):
        pw = generate_random(16, use_lower=False, use_upper=False, use_digits=True, use_special=False)
        assert pw.isdigit()

    def test_all_special_when_only_special(self):
        pw = generate_random(16, use_lower=False, use_upper=False, use_digits=False, use_special=True)
        assert all(c in SPECIAL_CHARS for c in pw)

    def test_contains_all_selected_types(self):
        pw = generate_random(20)
        assert any(c.islower() for c in pw)
        assert any(c.isupper() for c in pw)
        assert any(c.isdigit() for c in pw)
        assert any(c in SPECIAL_CHARS for c in pw)

    def test_rejects_all_disabled(self):
        with pytest.raises(ValueError):
            generate_random(16, use_lower=False, use_upper=False, use_digits=False, use_special=False)

    def test_exclude_ambiguous_lowercase(self):
        pw = generate_random(50, use_lower=True, use_upper=False, use_digits=False, use_special=False, exclude_ambiguous=True)
        for c in pw:
            assert c not in 'ilo'

    def test_exclude_ambiguous_digits(self):
        pw = generate_random(50, use_lower=False, use_upper=False, use_digits=True, use_special=False, exclude_ambiguous=True)
        for c in pw:
            assert c not in '01'

    def test_uniqueness(self):
        passwords = set(generate_random(20) for _ in range(100))
        assert len(passwords) == 100

    def test_pool_size_calculation_full(self):
        pool = calc_pool_size(True, True, True, True)
        assert pool == 26 + 26 + 10 + len(SPECIAL_CHARS)

    def test_pool_size_no_special(self):
        pool = calc_pool_size(True, True, True, False)
        assert pool == 26 + 26 + 10


class TestPassphraseGeneration:
    def test_no_duplicate_words(self):
        assert len(PASSPHRASE_WORDS) == len(set(PASSPHRASE_WORDS))

    def test_word_count(self):
        pw = generate_passphrase(word_count=4, add_number=False, add_special=False)
        words = pw.split('-')
        assert len(words) == 4

    def test_all_words_are_valid(self):
        pw = generate_passphrase(word_count=5, add_number=False, add_special=False)
        for word in pw.split('-'):
            assert word.lower() in PASSPHRASE_WORDS or word in PASSPHRASE_WORDS

    def test_minimum_words(self):
        pw = generate_passphrase(word_count=3, add_number=False, add_special=False)
        assert len(pw.split('-')) == 3

    def test_rejects_too_few_words(self):
        with pytest.raises(ValueError):
            generate_passphrase(word_count=2)

    def test_capitalize(self):
        pw = generate_passphrase(word_count=4, capitalize=True, add_number=False, add_special=False)
        for word in pw.split('-'):
            assert word[0].isupper()

    def test_no_capitalize(self):
        pw = generate_passphrase(word_count=4, capitalize=False, add_number=False, add_special=False)
        for word in pw.split('-'):
            assert word[0].islower()

    def test_dot_separator(self):
        pw = generate_passphrase(word_count=4, separator='.', add_number=False, add_special=False)
        assert '.' in pw

    def test_underscore_separator(self):
        pw = generate_passphrase(word_count=4, separator='_', add_number=False, add_special=False)
        assert '_' in pw

    def test_space_separator(self):
        pw = generate_passphrase(word_count=4, separator=' ', add_number=False, add_special=False)
        assert ' ' in pw

    def test_add_number(self):
        pw = generate_passphrase(word_count=4, add_number=True, add_special=False)
        parts = pw.split('-')
        last = parts[-1]
        assert last.isdigit()

    def test_no_number(self):
        pw = generate_passphrase(word_count=4, add_number=False, add_special=False)
        parts = pw.split('-')
        for part in parts:
            assert not part.isdigit()

    def test_add_special(self):
        pw = generate_passphrase(word_count=4, add_number=False, add_special=True)
        assert pw[-1] in "!@#$%^&*"


class TestPinGeneration:
    def test_default_length(self):
        pin = generate_pin()
        assert len(pin) == 6
        assert pin.isdigit()

    def test_custom_length(self):
        pin = generate_pin(8)
        assert len(pin) == 8
        assert pin.isdigit()

    def test_min_length(self):
        pin = generate_pin(4)
        assert len(pin) == 4

    def test_max_length(self):
        pin = generate_pin(12)
        assert len(pin) == 12

    def test_rejects_too_short(self):
        with pytest.raises(ValueError):
            generate_pin(3)

    def test_rejects_too_long(self):
        with pytest.raises(ValueError):
            generate_pin(13)

    def test_all_digits(self):
        pin = generate_pin(10)
        assert all(c in string.digits for c in pin)


class TestSequentialCheck:
    def test_abc(self):
        issues = _check_sequential("passwordabc")
        assert 'abc' in issues

    def test_123(self):
        issues = _check_sequential("test123")
        assert '123' in issues

    def test_xyz(self):
        issues = _check_sequential("xyz789")
        assert 'xyz' in issues

    def test_long_sequential(self):
        issues = _check_sequential("abcdefgh")
        assert any('abcd' in i for i in issues)

    def test_no_sequential(self):
        issues = _check_sequential("xk8$mP2n")
        assert len(issues) == 0

    def test_reversed(self):
        issues = _check_sequential("testcba")
        assert len(issues) > 0


class TestKeyboardCheck:
    def test_qwerty(self):
        issues = _check_keyboard("passwordqwerty")
        assert 'qwerty' in issues

    def test_asdf(self):
        issues = _check_keyboard("testasdf")
        assert 'asdf' in issues

    def test_zxcv(self):
        issues = _check_keyboard("mypasswordzxcvbnm")
        found = any('zxcv' in i for i in issues)
        assert found

    def test_reversed_keyboard(self):
        issues = _check_keyboard("testytrewq")
        assert len(issues) > 0

    def test_no_keyboard(self):
        issues = _check_keyboard("xk8$mP2nQz")
        assert len(issues) == 0


class TestRepeatedChars:
    def test_repeated_char_detected(self):
        issues = _check_repeated_chars("aaaaaaaaaaab")
        found = any(c == 'a' for c, _ in issues)
        assert found

    def test_no_repetition(self):
        issues = _check_repeated_chars("abcdefghij")
        assert len(issues) == 0

    def test_25_percent_threshold(self):
        pw = "aa" + "bcdefghij"
        issues = _check_repeated_chars(pw)
        assert len(issues) == 0

    def test_above_threshold(self):
        pw = "aaaa" + "bcdefgh"
        issues = _check_repeated_chars(pw)
        assert len(issues) > 0


class TestRepeatedPatterns:
    def test_abab(self):
        issues = _check_repeated_patterns("abab")
        assert 'ab' in issues

    def test_xyzxyz(self):
        issues = _check_repeated_patterns("xyzxyz")
        assert 'xyz' in issues

    def test_no_pattern(self):
        issues = _check_repeated_patterns("abcdefgh")
        assert len(issues) == 0


class TestCommonPassword:
    def test_password(self):
        assert _is_common_password("password")

    def test_123456(self):
        assert _is_common_password("123456")

    def test_not_common(self):
        assert not _is_common_password("xK8$mP2nQz!vR")


class TestDictionaryWords:
    def test_hello(self):
        words = _find_dictionary_words("helloworld")
        assert 'hello' in words or 'world' in words

    def test_admin(self):
        words = _find_dictionary_words("admin123")
        assert 'admin' in words

    def test_no_words(self):
        words = _find_dictionary_words("xK8$mP2n")
        assert len(words) == 0


class TestLeetSpeak:
    def test_p4ssw0rd(self):
        words = _detect_leetspeak("p4ssw0rd")
        assert 'password' in words

    def test_at_dm1n(self):
        words = _detect_leetspeak("@dm1n")
        assert 'admin' in words

    def test_adm1n(self):
        words = _detect_leetspeak("adm1n")
        assert 'admin' in words

    def test_p4ssw0rd1(self):
        words = _detect_leetspeak("p4ssw0rd1")
        assert 'password' in words


class TestDatePatterns:
    def test_year_2024(self):
        issues = _check_date_patterns("password2024")
        assert '2024' in issues

    def test_date_format(self):
        issues = _check_date_patterns("pass12/25/2024word")
        assert len(issues) > 0

    def test_no_date(self):
        issues = _check_date_patterns("xK8$mP2nQz")
        assert len(issues) == 0


class TestCommonCombos:
    def test_password2024(self):
        issues = _check_common_combos("password2024")
        assert len(issues) > 0

    def test_admin123(self):
        issues = _check_common_combos("admin123")
        assert len(issues) > 0

    def test_no_combo(self):
        issues = _check_common_combos("xK8$mP2nQz!vR")
        assert len(issues) == 0


class TestEmailUrl:
    def test_email(self):
        issues = _check_email_url("user@example.com")
        assert any('email' in i for i in issues)

    def test_url(self):
        issues = _check_email_url("https://google.com")
        assert any('URL' in i for i in issues)

    def test_no_personal(self):
        issues = _check_email_url("xK8$mP2nQz")
        assert len(issues) == 0


class TestOnlyTwoTypes:
    def test_lower_digit(self):
        assert _check_only_two_types("abcdef123")

    def test_upper_lower(self):
        assert _check_only_two_types("AbCdEfGh")

    def test_all_four_types(self):
        assert not _check_only_two_types("aB3!")


class TestPasswordStrength:
    def test_empty_password(self):
        r = analyze_password("")
        assert r['score'] == 0
        assert r['grade'] == 'F'

    def test_common_password_gets_f(self):
        r = analyze_password("password")
        assert r['grade'] == 'F'

    def test_123456_gets_f(self):
        r = analyze_password("123456")
        assert r['grade'] == 'F'

    def test_short_password_penalized(self):
        r = analyze_password("abc")
        assert r['score'] < 50
        assert r['grade'] in ('D', 'F')

    def test_sequential_penalized(self):
        r = analyze_password("abcdefg1A!")
        seq_penalty = any('sequential' in i.lower() for i in r['issues'])
        assert seq_penalty

    def test_keyboard_penalized(self):
        r = analyze_password("qwerty1A!")
        kb_penalty = any('keyboard' in i.lower() for i in r['issues'])
        assert kb_penalty

    def test_repeated_pattern_penalized(self):
        r = analyze_password("abcabc1A!")
        rep_penalty = any('pattern' in i.lower() or 'repeat' in i.lower() for i in r['issues'])
        assert rep_penalty

    def test_dictionary_word_warning(self):
        r = analyze_password("helloworld1A!")
        dict_warn = any('dictionary' in w.lower() for w in r['warnings'])
        assert dict_warn

    def test_leetspeak_warning(self):
        r = analyze_password("p4ssw0rd!")
        leet_warn = any('leet' in w.lower() for w in r['warnings'])
        assert leet_warn

    def test_date_warning(self):
        r = analyze_password("password2024!")
        date_warn = any('date' in w.lower() for w in r['warnings'])
        assert date_warn

    def test_email_detected(self):
        r = analyze_password("user@example.com1A!")
        email_issue = any('email' in i.lower() for i in r['issues'])
        assert email_issue

    def test_strong_password_gets_good_grade(self):
        r = analyze_password("xK8$mP2nQz!vR9wL")
        assert r['grade'] in ('A+', 'A', 'B')

    def test_very_strong_gets_a_plus(self):
        r = analyze_password("xK8$mP2nQz!vR9wLbY4#jN1@")
        assert r['grade'] in ('A+', 'A')

    def test_entropy_calculation(self):
        r = analyze_password("abcdefghij")
        assert r['entropy_bits'] > 0
        expected = 10 * math.log2(26)
        assert abs(r['entropy_bits'] - round(expected, 2)) < 0.1

    def test_categories_count(self):
        r = analyze_password("abc")
        assert r['categories'] == 1

        r = analyze_password("aB3!")
        assert r['categories'] == 4

    def test_crack_time_present(self):
        r = analyze_password("xK8$mP2nQz")
        assert 'crack_time' in r
        assert isinstance(r['crack_time'], str)

    def test_score_range(self):
        for pw in ["password", "xK8$mP2nQz!vR", "abc", "qwerty123", "a"]:
            r = analyze_password(pw)
            assert 0 <= r['score'] <= 100

    def test_common_combo_penalized(self):
        r = analyze_password("password2024")
        combo_issue = any('combo' in i.lower() for i in r['issues'])
        assert combo_issue


class TestBase64Storage:
    def test_encode_decode_roundtrip(self):
        original = "xK8$mP2nQz!vR"
        encoded = encode_password(original)
        decoded = decode_password(encoded)
        assert decoded == original

    def test_encode_produces_different_string(self):
        original = "password123"
        encoded = encode_password(original)
        assert encoded != original

    def test_unicode_password(self):
        original = "pässwörd123!"
        encoded = encode_password(original)
        decoded = decode_password(encoded)
        assert decoded == original

    def test_empty_string(self):
        assert decode_password(encode_password("")) == ""


class TestFileStorage:
    def test_save_and_load(self, tmp_path):
        test_file = tmp_path / "analyze_passwords.txt"
        passwords = ["alpha123", "Beta456!", "gamma789#"]
        save_passwords.__wrapped__ = None

        with open(test_file, 'w', encoding='utf-8') as f:
            for pw in passwords:
                f.write(encode_password(pw) + '\n')

        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        loaded = []
        for line in content.split('\n'):
            line = line.strip()
            if line:
                loaded.append(decode_password(line))

        assert loaded == passwords


class TestEstimateCrackTime:
    def test_zero_entropy(self):
        assert estimate_crack_time(0) == "instant"

    def test_low_entropy(self):
        result = estimate_crack_time(10)
        assert 'seconds' in result or 'instant' in result

    def test_high_entropy(self):
        result = estimate_crack_time(128)
        assert 'billion' in result or 'universe' in result or 'years' in result

    def test_returns_string(self):
        for bits in [0, 10, 40, 80, 128, 256]:
            result = estimate_crack_time(bits)
            assert isinstance(result, str)


class TestStrengthBar:
    def test_full_bar(self):
        bar = strength_bar(100)
        assert '█' in bar
        assert '100%' in bar

    def test_empty_bar(self):
        bar = strength_bar(0)
        assert '░' in bar
        assert '0%' in bar

    def test_half_bar(self):
        bar = strength_bar(50)
        assert '█' in bar
        assert '░' in bar
        assert '50%' in bar


class TestMaskPassword:
    def test_short_password_fully_masked(self):
        for pw in ["a", "ab", "abc", "abcd"]:
            assert '*' in _mask_password(pw)
            assert pw not in _mask_password(pw)

    def test_medium_password_hides_middle(self):
        masked = _mask_password("abcdefgh")
        assert masked[0] == 'a'
        assert masked[-1] == 'h'
        assert 'bcdefg' not in masked

    def test_long_password_masked(self):
        masked = _mask_password("xK8$mP2nQz!vR")
        assert 'xK8$' in masked
        assert 'vR' in masked
        assert 'mP2nQz' not in masked

    def test_mask_same_length_as_password(self):
        for pw in ["a", "ab", "abcdefgh", "xK8$mP2nQz!vR"]:
            assert len(_mask_password(pw)) == len(pw)


class TestColorSupport:
    def test_no_color_env_disables(self, monkeypatch):
        monkeypatch.setenv('NO_COLOR', '1')
        monkeypatch.setattr(app_utils, '_enable_windows_vt', lambda: True)
        monkeypatch.setattr(app_utils.sys.stdout, 'isatty', lambda: True)
        assert app_utils._detect_color() is False

    def test_non_tty_disables(self, monkeypatch):
        monkeypatch.delenv('NO_COLOR', raising=False)
        monkeypatch.setattr(app_utils, '_enable_windows_vt', lambda: True)
        monkeypatch.setattr(app_utils.sys.stdout, 'isatty', lambda: False)
        assert app_utils._detect_color() is False

    def test_tty_enables(self, monkeypatch):
        monkeypatch.delenv('NO_COLOR', raising=False)
        monkeypatch.setattr(app_utils, '_enable_windows_vt', lambda: True)
        monkeypatch.setattr(app_utils.sys.stdout, 'isatty', lambda: True)
        assert app_utils._detect_color() is True

    def test_no_vt_disables(self, monkeypatch):
        monkeypatch.delenv('NO_COLOR', raising=False)
        monkeypatch.setattr(app_utils, '_enable_windows_vt', lambda: False)
        monkeypatch.setattr(app_utils.sys.stdout, 'isatty', lambda: True)
        assert app_utils._detect_color() is False

    def test_colorize_strips_codes_when_disabled(self, restore_color):
        app_utils.set_color_enabled(False)
        assert colorize("x", C.RED) == "x"
        assert bold("x") == "x"
        assert dim("x") == "x"

    def test_colorize_adds_codes_when_enabled(self, restore_color):
        app_utils.set_color_enabled(True)
        assert '\033' in colorize("x", C.RED)
        assert '\033' in bold("x")
        assert '\033' in dim("x")

    def test_strength_bar_plain_when_disabled(self, restore_color):
        app_utils.set_color_enabled(False)
        bar = strength_bar(50)
        assert '\033' not in bar
        assert '█' in bar
        assert '░' in bar
        assert '50%' in bar

    def test_clear_screen_noop_when_not_tty(self, monkeypatch):
        calls = []
        monkeypatch.setattr(app_utils.sys.stdout, 'isatty', lambda: False)
        monkeypatch.setattr(app_utils.os, 'system', lambda cmd: calls.append(cmd))
        clear_screen()
        assert calls == []

    def test_clear_screen_runs_when_tty(self, monkeypatch):
        calls = []
        monkeypatch.setattr(app_utils.sys.stdout, 'isatty', lambda: True)
        monkeypatch.setattr(app_utils.os, 'system', lambda cmd: calls.append(cmd))
        clear_screen()
        assert len(calls) == 1


class TestEdgeCases:
    def test_very_long_random(self):
        pw = generate_random(128)
        assert len(pw) == 128

    def test_min_passphrase_with_number(self):
        pw = generate_passphrase(word_count=3, add_number=True)
        parts = pw.split('-')
        assert len(parts) == 4
        assert parts[-1].isdigit()

    def test_min_passphrase_no_number(self):
        pw = generate_passphrase(word_count=3, add_number=False)
        assert len(pw.split('-')) == 3

    def test_max_passphrase_with_number(self):
        pw = generate_passphrase(word_count=8, add_number=True)
        parts = pw.split('-')
        assert len(parts) == 9
        assert parts[-1].isdigit()

    def test_max_passphrase_no_number(self):
        pw = generate_passphrase(word_count=8, add_number=False)
        assert len(pw.split('-')) == 8

    def test_pin_all_same_digit(self):
        for _ in range(50):
            pin = generate_pin(6)
            assert len(pin) == 6

    def test_only_special_chars(self):
        r = analyze_password("!@#$%^&*()")
        assert r['categories'] >= 1
        assert r['has_special']

    def test_very_long_password_test(self):
        long_pw = "aB3!" * 50
        r = analyze_password(long_pw)
        assert r['score'] > 0
        assert r['length'] == 200
