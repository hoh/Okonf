import logging
import asyncssh


class SSHHost:

    def __init__(self, **kwargs):
        self.ssh_settings = kwargs

    async def run(self, command, check=True):
        host, username = self.ssh_settings['host'], \
                         self.ssh_settings['username']
        logging.info("run %s@%s$ %s", username, host, command)

        async with asyncssh.connect(**self.ssh_settings) as ssh:
            result = await ssh.run(command, check=check)
            logging.debug("Result stdout = '%s'", result.stdout)
            return result.stdout

    async def put(self, path, local_path):
        host = self.ssh_settings['host']
        logging.info("sftp %s -> %s:%s", local_path, host, path)

        async with asyncssh.connect(**self.ssh_settings) as ssh:
            async with ssh.start_sftp_client() as sftp:
                await sftp.put(local_path, path)
