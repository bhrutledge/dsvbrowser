import os
import unittest

from werkzeug.exceptions import NotFound

from tab2html import app, models
from tab2html.models import ReportDirectory


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.dir_path = os.path.join(test_dir, 'reports', 'inventory')
        self.filenames = ['one.txt', 'two.txt']
        self.paths = [ os.path.join(self.dir_path, f) for f in self.filenames ]


class TestReport(TestCase):

    def test_nonblank_lines(self):
        input_lines = ['one\n', '\n', 'two\n', 'three\n', 'four\n', '\n']
        expected_lines = ['one', 'two', 'three', 'four']
        
        nonblank_lines = list(models.nonblank_lines(input_lines))
        self.assertEqual(nonblank_lines, expected_lines)

# File NotFound
# File Forbidden
# Empty file
# Invalid file format

class TestReportDirectory(TestCase):

    def test_get_report_paths(self):
        report_dir = ReportDirectory(self.dir_path)
        paths = report_dir.get_report_paths()
        self.assertEqual(paths, self.paths)

        # TODO: Just test in views?
        report_dir = ReportDirectory('foo')
        with self.assertRaises(NotFound):
            report_dir.get_report_paths()

    def test_get_reports(self):
        report_dir = ReportDirectory(self.dir_path)
        reports = report_dir.get_reports()

        self.assertEqual(len(reports), len(self.paths))
        for report in reports:
            self.assertIn(report.path, self.paths)

    def test_get_report(self):
        report_dir = ReportDirectory(self.dir_path)
        report = report_dir.get_report('one')

        self.assertEqual(report.path, self.paths[0])

        with self.assertRaises(NotFound):
            report_dir.get_report('three')

# File upload
# Skip invalid extensions
# Skip unopenable files
# Directory Forbidden
