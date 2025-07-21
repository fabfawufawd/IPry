import ipaddress

def load_vpn_ranges(filename='vpn-ranges.txt'):
    networks = []
    with open(filename, 'r') as file:
        for line in file:
            net = line.strip()
            if not net:
                continue
            try:
                network = ipaddress.ip_network(net)
                networks.append(network)
            except ValueError:
                continue

    networks.sort(key=lambda n: n.prefixlen, reverse=True)
    return networks

def check_vpn(ip, networks):
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        return 'Invalid IP Address'

    for net in networks:
        if ip_obj in net:
            return True
    return False