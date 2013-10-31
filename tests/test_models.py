import os
import unittest

from werkzeug.exceptions import NotFound

from tab2html import create_app
from tab2html.models import Report, ReportDirectory
from tab2html.constants import *


class TestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(os.path.dirname(os.path.realpath(__file__)))
        self.app = app.test_client()

        self.subdir_path = os.path.join(app.instance_path, REPORT_DIR, 
                                        'inventory')
        self.slugs = ['report_one', 'report_two']
        self.filenames = [ s + REPORT_EXT for s in self.slugs ]
        self.paths = [ os.path.join(self.subdir_path, f)
                       for f in self.filenames ]


class ReportTestCase(TestCase):

    def setUp(self):
        super(ReportTestCase, self).setUp()
        self.path = self.paths[0]
        self.slug = self.slugs[0]

    def test_path(self):
        import datetime

        report = Report(self.path)

        self.assertEqual(report.path, self.path)
        self.assertEqual(report.slug, self.slug)
        self.assertIsInstance(report.date, datetime.datetime)
        self.assertEqual(len(report.content), 0)

    def test_content(self):
        content = [' title\n', '\n', 'one\ttwo\n', '1\t2\n', '3\t4\n', '\n']

        report = Report(self.path, content)

        self.assertEqual(report.content, content)
        self.assertEqual(report.title, 'title')
        self.assertEqual(report.head, ['one', 'two'])
        self.assertEqual(report.body, [['1', '2'], ['3', '4']])

    def test_missing_content(self):
        report = Report(self.path)
        
        report.content = []
        self.assertEqual(len(report.content), 0)
        self.assertEqual(report.title, '')
        self.assertEqual(report.head, [])
        self.assertEqual(report.body, [])

        report.content = [' title\n', '\n']
        self.assertEqual(report.title, 'title')
        self.assertEqual(report.head, [])
        self.assertEqual(report.body, [])

        report.content = [' title\n', '\n', 'one\ttwo\n', '\n']
        self.assertEqual(report.title, 'title')
        self.assertEqual(report.head, ['one', 'two'])
        self.assertEqual(report.body, [])


class ReportDirectoryTestCase(TestCase):

    def test_get_report_paths(self):
        report_dir = ReportDirectory(self.subdir_path)
        paths = report_dir.get_report_paths()
        self.assertEqual(paths, self.paths)

    def test_get_reports(self):
        report_dir = ReportDirectory(self.subdir_path)
        reports = report_dir.get_reports()

        self.assertEqual(len(reports), len(self.paths))
        for report in reports:
            self.assertIn(report.path, self.paths)

        # TODO: Skip invalid extensions
        # TODO: Skip unopenable files

    def test_get_report(self):
        report_dir = ReportDirectory(self.subdir_path)
        report = report_dir.get_report(self.slugs[0])
        self.assertEqual(report.path, self.paths[0])

    def test_upload_file(self):
        pass

