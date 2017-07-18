from okonf.facts.lxd import container_is_present


async def container_present(lxdhost, name):

    config = {
        'name': name,
        'source': {'type': 'image', 'fingerprint': '7a7ff654cbd8'},
    }

    if not await container_is_present(lxdhost, name):
        container = lxdhost.containers.create(config, wait=True)
        container.start()

