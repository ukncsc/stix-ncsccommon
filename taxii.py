def _taxii(content):
    client = create_client(CONFIG['taxii'][0]['host'], use_https=CONFIG['taxii'][0][
                           'ssl'], discovery_path=CONFIG['taxii'][0]['discovery_path'])
    content = content
    binding = CONFIG['taxii'][0]['binding']
    client.set_auth(username=CONFIG['taxii'][0][
                    'username'], password=CONFIG['taxii'][0]['password'])
    client.push(content, binding, uri=CONFIG['taxii'][0]['inbox_path'])
