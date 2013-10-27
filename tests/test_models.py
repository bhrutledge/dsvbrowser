import os
import unittest

from werkzeug.exceptions import NotFound

from tab2html import app, models
from tab2html.models import Report, ReportDirectory


class TestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

        test_dir = os.path.dirname(os.path.realpath(__file__))
        self.inv_path = os.path.join(test_dir, 'reports', 'inventory')
        self.slugs = ['one', 'two']
        self.filenames = [ s + '.txt' for s in self.slugs ]
        self.paths = [ os.path.join(self.inv_path, f) for f in self.filenames ]


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
        report_dir = ReportDirectory(self.inv_path)
        paths = report_dir.get_report_paths()
        self.assertEqual(paths, self.paths)

        # TODO: Test in views
        report_dir = ReportDirectory('foo')
        with self.assertRaises(NotFound):
            report_dir.get_report_paths()

    def test_get_reports(self):
        report_dir = ReportDirectory(self.inv_path)
        reports = report_dir.get_reports()

        self.assertEqual(len(reports), len(self.paths))
        for report in reports:
            self.assertIn(report.path, self.paths)

    def test_get_report(self):
        report_dir = ReportDirectory(self.inv_path)
        report = report_dir.get_report(self.slugs[0])

        self.assertEqual(report.path, self.paths[0])

        # TODO: Test in views
        with self.assertRaises(NotFound):
            report_dir.get_report('three')

# File upload
# Skip invalid extensions
# Skip unopenable files
