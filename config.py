import json
from json.decoder import JSONDecodeError
import logging


config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "TEMPLATE_DIR": "./template",
    "ERROR_THRESHOLD": 0.8,
    "LOG_NAME_PATTERN": 'nginx-access-ui.log-([0-9]+).(gz|plain)',
}


def load_config(path):
    """загрузить парметры для парсинга"""
    try:
        with open(path, encoding='utf-8') as f:
            file_config = json.load(f)
            config.update(file_config)

        return config
    except (FileNotFoundError, PermissionError, JSONDecodeError):
        logging.exception(...)
        raise Exception("файл конфига не существует или не парсится")
