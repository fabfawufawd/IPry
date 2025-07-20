import ipaddress
import pytricia

def load_vpn_ranges(filename='vpn-ranges.txt'):
    trie = pytricia.PyTricia()
    with open(filename, 'r') as file:
        for line in file:
            network = line.strip()
            trie[network] = True
    return trie

def check_vpn(ip, trie):
    try:
        ipaddress.ip_address(ip)
        return trie.get(ip) != None
    except ValueError:
        return 'Invalid IP Address'