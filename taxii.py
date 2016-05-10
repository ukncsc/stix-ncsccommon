from cabby import create_client


def taxii(content, host, https, discovery, binding, username, password, inbox):
    client = create_client(host, use_https=https, discovery_path=discovery)
    content = content
    binding = binding
    client.set_auth(username=username, password=password)
    client.push(content, binding, uri=inbox)
