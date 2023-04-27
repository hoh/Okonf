from .abstract import Fact
from ..connectors.abstract import Executor
from ..connectors.exceptions import ShellError


class DockerImagePulled(Fact):
    """Ensure that a file is present"""

    image: str
    tag: str

    def __init__(self, image: str, tag: str = None) -> None:
        if tag:
            self.image, self.tag = image, tag
        else:
            self.image, self.tag = image.split(":", 1)

    async def enquire(self, host: Executor) -> bool:
        command = f"docker image exists {self.image}:{self.tag}"
        result = await host.run(command)
        if result.exit_code == 0:
            return True
        elif result.exit_code == 1:
            return False
        else:
            raise ShellError(
                result.exit_code, stdout=result.stdout, stderr=result.stderr
            )

    async def enforce(self, host: Executor) -> bool:
        await host.run(f"docker pull {self.image}:{self.tag}")
        return True
