from .updater import get_release_info, download_file, extract_file
from .other import COLORS, fdir
import json
import os

curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
json_path = os.path.join(os.path.dirname(__file__), 'last_date.json')

def check_databases():
    required_links = {
        'ip-to-city.mmdb': 'https://db-ip.com/db/download/ip-to-city-lite',
        'ip-to-asn.mmdb': 'https://db-ip.com/db/download/ip-to-asn-lite'
    }

    if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
        last_dates = {'city': None, 'asn': None}
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(last_dates, f, indent=4)
        print(f'{COLORS["white"]}Created new {COLORS["orange"]}last_date.json{COLORS["reset"]}')
    else:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                last_dates = json.load(f)
        except json.JSONDecodeError:
            print(f'{COLORS["red"]}Error: {COLORS["white"]}Invalid JSON in last_date.json. Resetting..{COLORS["reset"]}')
            last_dates = {'city': None, 'asn': None}
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(last_dates, f, indent=4)

    missing = [name for name in required_links if not os.path.isfile(fdir(name))]

    if missing:
        print(f'{COLORS["orange"]}Missing database files: {COLORS["blue"]}{", ".join(missing)}{COLORS["white"]}.{COLORS["reset"]}')

        for filename in missing:
            try:
                release_info = get_release_info(required_links[filename])
                archive_path = download_file(release_info['download_link'], save_path=curr_dir)
                extract_file(archive_path, dest_folder=curr_dir, filename=filename)

                db_key = 'city' if 'city' in filename else 'asn'
                last_dates[db_key] = release_info['release_date']

                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(last_dates, f, indent=4)

            except Exception as er:
                print(f'{COLORS["red"]}Error: {er}{COLORS["reset"]}')