import logging

from pylxd import Client


class LXDHost:
    def __init__(self, name):
        self._client = Client()
        self._container = self._client.containers.get(name)

    async def run(self, command, check=True):
        logging.info("run %s$ %s", self._container.name, command)

        command = command.split(' ')

        result = self._container.execute(command)
        if check and result.exit_code != 0:
            print(result)
            raise FileNotFoundError
        return result.stdout


    async def put(self, path, local_path):
        content = open(local_path, 'rb')
        result = self._container.files.put(path, content)
        print(result)
