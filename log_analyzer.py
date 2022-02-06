#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import os

from utils import get_time_array, calc_log_stats, get_log_attrs, render_report, save_report
from config import load_config

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", help="путь до конфига парсера", default="./config.json")
args = parser.parse_args()

config = load_config(args.config)
logging.basicConfig(filename=f"{config['LOG_DIR']}/parser.log" if config['LOG_DIR'] else None,
                    format='[%(asctime)s] %(levelname).1s %(message)s',
                    datefmt='%Y.%m.%d %H:%M:%S')


def main():
    log_name, log_date = get_log_attrs(config)
    if not log_name:
        logging.info(f'Лог файл отсутсвует в каталоге "{config["LOG_DIR"]}" ')
        return

    report_name = f'report-{log_date.strftime("%Y.%m.%d")}.html'
    report_path = os.path.join(config["REPORT_DIR"], report_name)
    if report_name in os.listdir(config["REPORT_DIR"]):
        logging.info(f'Отчет уже сформироан, посмотрите в папку "{report_path}"')
        return

    # подсчитать статистику
    stats_array, error_threshold = get_time_array(log_path=os.path.join(config["LOG_DIR"], log_name))
    if error_threshold < config["ERROR_THRESHOLD"]:
        logging.info(f'Большую часть анализируемого лога не удалось распарсить, процент ошибок "{error_threshold}"')
        return

    report = render_report(template=os.path.join(config["TEMPLATE_DIR"], 'report.html'),
                           stats=calc_log_stats(stats_array))

    save_report(save_path=report_path, report=report)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception(...)
