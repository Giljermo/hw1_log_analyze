import os
import re
import gzip
from array import array
from datetime import datetime as dt
from statistics import median


def parse_date(date_string):
    """получить объект datetime из строки"""
    return dt.strptime(date_string, '%Y%m%d')


def get_log_attrs(config):
    """
    поиск наменования актуального лога, а получения его даты создания
    """
    actual_log = None
    date_log = None

    for log in os.listdir(config['LOG_DIR']):
        match = re.match(config['LOG_NAME_PATTERN'], log)
        if not match:
            continue

        date_ = match.group(1)
        if date_:
            if not date_log:
                date_log = parse_date(date_)
                actual_log = log
            else:
                if parse_date(date_) > date_log:
                    date_log = parse_date(date_)
                    actual_log = log

    return actual_log, date_log


def get_log_info(log_path):
    """получить построчную информацию из логов"""
    log_open = gzip.open if log_path.endswith('.gz') else open
    with log_open(log_path, 'r') as f:
        for line in f.readlines():
            if isinstance(line, bytes):
                line = line.decode('utf-8')
            yield line


def parse_url_and_time(log_info):
    """распарсить url и время обработки url"""
    url = time = None
    pattern = '.+\"(GET|POST) (.+?) '
    match = re.match(pattern, log_info)
    if match:
        url = match.group(2)

    if float(log_info.strip('\n').split()[-1]):
        time = float(log_info.strip('\n').split()[-1])

    return url, time


def get_time_array(log_path):
    """для каждого уникального url сформировать массив содержащий время обработки при каждом обращении к url"""
    stats = {}  # stats = {'example/url/1': array([123ms, 432ms, 5ms, 85ms, ...])}
    success_count = 0
    unsuccess_count = 0

    for log_info in get_log_info(log_path):
        url, time = parse_url_and_time(log_info)
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
