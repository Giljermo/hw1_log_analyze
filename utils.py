import os
import re
import gzip
from array import array
from datetime import datetime as dt
from statistics import median
from string import Template


def get_log_attrs(config):
    """
    поиск наменования актуального лога, а получения его даты создания
    """
    actual_log = None
    actual_date = None

    for log_name in os.listdir(config['LOG_DIR']):
        match = re.match(config['LOG_NAME_PATTERN'], log_name)
        if not match:
            continue

        date = match.group(1)
        if not date:
            continue

        try:
            date = dt.strptime(date, '%Y%m%d')
        except ValueError:
            continue

        if (not actual_date) or (date > actual_date):
            actual_date = dt.strptime(date, '%Y%m%d')
            actual_log = log_name

    return actual_log, actual_date


def get_url_and_time_from_log(log_path, parser):
    """считывает построчно логи и возвращает распарсенные данные: url и time"""
    log_open = gzip.open if log_path.endswith('.gz') else open
    with log_open(log_path, 'r') as file:
        for line in file:
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            yield parser(line)


def url_and_time_parser(log_string):
    """ получить строку и вернуть распарсенные данные: url и time """
    url = time = None
    pattern = '.+\"(GET|POST) (.+?) '
    match = re.match(pattern, log_string)
    if match:
        url = match.group(2)

    if float(log_string.strip('\n').split()[-1]):
        time = float(log_string.strip('\n').split()[-1])

    return url, time


def get_time_array(log_path):
    """для каждого уникального url сформировать массив содержащий время обработки при каждом обращении к url"""
    stats = {}  # stats = {'example/url/1': array([123ms, 432ms, 5ms, 85ms, ...])}
    success_count = 0
    unsuccess_count = 0

    for url, time in get_url_and_time_from_log(log_path=log_path, parser=url_and_time_parser):
        if (not url) or (not time):  # если не удалось распарсить данные
            unsuccess_count += 1
            continue

        success_count += 1
        if url not in stats:
            count_array = array('d')
            count_array.append(time)
            stats[url] = count_array
        else:
            stats[url].append(time)

    error_threshold = success_count * 100 / (success_count + unsuccess_count)  # процент ошибок
    return stats, error_threshold


def calc_log_stats(stats):
    """расчет статистических данных для каждого url"""
    stats_for_render = []
    requests_count = sum([len(arr) for _, arr in stats.items()])
    requests_time = sum([sum(arr) for _, arr in stats.items()])
    for url, arr in stats.items():
        count = len(arr)
        count_perc = count * 100 / requests_count
        time_sum = sum(arr)
        time_perc = time_sum * 100 / requests_time
        time_avg = time_sum/count
        time_max = max(arr)
        time_med = median(arr)

        stats_for_render.append({
            'url': url,
            'count': round(count, 3),
            'time_avg': round(time_avg, 3),
            'time_max': round(time_max, 3),
            'time_sum': round(time_sum, 3),
            'time_med': round(time_med, 3),
            'time_perc': round(time_perc, 3),
            'count_perc': round(count_perc, 3),
        })

    return stats_for_render


def render_report(template, stats):
    with open(template, encoding='utf-8') as f:
        return Template(f.read()).safe_substitute({'table_json': stats})


def save_report(save_path, report):
    with open(save_path, mode='w') as f:
        f.write(report)
