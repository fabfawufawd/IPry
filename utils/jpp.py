from typing import Any, Dict
from .other import COLORS

def pretty_print(data: Any, indent: int = 2) -> None:
    match data:
        case dict():
            print(f'{COLORS["white"]}{{')
            for i, (key, value) in enumerate(data.items()):
                is_last = i == len(data) - 1
                print(' ' * indent + f'{COLORS["purple"]}"{COLORS["yellow"]}{key}{COLORS["purple"]}"{COLORS["white"]}: ', end='')
                pretty_print(value, indent + 2)
                print(f'{COLORS["white"]}{"" if is_last else ","}')
            print(' ' * (indent - 2) + f'}}{COLORS["reset"]}', end='')

        case list():
            print(f'{COLORS["white"]}[')
            for i, item in enumerate(data):
                is_last = i == len(data) - 1
                print(' ' * indent, end='')
                pretty_print(item, indent + 2)
                print(f'{COLORS["white"]}{"" if is_last else ","}')
            print(' ' * (indent - 2) + f']{COLORS["reset"]}', end='')

        case bool():
            print(f'{COLORS["purple"]}{str(data).lower()}{COLORS["reset"]}', end='')

        case int() | float():
            str_num = f'{data:.4f}'.rstrip('0').rstrip('.')
            parts = str_num.split('.')
            if len(parts) == 1:
                print(f'{COLORS["purple"]}{parts[0]}{COLORS["reset"]}', end='')
            else:
                print(f'{COLORS["purple"]}{parts[0]}{COLORS["white"]}.{COLORS["purple"]}{parts[1]}{COLORS["reset"]}', end='')

        case None:
            print(f'{COLORS["purple"]}null{COLORS["reset"]}', end='')

        case _:
            print(f'{COLORS["purple"]}"{COLORS["yellow"]}{data}{COLORS["purple"]}"{COLORS["reset"]}', end='')