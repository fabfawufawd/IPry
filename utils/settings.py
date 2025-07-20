from .other import COLORS, fdir
import json

def apply_setting(key, value):
    try:
        with open(fdir('settings.json'), 'r', encoding='UTF-8') as file:
            settings = json.load(file)

        settings[key] = value

        with open(fdir('settings.json'), 'w', encoding='UTF-8') as file:
            json.dump(settings, file, indent=4)
    except Exception as er:
        return f'{COLORS["red"]}Error: {COLORS["white"]}{er}'+COLORS["reset"]
    else:
        return f'{COLORS["green"]}Successfully changed!{COLORS["reset"]}'

def change_settings():
    print(f'{COLORS["orange"]}Program settings{COLORS["reset"]}')

    try:
        with open(fdir('settings.json'), 'r', encoding='UTF-8') as file:
            settings = json.load(file)
    except Exception as er:
        print(f'{COLORS["red"]}Error loading settings: {COLORS["white"]}{er}{COLORS["reset"]}')
        raise SystemExit(1)

    settings_list = ('raw', 'local-db', 'exit')

    curr_raw = settings.get('raw', False)
    curr_db = settings.get('local-db', False)

    # When local-db is enabled, we use the DB-IP Free IP-to-City Lite database.
    # Source: https://db-ip.com, License: CC BY 4.0

    settings_help = '\n'.join([
        f'{COLORS["white"]}• {COLORS["blue"]}raw {COLORS["white"]}- {COLORS["gray"]}Prints raw data without pretty_print (Current: {curr_raw})',
        f'{COLORS["white"]}• {COLORS["blue"]}local-db {COLORS["white"]}- {COLORS["gray"]}Get info from local database (Current: {curr_db})',
        f'{COLORS["white"]}  • {COLORS["gray"]}geolocation database from DB-IP.com (CC BY 4.0)'
    ])

    print(f'\n{settings_help}\n{COLORS["reset"]}')

    try:
        command = input(COLORS["white"] + '> ' + COLORS["pink"]).strip().lower()

        if command not in settings_list:
            print(f'{COLORS["red"]}Error: {COLORS["white"]}Setting not found{COLORS["reset"]}')
            raise SystemExit(1)

        if command == 'raw':
            current_value = settings.get('raw', False)
            new_value = not current_value
            print(apply_setting('raw', new_value))
            raise SystemExit(0)
        elif command == 'local-db':
            current_value = settings.get('local-db', False)
            new_value = not current_value
            print(apply_setting('local-db', new_value))
            raise SystemExit(0)
        elif command == 'exit':
            raise SystemExit(0)
    except KeyboardInterrupt:
        print(COLORS['reset'])
        raise SystemExit(0)