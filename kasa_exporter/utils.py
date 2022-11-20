from subprocess import Popen, PIPE


def ping(address: str, timeout: int = 5) -> bool:
    command = ["ping", "-c", "1", "-W", str(timeout), address]
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    proc.communicate()
    return proc.returncode == 0
