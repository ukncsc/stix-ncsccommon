from ConfigParser import SafeConfigParser
import datetime
from datetime import timedelta
from dateutil.tz import tzutc
import os
from StringIO import StringIO
import sys

import libtaxii as t
import libtaxii.clients as tc
from libtaxii.constants import *
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


def main():
    poll_params1 = tm11.PollParameters(
        allow_asynch=False,
        response_type=RT_COUNT_ONLY,
        content_bindings=[tm11.ContentBinding(binding_id=CB_STIX_XML_11)],
    )

    poll_req3 = tm11.PollRequest(
        message_id='PollReq03',
        collection_name=collection,
        poll_parameters=poll_params1,
        exclusive_begin_timestamp_label=datetime.datetime.now(
            tzutc()) - timedelta(days=int(days)),
        inclusive_end_timestamp_label=datetime.datetime.now(tzutc()),
    )
    poll_xml = poll_req3.to_xml()

    http_resp = client.call_taxii_service2(
        server, path, VID_TAXII_XML_11,
        poll_xml, port=port)
    taxii_message = t.get_message_from_http_response(
        http_resp, poll_req3.message_id)
    if taxii_message.message_type == MSG_POLL_RESPONSE:
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
        print("[-] Error with TAXII response")

if __name__ == "__main__":
    main()
