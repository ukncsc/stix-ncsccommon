from os import path
import sys
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from certuk_common import get_file_contents, taxii

binding = "urn:stix.mitre.org:xml:1.1.1"
content = get_file_contents(sys.argv[1])
discovery_path = "taxii-discovery-service"
host = "taxii.example.org"
https = False
inbox = "/taxii-data"
password = "password"
username = "username"

taxii(content, host, https, discovery_path, binding, username, password, inbox)
