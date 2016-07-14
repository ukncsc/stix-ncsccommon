import json
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from certuk_common import get_file_contents, taxii

with open('taxii-config.json') as data_file:
    CONFIG = json.load(data_file)

binding = CONFIG['taxii'][0]['binding']
content = get_file_contents(sys.argv[1])
discovery_path = CONFIG['taxii'][0]['discovery_path']
host = CONFIG['taxii'][0]['host']
https = CONFIG['taxii'][0]['ssl']
inbox = CONFIG['taxii'][0]['inbox']
password = CONFIG['taxii'][0]['password']
username = CONFIG['taxii'][0]['username']

taxii(content, host, https, discovery_path, binding, username, password, inbox)
