import os
from typing import Dict, Optional


def read_config_file(path: str = 'config.ini') -> Dict[str, str]:
    """Read a simple config file with lines like [key]=value.

    - Ignores empty/invalid lines
    - Later duplicates overwrite earlier ones
    """
    config: Dict[str, str] = {}
    if not os.path.exists(path):
        return config

    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    key = key.strip('[]').strip()
                    value = value.strip()
                    if key:
                        config[key] = value
    except Exception:
        # Best-effort parsing; caller can decide defaults
        pass
    return config


def write_config_file(config: Dict[str, str], path: str = 'config.ini') -> None:
    """Write the config dict back to disk in [key]=value lines, compacted."""
    lines = []
    for k, v in config.items():
        if v is None:
            continue
        lines.append(f"[{k}]={v}\n")
    # remove empty lines and duplicates are already resolved
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def update_entry(key: str, value: Optional[str], path: str = 'config.ini') -> Dict[str, str]:
    """Update a single entry in config.ini and return the updated dict.

    - If value is None or empty string, the key is removed
    - Ensures one entry per key
    """
    config = read_config_file(path)
    if value is None or value == "":
        # remove key
        if key in config:
            del config[key]
    else:
        config[key] = str(value)
    write_config_file(config, path)
    return config
