#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging as lg
import os
from string import Template

from tools import get_time_array, calc_log_stats, get_log_attrs
from config import load_config


def main():
    # распарсить аргументы с помощью argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="путь до конфига парсера", default="")
    args = parser.parse_args()

    # считать парамметры конфига
    config = load_config(path_=args.config)

    # настроить логер
    file_name = f"{config['LOG_DIR']}/parser.log" if config['LOG_DIR'] else None
    lg.basicConfig(filename=file_name,
                   level='INFO',
                   format='[%(asctime)s] %(levelname).1s %(message)s',
                   datefmt='%Y.%m.%d %H:%M:%S')

    log_name, log_date = get_log_attrs(config)  # получить путь лог файла
    if not log_name:
        lg.info(f'Лог файл отсутсвует в каталоге "{config["LOG_DIR"]}" ')
        return

    report_name = f'report-{log_date.strftime("%Y.%m.%d")}.html'
    report_path = os.path.join(config["REPORT_DIR"],  report_name)
    # проверка наличия предыдущего запуска
    if report_name in os.listdir(config["REPORT_DIR"]):
        lg.info(f'Отчет уже сформироан, посмотрите в папку "{report_path}"')
        return

    # подсчитать статистику
    stats_array, error_threshold = get_time_array(log_path=os.path.join(config["LOG_DIR"], log_name))
    if error_threshold < config["ERROR_THRESHOLD"]:
        lg.info(f'Большую часть анализируемого лога не удалось распарсить, процент ошибок "{error_threshold}"')
        return

    # подставить в шаблон
    stats = calc_log_stats(stats_array)
    with open(os.path.join(config["TEMPLATE_DIR"], 'report.html'), encoding='utf-8') as f:
        data = Template(f.read()).safe_substitute({'table_json': stats})

    with open(report_path, mode='w') as f:
        f.write(data)


if __name__ == "__main__":
    try:
        lg.info('Начинаю анализ логов')
        main()
        lg.info('Анализ логов завершен')
    except Exception:
        lg.exception(...)
