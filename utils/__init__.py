from .updater import check_for_update, update_vpn_data, check_vpn_ranges_file
from .jpp import pretty_print
from .downloader import *
from .settings import *
import os

if os.name == 'nt':
    from .check_vpn_win import *
else:
    from .check_vpn import *

from .other import COLORS, fdir