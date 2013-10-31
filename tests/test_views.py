import os
import unittest

from tab2html import create_app


def view_url(*args):
    return '/'.join([''] + list(args))


class TestCase(unittest.TestCase):

    def setUp(self):
        app = create_app(os.path.dirname(os.path.realpath(__file__)))
        self.app = app.test_client()
        self.subdirs = {'inventory' : ['report_one', 'report_two']}

    def test_list_subdirs(self):
        rv = self.app.get(view_url(''))
        self.assertEqual(rv.status_code, 200)
        for subdir in self.subdirs:
            self.assertIn(subdir, rv.data)

    def test_list_reports(self):
        for subdir in self.subdirs:
            rv = self.app.get(view_url(subdir))
            self.assertEqual(rv.status_code, 200)
            self.assertIn(subdir, rv.data)
            
            for slug in self.subdirs[subdir]:
                self.assertIn(view_url(subdir, slug), rv.data)

        rv = self.app.get(view_url('foo'))
        self.assertEqual(rv.status_code, 404)
        
        # TODO: Forbidden

    def test_show_report(self):
        for subdir in self.subdirs:
            for slug in self.subdirs[subdir]:
                rv = self.app.get(view_url(subdir, slug))
                self.assertEqual(rv.status_code, 200)
                self.assertIn(slug, rv.data)

            rv = self.app.get(view_url(subdir, 'foo'))
            self.assertEqual(rv.status_code, 404)

        rv = self.app.get(view_url('foo', 'bar'))
        self.assertEqual(rv.status_code, 404)

    def test_upload_file(self):
        pass
