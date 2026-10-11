import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.utils import (
    C, colorize, dim, print_section, print_ok, print_warn,
    print_error, print_info, load_passwords, save_passwords,
)


def run():
    print_section("PASSWORD VAULT", C.CYAN + C.BOLD)
    print()

    passwords = load_passwords()

    if not passwords:
        print_warn("No passwords saved yet.")
        input(f"\n  {colorize('Press Enter to return...', C.DIM)}")
        return

    print(f"  {colorize(f'{len(passwords)} password(s) in vault', C.WHITE)}")
    print()

    print(f"    {colorize('[1]', C.WHITE)} View all passwords")
    print(f"    {colorize('[2]', C.WHITE)} Search passwords")
    print(f"    {colorize('[3]', C.WHITE)} Delete a password")
    print(f"    {colorize('[4]', C.WHITE)} Clear entire vault")
    print()

    choice = input(f"  Select option {colorize('(1-4)', C.DIM)}: ").strip()

    if choice == '1':
        _view_all(passwords)
    elif choice == '2':
        _search(passwords)
    elif choice == '3':
        _delete(passwords)
    elif choice == '4':
        _clear_vault(passwords)
    else:
        print_error("Invalid option.")


def _view_all(passwords: list):
    print()
    print(colorize("  " + "-" * 52, C.DIM))
    print(f"  {colorize('ALL SAVED PASSWORDS', C.BOLD + C.WHITE)}")
    print(colorize("  " + "-" * 52, C.DIM))
    print()

    for i, pw in enumerate(passwords, 1):
        masked = _mask_password(pw)
        print(f"    {colorize(str(i), C.CYAN)}. {masked}  {dim(f'({len(pw)} chars)')}")

    print()
    print(colorize("  " + "-" * 52, C.DIM))

    show = input(f"\n  Reveal a password? Enter number or {colorize('Enter to skip', C.DIM)}: ").strip()
    if show and show.isdigit():
        idx = int(show) - 1
        if 0 <= idx < len(passwords):
            print()
            print(f"    {colorize('Password:', C.BOLD)} {colorize(passwords[idx], C.GREEN)}")
            print(f"    {colorize('Length:', C.BOLD)} {len(passwords[idx])} characters")
        else:
            print_error("Invalid number.")

    input(f"\n  {colorize('Press Enter to return...', C.DIM)}")


def _search(passwords: list):
    print()
    query = input(f"  Search term: ").strip()
    if not query:
        print_warn("Empty search.")
        return

    results = []
    for i, pw in enumerate(passwords):
        if query.lower() in pw.lower():
            results.append((i, pw))

    print()
    if not results:
        print_warn(f"No passwords match '{query}'.")
    else:
        print(f"  {colorize(f'{len(results)} match(es) found', C.GREEN)}")
        print()
        for idx, pw in results:
            masked = _mask_password(pw)
            print(f"    {colorize(str(idx + 1), C.CYAN)}. {masked}  {dim(f'({len(pw)} chars)')}")

        show = input(f"\n  Reveal a password? Enter number or {colorize('Enter to skip', C.DIM)}: ").strip()
        if show and show.isdigit():
            reveal_idx = int(show) - 1
            for idx, pw in results:
                if idx == reveal_idx:
                    print(f"\n    {colorize('Password:', C.BOLD)} {colorize(pw, C.GREEN)}")
                    break
            else:
                print_error("Invalid number from results.")

    input(f"\n  {colorize('Press Enter to return...', C.DIM)}")


def _delete(passwords: list):
    print()
    for i, pw in enumerate(passwords, 1):
        masked = _mask_password(pw)
        print(f"    {colorize(str(i), C.CYAN)}. {masked}  {dim(f'({len(pw)} chars)')}")

    print()
    choice = input(f"  Enter number to delete or {colorize('Enter to cancel', C.DIM)}: ").strip()
    if not choice:
        print_info("Cancelled.")
        return

    if not choice.isdigit():
        print_error("Invalid input.")
        return

    idx = int(choice) - 1
    if idx < 0 or idx >= len(passwords):
        print_error("Invalid number.")
        return

    masked = _mask_password(passwords[idx])
    confirm = input(f"  Delete {colorize(masked, C.RED)}? {colorize('(y/n)', C.DIM)}: ").strip().lower()
    if confirm == 'y':
        passwords.pop(idx)
        save_passwords(passwords)
        print_ok("Password deleted.")
    else:
        print_info("Cancelled.")

    input(f"\n  {colorize('Press Enter to return...', C.DIM)}")


def _clear_vault(passwords: list):
    print()
    print_warn(f"This will delete ALL {len(passwords)} saved passwords.")
    confirm = input(f"  Are you sure? {colorize('Type YES to confirm', C.RED)}: ").strip()
    if confirm == 'YES':
        save_passwords([])
        print_ok("Vault cleared.")
    else:
        print_info("Cancelled.")

    input(f"\n  {colorize('Press Enter to return...', C.DIM)}")


def _mask_password(pw: str) -> str:
    if len(pw) <= 4:
        return '*' * len(pw)
    if len(pw) <= 8:
        return pw[0] + '*' * (len(pw) - 2) + pw[-1]
    return pw[:4] + '*' * (len(pw) - 8) + pw[-4:]


if __name__ == '__main__':
    run()
