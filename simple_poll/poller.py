"""
Basic Poller Script.

This script polls a given taxii server for new messages.
"""

from ConfigParser import SafeConfigParser
import datetime
from datetime import timedelta
from dateutil.tz import tzutc
import os
from StringIO import StringIO
import sys

import libtaxii as t
import libtaxii.clients as tc
from libtaxii.constants import CB_STIX_XML_11
from libtaxii.constants import MSG_POLL_RESPONSE
from libtaxii.constants import RT_COUNT_ONLY
from libtaxii.constants import VID_TAXII_XML_11
import libtaxii.messages_11 as tm11
from stix.core import STIXPackage

path = os.path.dirname(os.path.abspath(sys.argv[0]))
parser = SafeConfigParser()
parser.read(path + '/config.ini')

username = parser.get('TAXII', 'Username')
password = parser.get('TAXII', 'Password')
proxy = parser.getboolean('TAXII', 'Proxy')
proxyaddress = parser.get('TAXII', 'ProxyAddress')
ssl = parser.getboolean('TAXII', 'HTTPS')
collection = parser.get('TAXII', 'Collection')
server = parser.get('TAXII', 'Server')
port = parser.get('TAXII', 'Port')
path = parser.get('TAXII', 'Path')
days = parser.get('TAXII', 'Days')

client = tc.HttpClient()
client.set_auth_type(tc.HttpClient.AUTH_BASIC)
client.set_use_https(ssl)
if proxy is True:
    client.set_proxy(proxyaddress)
client.set_auth_credentials(
    {'username': username, 'password': password})


def _saveTimestamp(timestamp=None):
    mtimestamp = timestamp
    if not timestamp:
        mtimestamp = datetime.datetime.now(tzutc())
    fname = "timestamp"
    f = open(fname, "w")
    f.write(mtimestamp)
    f.close()


def _readTimestamp():
    fname = "timestamp"
    f = open(fname, "r")
    mtimestamp = f.read()
    f.close()
    return mtimestamp


def _main(first=True):
    if first:
        begin = datetime.datetime.now(tzutc()) - timedelta(days=int(days))
    else:
        try:
            begin = _readTimestamp()
        except IOError:
            print("[-] No timestamp file found have you 'first_run'?")
            sys.exit(0)

    end = datetime.datetime.now(tzutc())

    poll_params1 = tm11.PollParameters(
        allow_asynch=False,
        response_type=RT_COUNT_ONLY,
        content_bindings=[tm11.ContentBinding(binding_id=CB_STIX_XML_11)],
    )

    try:
        poll_req3 = tm11.PollRequest(
            message_id='PollReq03',
            collection_name=collection,
            poll_parameters=poll_params1,
            exclusive_begin_timestamp_label=begin,
            inclusive_end_timestamp_label=end,
        )
    except ValueError:
        print("[-] Invalid timestamp file")
        sys.exit(0)

    except Exception:
        print("[-] Error with PollRequest")

    poll_xml = poll_req3.to_xml()

    http_resp = client.call_taxii_service2(
        server, path, VID_TAXII_XML_11,
        poll_xml, port=port)
    taxii_message = t.get_message_from_http_response(
        http_resp, poll_req3.message_id)
    if taxii_message.message_type == MSG_POLL_RESPONSE:
        if taxii_message.content_blocks:
            try:
                for content in taxii_message.content_blocks:
                    package_io = StringIO(content.content)
                    pkg = STIXPackage.from_xml(package_io)
                    title = pkg.id_.split(':', 1)[-1]
                    with open(title + ".xml", "w") as text_file:
                        text_file.write(content.content)
                    print("[+] Successfully generated " + title)
            except Exception:
                print("[-] Error with TAXII response")
        else:
            print("[+] No content returned")
        _saveTimestamp(str(end))
    else:
        print("[-] Error with TAXII response")


def _usage():
    print("Usage: poller.py [first_run|check_new]")
    sys.exit(0)

if __name__ == "__main__":
    try:
        op = sys.argv[1]
    except IndexError:
        _usage()
    if op == "first_run":
        _main(True)
    elif op == "check_new":
        _main(None)
    else:
        _usage()
