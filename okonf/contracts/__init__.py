from .files import (file_present, file_absent, file_copy, file_content)
from .apt import (apt_updated, apt_autoremoved, apt_present, apt_absent)

assert file_present
assert file_absent
assert file_copy
assert file_content

assert apt_updated
assert apt_autoremoved
assert apt_present
assert apt_absent
