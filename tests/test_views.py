import os
import unittest

from StringIO import StringIO
from tab2html import create_app


def view_url(*args):
    return '/'.join([''] + list(args))


class TestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(os.path.dirname(os.path.realpath(__file__)))
        self.client = self.app.test_client()
        self.subdirs = {'inventory' : ['report_one', 'report_two']}

    def test_list_subdirs(self):
        rv = self.client.get(view_url(''))
        self.assertEqual(rv.status_code, 200)
        for subdir in self.subdirs:
            self.assertIn(subdir, rv.data)

    def test_list_reports(self):
        for subdir in self.subdirs:
            rv = self.client.get(view_url(subdir))
            self.assertEqual(rv.status_code, 200)
            self.assertIn(subdir, rv.data)
            
            for slug in self.subdirs[subdir]:
                self.assertIn(view_url(subdir, slug), rv.data)

    def test_list_reports_not_found(self):
        rv = self.client.get(view_url('foo'))
        self.assertEqual(rv.status_code, 404)
        
    def test_list_reports_forbidden(self):
        pass

    def test_show_report(self):
        for subdir in self.subdirs:
            for slug in self.subdirs[subdir]:
                rv = self.client.get(view_url(subdir, slug))
                self.assertEqual(rv.status_code, 200)
                self.assertIn(slug, rv.data)

    def test_show_report_not_found(self):
        for subdir in self.subdirs:
            rv = self.client.get(view_url(subdir, 'foo'))
            self.assertEqual(rv.status_code, 404)

        rv = self.client.get(view_url('foo', 'bar'))
        self.assertEqual(rv.status_code, 404)

    def test_show_report_forbidden(self):
        pass

    def test_upload_file(self):
        pass
