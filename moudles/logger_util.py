import os
import platform
from datetime import datetime
from typing import Any


def init_log(log_path: str = 'log.txt') -> None:
    os.makedirs(os.path.dirname(log_path) or '.', exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(f"OS：{platform.system()}\n")
        log.write(f"BUILD：{platform.release()}\n")
        log.write(f"PLATFORM：{platform.machine()}\n")
        log.write(f"TIME：{datetime.now()}\n\n")


def log_print(*args: Any, log_path: str = 'log.txt') -> None:
    # console
    try:
        print(*args)
    except Exception:
        pass
    # file append
    try:
        with open(log_path, 'a', encoding='utf-8') as f:
            print(*args, file=f)
    except Exception:
        pass


