import os
import shutil
import unittest
from utils import get_log_attrs, url_and_time_parser
from config import load_config


class LogAnalayzerTest(unittest.TestCase):

    def setUp(self) -> None:
        self.cfg = load_config("./config.json")

        # подготовим тестовую папку
        path_test = 'test_ext'
        os.makedirs(path_test, exist_ok=True)
        self.cfg['LOG_DIR'] = path_test

        # создадим тестовый логи
        for name in ['nginx-access-ui.log-20170630.gz',
                     'nginx-access-ui.log-20180630.plain',
                     'nginx-access-ui.log-20190630.bz2',
                     'nginx-access-ui.log-20170630.another',
                     'nginx-access-ui.log-20170630.rar',]:
            with open(os.path.join(self.cfg['LOG_DIR'], name), 'w') as f:
                pass

    def test_correct_log_extension(self):
        """функцию поиска лога не должна возвращать .bz2 файлы и т.п. """
        log_name, log_date = get_log_attrs(self.cfg)
        self.assertEqual(log_name, 'nginx-access-ui.log-20180630.plain',
                         'должен быть "nginx-access-ui.log-20180630.plain"')

    def test_correct_parse_url_and_time(self):
        log_line = '1.99.174.176 3b81f63526fa8  - [29/Jun/2017:03:50:22 +0300]' \
                   ' "GET /api/1//?server_name=WIN7RB4 HTTP/1.1"' \
                   '  200 12 "-" "Python-urllib/2.7" "-" "1498697422-32900793-4708-9752770" "-" 0.133'
        url, time = url_and_time_parser(log_line)
        self.assertEqual(url, '/api/1//?server_name=WIN7RB4', 'должно быть так: "/api/1//?server_name=WIN7RB4"')
        self.assertEqual(time, 0.133, 'должно быть так: "0.133"')

    def tearDown(self) -> None:
        # удалим тестовый набор данных
        shutil.rmtree(self.cfg['LOG_DIR'], ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
