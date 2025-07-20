from .other import COLORS, fdir
from pipebar import ProgressBar
from bs4 import BeautifulSoup
import requests
import shutil
import gzip
import time
import json
import os

vpn_ranges_link = 'https://raw.githubusercontent.com/josephrocca/is-vpn/main/vpn-or-datacenter-ipv4-ranges.txt'

def download_file(url, save_path='.', file_name=None):
    url = url.strip('/')
    if file_name is None:
        file_name = url.split('/')[-1]
    full_path = os.path.join(save_path, file_name)

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    total_size_mb = total_size / (1024 * 1024)
    print(f'Downloading {file_name} ({total_size_mb:.1f} MB)')

    try:
        with ProgressBar(total=total_size, unit='MB', scale=1024 * 1024) as pbar:
            with open(full_path, 'wb') as file:
                for data in response.iter_content(chunk_size=1024):
                    file.write(data)
                    pbar.update(len(data))
        return full_path
    except KeyboardInterrupt:
        print(f'\n{COLORS["red"]}ERROR: Aborted by user.{COLORS["reset"]}')
        if os.path.exists(full_path):
            os.remove(full_path)
        raise SystemExit(0)

def extract_file(archive_path, dest_folder, filename):
    try:
        os.makedirs(dest_folder, exist_ok=True)
        final_path = os.path.join(dest_folder, filename)
        hidden_path = os.path.join(dest_folder, f'.{filename}')

        with gzip.open(archive_path, 'rb') as f_in:
            with open(hidden_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.replace(hidden_path, final_path)
        os.remove(archive_path)

        print(f'File {COLORS["green"]}{filename}{COLORS["reset"]} successfully extracted.')
    except Exception as er:
        print(f'{COLORS["red"]}ERROR: {COLORS["reset"]}{er}')
        if 'hidden_path' in locals() and os.path.exists(hidden_path):
            os.remove(hidden_path)
        raise SystemExit(1)

def get_release_info(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    mmdb_card = soup.select_one('.card:has(dd:-soup-contains("MMDB"))')
    if mmdb_card:
        release_date = mmdb_card.select_one('dl dd:nth-of-type(2)')
        download_link = mmdb_card.select_one('.px-1.mb-1 a')

        if release_date and download_link:
            return {
                'release_date': release_date.text.strip(),
                'download_link': download_link['href']
            }
    return None

def check_for_update(db_link, filename, db_type):
    data = get_release_info(db_link)
    if not data:
        print(f'{COLORS["red"]}ERROR: {COLORS["white"]}Could not retrieve release info for {COLORS["orange"]}{filename}{COLORS["reset"]}')
        raise SystemExit(1)

    json_path = os.path.join(os.path.dirname(__file__), 'last_date.json')

    if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump({'city': None, 'asn': None}, file, indent=4)
        print(f'{COLORS["white"]}Created new {COLORS["orange"]}last_date.json{COLORS["reset"]}')

    with open(json_path, 'r', encoding='utf-8') as file:
        try:
            last_dates = json.load(file)
        except json.JSONDecodeError:
            print(f'{COLORS["red"]}ERROR: {COLORS["white"]}Invalid JSON format in {COLORS["orange"]}last_date.json{COLORS["white"]}. Resetting file.{COLORS["reset"]}')
            last_dates = {'city': None, 'asn': None}
            with open(json_path, 'w', encoding='utf-8') as reset_file:
                json.dump(last_dates, reset_file, indent=4)

    if db_type not in last_dates:
        last_dates[db_type] = None

    if data['release_date'] != last_dates[db_type]:
        new_version = data['release_date']
        link = data['download_link']

        print(f'{COLORS["green"]}New version available for {filename}:{COLORS["reset"]} {new_version}')

        last_dates[db_type] = new_version
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(last_dates, file, indent=4)

        full_path = download_file(link)
        extract_file(full_path, fdir(''), filename)
        print()
    else:
        print(f'{COLORS["cyan"]}{filename}{COLORS["white"]} is up to date.{COLORS["reset"]}')

def update_vpn_data():
    local_path = fdir('vpn-ranges.txt')

    try:
        response = requests.get(vpn_ranges_link, timeout=10)
        response.raise_for_status()
        new_content = response.text.strip()

        if not new_content:
            print(f'{COLORS["red"]}ERROR: {COLORS["white"]}downloaded vpn_ranges.txt content is empty.{COLORS["reset"]}')
            return

        if os.path.exists(local_path):
            with open(local_path, 'r', encoding='utf-8') as f:
                old_content = f.read().strip()
        else:
            old_content = None

        if old_content == new_content:
            print(f'{COLORS["cyan"]}vpn-ranges.txt {COLORS["white"]}is up to date.{COLORS["reset"]}')
            return

        with open(local_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f'{COLORS["orange"]}vpn-ranges.txt {COLORS["green"]}updated successfully.{COLORS["reset"]}')

    except requests.RequestException as e:
        print(f'{COLORS["red"]}ERROR: {COLORS["white"]}Network error while updating vpn-ranges.txt: {COLORS["yellow"]}{e}{COLORS["reset"]}')
    except IOError as e:
        print(f'{COLORS["red"]}ERROR: {COLORS["white"]}File error while updating vpn-ranges.txt: {COLORS["yellow"]}{e}{COLORS["reset"]}')

def check_vpn_ranges_file():
    path = fdir('vpn-ranges.txt')

    if not os.path.exists(path):
        download_file(vpn_ranges_link, save_path=os.path.dirname(path), file_name='vpn-ranges.txt')