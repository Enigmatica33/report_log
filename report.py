import argparse
import json
import logging
from datetime import datetime

from tabulate import tabulate

REPORT_DATE_FORMAT = '%Y-%d-%m'
LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%+z'


class LogAnalyzer():

    def __init__(self, file_paths, report_name, date=None):
        self.file_paths = file_paths
        self.report_name = report_name
        self.date = date
        self.results = []
        self.urls_stat = {}

    @staticmethod
    def check_date(log_date, report_date):
        parse_date = datetime.fromisoformat(log_date).date()
        report_date = datetime.strptime(
                            report_date,
                            REPORT_DATE_FORMAT
                        ).date()
        return parse_date == report_date

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.readlines()
        except FileNotFoundError:
            logging.error(f'Файл не найден: {file_path}.')
        except Exception as e:
            logging.error(f'Ошибка чтения файла {file_path}: {e}')
        return []

    def parse_logs(self):
        for file_path in self.file_paths:
            lines = self.read_file(file_path)
            for line in lines:
                try:
                    log_entry = json.loads(line)
                    if not self.date or self.check_date(
                        log_entry['@timestamp'],
                        self.date
                    ):
                        self.results.append(log_entry)
                except json.JSONDecodeError:
                    logging.error('Ошибка при парсинге JSON в файле '
                                  f'{file_path}: {line.strip()}')

    def analyze_urls(self):
        for result in self.results:
            url = result['url']
            time = round(result['response_time'], 3)
            if url not in self.urls_stat:
                self.urls_stat[url] = {'total_time': 0.0, 'count': 0}
            self.urls_stat[url]['total_time'] += time
            self.urls_stat[url]['count'] += 1

        for url, stats in self.urls_stat.items():
            stats['average_time'] = round(
                stats['total_time']/stats['count'], 3
            )

    def print_report(self):
        table_data = [
            {'id': index,
             'url': key,
             'total_time': value['total_time'],
             'average_time': value['average_time']
             } for
            index, (key, value) in enumerate(self.urls_stat.items())
            ]
        print(tabulate(table_data, headers='keys', tablefmt='fancy_grid'))


def main():
    """
    Основная логика скрипта.
    """
    parser = argparse.ArgumentParser(description='Обработка лог-файлов.')
    parser.add_argument('--file', nargs='+', help='Путь к файлу/файлам')
    parser.add_argument(
        '--report',
        default='average',
        required=False,
        help='Название отчета'
    )
    parser.add_argument('--date', required=False, help='Дата логов')
    args = parser.parse_args()

    if not args.file:
        raise ValueError('Укажите хотя бы один файл для анализа.')

    analyzer = LogAnalyzer(args.file, args.report, args.date)
    analyzer.parse_logs()
    analyzer.analyze_urls()
    analyzer.print_report()
    return analyzer


if __name__ == '__main__':
    main()
