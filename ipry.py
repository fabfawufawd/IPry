from .utils import *
import maxminddb
import ipaddress
import requests
import sys

def ip_api(ip):
    url = f'http://ip-api.com/json/{ip}?fields=731'
    response = requests.get(url)

    if response.status_code != 200:
        print(f'{COLORS["red"]}Error {COLORS["white"]}while receiving response from ip-api: {response.status_code}'+COLORS['reset'])
        raise SystemExit(1)
    return response.json()

def local_db(ip_address):
    try:
        with maxminddb.open_database(fdir('ip-to-city.mmdb')) as reader:
            city_data = reader.get(ip_address)

        with maxminddb.open_database(fdir('ip-to-asn.mmdb')) as reader:
            asn_data = reader.get(ip_address)
    except Exception as e:
        print(f'{COLORS["red"]}Error {COLORS["white"]}while reading the database: {e}'+COLORS['reset'])
        return None

    if city_data is None:
        return {
            'error': 'IP address not found in database.'
        }

    if asn_data is None:
        asn_data = {'autonomous_system_organization': 'N/A'}

    country = city_data.get('country', {}).get('names', {}).get('en', 'N/A')
    country_code = city_data.get('country', {}).get('iso_code', 'N/A')
    region_name = city_data.get('subdivisions', [{}])[0].get('names', {}).get('en', 'N/A')
    city = city_data.get('city', {}).get('names', {}).get('en', 'N/A')
    latitude = city_data.get('location', {}).get('latitude', 0.0)
    longitude = city_data.get('location', {}).get('longitude', 0.0)

    check_vpn_ranges_file()
    vpn_trie = load_vpn_ranges(fdir('vpn-ranges.txt'))
    is_vpn = check_vpn(ip_address, vpn_trie)

    #asn_number = asn_data.get('autonomous_system_number', 'N/A')
    isp = asn_data.get('autonomous_system_organization', 'N/A')

    result = {
        'country': country,
        'countryCode': country_code,
        'regionName': region_name,
        'city': city,
        'is_vpn': is_vpn,
        'lat': latitude,
        'lon': longitude,
        'isp': isp
    }
    return result

def find_ip(args):
    for arg in args:
        parts = arg.split('.')
        if len(parts) == 4 and all(part.isdigit() for part in parts):
            return arg
    return None

def find_arg(*arguments, next_arg=True):
    arguments = [arg.lower() for arg in arguments]

    for index, arg in enumerate(sys.argv):
        if arg.lower() in arguments:
            if next_arg:
                try:
                    return sys.argv[index + 1]
                except:
                    pass
            return True
    return None

def cli_main():
    if len(sys.argv) < 2:
        print(f'{COLORS["red"]}Usage: {COLORS["white"]}ipry [-h] [--raw] [--local-db] IP'+COLORS['reset'])

    else:
        ip_to_city = 'https://db-ip.com/db/download/ip-to-city-lite'
        ip_to_asn = 'https://db-ip.com/db/download/ip-to-asn-lite'

        if find_arg('--update'):
            try:
                check_for_update(ip_to_city, 'ip-to-city.mmdb', 'city')
                check_for_update(ip_to_asn, 'ip-to-asn.mmdb', 'asn')
                update_vpn_data()
            except Exception as er:
                print(f'{COLORS["red"]}Error: {COLORS["white"]}{er}'+COLORS['reset'])
                raise SystemExit(1)
            raise SystemExit(0)

        if find_arg('--help', '-h', next_arg=False):
            arguments = [
                f'{COLORS["magenta"]}--settings {COLORS["gray"]}— {COLORS["yellow"]}Change utility settings.',
                f'{COLORS["magenta"]}--help {COLORS["gray"]}— {COLORS["yellow"]}Shows this help message.',
                f'{COLORS["magenta"]}--raw {COLORS["gray"]}— {COLORS["yellow"]}Prints IP data without pretty_print.',
                f'{COLORS["magenta"]}--local-db {COLORS["gray"]}— {COLORS["yellow"]}Using local database.\n               {COLORS["gray"]}(from DB-IP.com, licensed under CC BY 4.0).',
                f'{COLORS["magenta"]}--update {COLORS["gray"]}— {COLORS["yellow"]}Update all databases.'
            ]

            formatted_help = '\n\n'.join([f'  {arg}' for arg in arguments])

            print(f'{COLORS["gray"]}Help:\n{formatted_help}'+COLORS['reset'])
            raise SystemExit(0)

        default_settings = {
            'raw': False,
            'local-db': False
        }

        try:
            with open(fdir('settings.json'), 'r', encoding='UTF-8') as file:
                settings = json.load(file)

                if not isinstance(settings, dict):
                    print(f'{COLORS["red"]}Error: {COLORS["white"]}settings.json is not a valid JSON object.'+COLORS['reset'])
                    raise SystemExit(1)
        except FileNotFoundError:
            #print(f'{COLORS["red"]}Error: {COLORS["white"]}Settings file not found.'+COLORS['reset'])

            try:
                with open(fdir('settings.json'), 'w') as f:
                    json.dump(default_settings, f, indent=4)
            except Exception as er:
                print(f'{COLORS["red"]}Error: {COLORS["white"]}{er}'+COLORS['reset'])
            else:
                #print(f'{COLORS["orange"]}settings.json {COLORS["green"]}successfully created.'+COLORS['reset'])
                settings = default_settings
        except json.JSONDecodeError:
            print(f'{COLORS["red"]}Error: {COLORS["white"]}settings.json contains invalid JSON. {COLORS["gray"]}(JSONDecodeError)'+COLORS['reset'])
            raise SystemExit(1)
        except Exception as er:
            print(f'{COLORS["red"]}Error: {COLORS["white"]}{er}'+COLORS['reset'])
            raise SystemExit(1)

        if find_arg('--settings'):
            change_settings()

        target_ip = find_ip(sys.argv)
        
        if not target_ip:
            print(f'{COLORS["red"]}Error: {COLORS["white"]}IP info not found.'+COLORS['reset'])
            raise SystemExit(1)

        try:
            ipaddress.ip_address(target_ip)
        except ValueError:
            print(f'{COLORS["red"]}Error: {COLORS["white"]}Invalid IP Address.'+COLORS['reset'])
            raise SystemExit(1)

        if any([find_arg('--local-db'), settings.get('local-db', False)]):
            check_databases()
            ip_info = local_db(target_ip)
        else:
            ip_info = ip_api(target_ip)

        if any([find_arg('--raw'), settings.get('raw', False)]):
            print(ip_info)
            raise SystemExit(0)
        pretty_print(ip_info)
        raise SystemExit(0)

if __name__ == '__main__':
    cli_main()