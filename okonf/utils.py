import subprocess


def get_file_hash(file_path):
    local_hash = subprocess.check_output(['sha256sum', file_path])
    return local_hash.split(b' ', 1)[0]
