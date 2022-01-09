import json
import os
from json.decoder import JSONDecodeError
import logging as lg

DEFAULT_CONFIG = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE_DIR": "./template",
    "ERROR_THRESHOLD": 0.8,
    "LOG_NAME_PATTERN": 'nginx-access-ui.log-([0-9]+).(gz|plain)',
}


def load_config(path_=None):
    """загрузить парметры для парсинга"""
    if not path_:
        [os.makedirs(DEFAULT_CONFIG[d]) for d in ['REPORT_DIR', 'LOG_DIR']]
        return DEFAULT_CONFIG

    try:
        with open(path_, encoding='utf-8') as f:
            temp_config = json.load(f)
            for key in DEFAULT_CONFIG.copy():
                if key in temp_config:
                    DEFAULT_CONFIG[key] = temp_config[key]
        return DEFAULT_CONFIG
    except (FileNotFoundError, PermissionError, JSONDecodeError):
        lg.exception(...)
        raise Exception("файл не существует или не парсится")
