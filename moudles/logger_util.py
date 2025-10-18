import os
import platform
from datetime import datetime
from typing import Any

def init_log(log_path: str = 'log.txt') -> None:
    """Initialize the log file.

    If a relative path is provided, it will be created under current working directory.
    Prefer passing an absolute path from main after appdata_path is set.
    """
    os.makedirs(os.path.dirname(log_path) or '.', exist_ok=True)
    with open(log_path, 'w', encoding='utf-8') as log:
        log.write(f"OS：{platform.system()}\n")
        log.write(f"BUILD：{platform.release()}\n")
        log.write(f"PLATFORM：{platform.machine()}\n")
        log.write(f"TIME：{datetime.now()}\n\n")


def log_print(*args: Any, log_path: str = None) -> None:
    """Print to console and append to log file.

    log_path defaults to appdata/log.txt if appdata_path is available, otherwise ./log.txt.
    Resolved at call-time to avoid import-time errors when appdata_path is not yet initialized.
    """
    # console
    try:
        print(*args)
    except Exception:
        pass
    # file append
    try:
        # Resolve default log path lazily without creating import cycles
        if log_path is None:
            base_dir = '.'
            try:
                # Lazy import to avoid circular dependency at import-time
                from moudles.app_state import app_state as _app_state  # type: ignore
                base_dir = _app_state.appdata_path or '.'
            except Exception:
                base_dir = '.'
            log_path = os.path.join(base_dir, 'log.txt')
        os.makedirs(os.path.dirname(log_path) or '.', exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            print(*args, file=f)
    except Exception:
        pass


