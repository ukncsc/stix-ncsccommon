import json

import requests
from cabby import create_client, exceptions


def _construct_headers():
    headers = {
        'Content-Type': 'application/xml',
        'Accept': 'application/json'
    }
    return headers


def get_file_contents(filename):
    with open(filename, 'r') as fd:
        return fd.read()


def inbox_package(endpoint_url, stix_package):
    """Inbox the package to the adapter."""
    data = stix_package
    headers = _construct_headers()
    response = requests.post(endpoint_url, data=data, headers=headers)
    print(json.dumps(response.json(), indent=4))
    return


def taxii(content, host, https, discovery, binding, username, password, inbox):
    try:
        client = create_client(host, use_https=https, discovery_path=discovery)
        content = content
        binding = binding
        client.set_auth(username=username, password=password)
        client.push(content, binding, uri=inbox)
        print("TAXII Successful")
    except Exception as e:
        print(e)
        return False
