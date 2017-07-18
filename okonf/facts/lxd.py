from pylxd import Client


async def container_is_present(lxdhost, name):
    return lxdhost.containers.exists(name)