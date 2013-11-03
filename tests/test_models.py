import os

from werkzeug.exceptions import NotFound

from tab2html.models import Report, ReportDirectory
from tab2html.constants import *
from .utils import AppTestCase


class ModelTestCase(AppTestCase):

    def setUp(self):
        super(ModelTestCase, self).setUp()

        self.subdir = 'inventory'
        self.subdir_path = os.path.join(
            self.instance_path, REPORT_DIR, self.subdir)
        self.slugs = ['report_one', 'report_two']
        self.filenames = [ s + REPORT_EXT for s in self.slugs ]
        self.paths = [ os.path.join(self.subdir_path, f)
                       for f in self.filenames ]


class ReportTestCase(ModelTestCase):

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


class ReportDirectoryTestCase(ModelTestCase):

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

    # TODO: def test_get_reports_invalid_exts(self):
    # TODO: def test_get_reports_unopenable(self):

    def test_get_report(self):
        report_dir = ReportDirectory(self.subdir_path)
        report = report_dir.get_report(self.slugs[0])
        self.assertEqual(report.path, self.paths[0])

    def test_delete_report(self):
        report_dir = ReportDirectory(self.subdir_path)
        slug = self.slugs[0]

        report_dir.delete_report(slug)
        reports = report_dir.get_reports()

        self.assertEqual(len(reports), len(self.slugs) - 1)
        for report in reports:
            self.assertNotEqual(slug, report.slug)

    # TODO: def test_upload_file(self):

