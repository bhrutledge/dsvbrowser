import unittest

from tab2html import app

class TestCase(unittest.TestCase):

    def setUp(self):
        # TODO: Testing instance folder
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.subdirs = ['inventory']

    def test_list_subdirs(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        for subdir in self.subdirs:
            self.assertIn(subdir, rv.data)

    def test_list_reports(self):
        subdir = self.subdirs[0]

        rv = self.app.get('/' + subdir)
        self.assertEqual(rv.status_code, 200)
        self.assertIn(subdir, rv.data)

        rv = self.app.get('/foo')
        self.assertEqual(rv.status_code, 404)
        # TODO: Report list

        # TODO: Forbidden

    def test_show_report(self):
        pass

    def test_upload_file(self):
        pass
