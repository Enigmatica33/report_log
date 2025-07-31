import pytest
import argparse
from unittest.mock import patch
from report import LogAnalyzer, main


def test_read_file(tmp_path):
    test_file = tmp_path / "test_log.json"
    test_file.write_text('{"test": "data"}\n')
    analyzer = LogAnalyzer([str(test_file)], 'test_report')
    lines = analyzer.read_file(str(test_file))
    assert lines == ['{"test": "data"}\n']


def test_parse_logs(tmp_path):
    test_file = tmp_path / "test_log.json"
    test_file.write_text('{"@timestamp": "2024-01-01T00:00:00+00:00", "url": "/test", "response_time": 1.0}\n')
    analyzer = LogAnalyzer([str(test_file)], 'test_report')
    analyzer.parse_logs()
    assert len(analyzer.results) == 1


def test_analyze_urls(tmp_path):
    test_file = tmp_path / "test_log.json"
    test_file.write_text('{"@timestamp": "2024-01-01T00:00:00+00:00", "url": "/test", "response_time": 1.0}\n')
    analyzer = LogAnalyzer([str(test_file)], 'test_report')
    analyzer.parse_logs()
    analyzer.analyze_urls()
    assert analyzer.urls_stat["/test"]["average_time"] == 1.0


def test_main(tmp_path):
    test_file = tmp_path / "test_log.json"
    test_file.write_text('{"@timestamp": "2024-01-01T00:00:00+00:00", "url": "/test", "response_time": 1.0}\n')

    with patch(
        'argparse.ArgumentParser.parse_args',
        return_value=argparse.Namespace(
            file=[str(test_file)],
            report='average',
            date=None
            )
    ):
        analyzer = main()
        assert analyzer is not None


def test_main_no_file():
    with pytest.raises(ValueError, match='Укажите хотя бы один файл.'):
        with patch(
            'argparse.ArgumentParser.parse_args',
            return_value=argparse.Namespace(file=None)
        ):
            main()


def test_read_file_error(tmp_path, caplog):
    analyzer = LogAnalyzer(["nonexistent.json"], 'test_report')
    lines = analyzer.read_file("nonexistent.json")
    assert lines == []
    assert "Файл не найден" in caplog.text


def test_parse_logs_invalid_json(tmp_path, caplog):
    test_file = tmp_path / "invalid.json"
    test_file.write_text('invalid json\n')
    analyzer = LogAnalyzer([str(test_file)], 'test_report')
    analyzer.parse_logs()
    assert "Ошибка при парсинге JSON" in caplog.text
