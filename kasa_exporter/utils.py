# Copyright 2021-2022 Thomas Helander
# All rights reserved.
import platform
from subprocess import Popen, PIPE


def _ping_linux(address: str, timeout: int = 5) -> bool:
    command = ["ping", "-c", "1", "-W", str(timeout), address]
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    proc.communicate()
    return proc.returncode == 0


def _ping_windows(address: str, timeout: int = 5) -> bool:
    # Windows uses a ms timeout instead of second.
    command = ["ping", "-n", "1", "-w", str(timeout * 1000), address]
    proc = Popen(command, stdout=PIPE, stderr=PIPE)
    proc.communicate()
    return proc.returncode == 0


def ping(address: str, timeout: int = 5) -> bool:
    if platform.system().lower() == "windows":
        return _ping_windows(address, timeout)
    return _ping_linux(address, timeout)
