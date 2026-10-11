import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.utils import (
    C, colorize, bold, dim, clear_screen, print_header,
    print_section, print_ok, print_warn, print_error, print_info,
)
from Generate.generate import run as run_generate
from Testing.test import run as run_test
from Manage.management import run as run_manage


def print_menu():
    print(colorize("  MAIN MENU", C.BOLD + C.WHITE))
    print(colorize("  " + "-" * 48, C.DIM))
    print()
    print(f"    {colorize('[1]', C.BOLD + C.CYAN)}  Generate Password")
    print(f"        {dim('Random, passphrase, or PIN generation')}")
    print()
    print(f"    {colorize('[2]', C.BOLD + C.CYAN)}  Test Password")
    print(f"        {dim('Cybersecurity strength analysis')}")
    print()
    print(f"    {colorize('[3]', C.BOLD + C.CYAN)}  Password Vault")
    print(f"        {dim('View, search, and manage saved passwords')}")
    print()
    print(f"    {colorize('[4]', C.BOLD + C.CYAN)}  Exit")
    print()
    print(colorize("  " + "=" * 48, C.DIM))


def show_session_log(log: list):
    if not log:
        return

    print()
    print(colorize("  " + "=" * 52, C.CYAN))
    print(colorize("            SESSION SUMMARY", C.BOLD + C.WHITE))
    print(colorize("  " + "=" * 52, C.CYAN))
    print()
    print(f"    {colorize('Total actions:', C.BOLD)} {len(log)}")
    print()

    for i, entry in enumerate(log, 1):
        time_str = colorize(entry['time'], C.DIM)
        action_str = colorize(entry['action'], C.WHITE)
        print(f"    {colorize(str(i), C.CYAN)}. [{time_str}] {action_str}")
        if entry.get('detail'):
            print(f"       {dim(entry['detail'])}")

    print()
    print(colorize("  " + "=" * 52, C.CYAN))


def _print_exit_banner():
    print()
    print(colorize("  " + "=" * 52, C.CYAN))
    print(colorize("  Exiting NeN-Password Manager.", C.BOLD + C.WHITE))
    print(colorize("  Stay secure. Never reuse passwords.", C.DIM))
    print(colorize("  " + "=" * 52, C.CYAN))
    print()


def main():
    session_log = []
    last_password = None

    try:
        while True:
            print_header()
            print_menu()

            choice = input(f"\n  {colorize('Select', C.WHITE)} (1-4): ").strip()

            if choice == '1':
                ts = datetime.now().strftime('%H:%M:%S')
                print()
                print_info(f"[{ts}] Password Generator")
                pw = run_generate()
                if pw:
                    last_password = pw
                    session_log.append({
                        'time': ts,
                        'action': 'Generated password',
                        'detail': f'Length: {len(pw)} chars',
                    })

            elif choice == '2':
                ts = datetime.now().strftime('%H:%M:%S')
                print()
                print_info(f"[{ts}] Password Tester")
                result, was_modified = run_test(last_password=last_password)
                if result:
                    if was_modified:
                        session_log.append({
                            'time': ts,
                            'action': 'Tested & improved password',
                            'detail': f'{len(last_password) if last_password else 0} -> {len(result)} chars',
                        })
                    else:
                        session_log.append({
                            'time': ts,
                            'action': 'Tested password',
                            'detail': f'Length: {len(result)} chars',
                        })
                    last_password = result

            elif choice == '3':
                ts = datetime.now().strftime('%H:%M:%S')
                print()
                print_info(f"[{ts}] Password Vault")
                run_manage()
                session_log.append({
                    'time': ts,
                    'action': 'Accessed password vault',
                })

            elif choice == '4':
                clear_screen()
                show_session_log(session_log)
                _print_exit_banner()
                break

            else:
                print_error("Invalid option. Enter 1-4.")
                input(f"\n  {colorize('Press Enter to continue...', C.DIM)}")
    except (KeyboardInterrupt, EOFError):
        print()
        show_session_log(session_log)
        _print_exit_banner()


if __name__ == '__main__':
    main()
