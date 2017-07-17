from okonf.facts.apt import apt_is_installed


async def apt_updated(host):
    await host.run("sudo apt-get update")


async def apt_autoremoved(host):
    await host.run("sudo apt-get -y autoremove")


async def apt_present(host, name):
    if not await apt_is_installed(host, name):
        await host.run("sudo apt-get install -y {}".format(name))


async def apt_absent(host, name, autoremove=False):
    if await apt_is_installed(host, name):
        await host.run("sudo apt-get remove -y {}".format(name))
        if autoremove:
            await apt_autoremoved(host)
