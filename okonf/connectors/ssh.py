import logging
import asyncssh

from okonf.connectors.exceptions import NoSuchFileError, ShellError


class SSHHost:

    def __init__(self, **kwargs):
        self.ssh_settings = kwargs

    async def run(self, command, check=True, no_such_file=False):
        host, username = self.ssh_settings['host'], \
                         self.ssh_settings['username']
        logging.info("run %s@%s$ %s", username, host, command)

        async with asyncssh.connect(**self.ssh_settings) as ssh:
            result = await ssh.run(command, check=False)

            if no_such_file and result.exit_status != 0:
                if result.stderr.endswith('No such file or directory\n'):
                    raise NoSuchFileError(result.exit_status,
                                          stdout=result.stdout,
                                          stderr=result.stderr)

            if check and result.exit_status != 0:
                raise ShellError(result.exit_status,
                                 stdout=result.stdout,
                                 stderr=result.stderr)

            logging.debug("Result stdout = '%s'", result.stdout)
            return result.stdout

    async def put(self, path, local_path):
        host = self.ssh_settings['host']
        if path.startswith('~/'):
            username = self.ssh_settings['username']
            path = "/home/{}/{}".format(username, path[2:])

        logging.info("sftp %s -> %s:%s", local_path, host, path)
        async with asyncssh.connect(**self.ssh_settings) as ssh:
            async with ssh.start_sftp_client() as sftp:
                await sftp.put(local_path, path)
