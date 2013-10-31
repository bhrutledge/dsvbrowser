import os
import shutil
import unittest

from StringIO import StringIO
from tab2html import create_app
from tab2html.constants import *
from .utils import AppTestCase


def view_url(*args):
    return '/'.join([''] + list(args))


class ViewTestCase(AppTestCase):

    def setUp(self):
        super(ViewTestCase, self).setUp()

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
        subdir = 'inventory'
        slug = 'test'
        contents = """
        report title

        column one\tcolumn two\t
        data one\tdata two\t
        """

        rv = self.client.post(view_url(subdir), 
            data={'file': (StringIO(contents), slug + REPORT_EXT)},
            follow_redirects=True)

        # TODO: Test redirect url

        self.assertEqual(rv.status_code, 200)
        self.assertIn('report title', rv.data)
        self.assertIn('column one', rv.data)
        self.assertIn('data two', rv.data)

    def test_upload_file_invalid(self):
        pass

    def test_upload_file_not_found(self):
        pass
