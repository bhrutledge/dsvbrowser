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
        self.subdir = 'inventory'
        self.subdir_slugs = {'inventory' : ['report_one', 'report_two']}

    def test_list_subdirs(self):
        rsp = self.client.get(view_url(''))
        self.assertEqual(rsp.status_code, 200)
        for subdir in self.subdir_slugs:
            self.assertIn(subdir, rsp.data)

    def test_list_reports(self):
        for subdir in self.subdir_slugs:
            rsp = self.client.get(view_url(subdir))
            self.assertEqual(rsp.status_code, 200)
            self.assertIn(subdir, rsp.data)
            
            for slug in self.subdir_slugs[subdir]:
                self.assertIn(view_url(subdir, slug), rsp.data)

    def test_list_reports_not_found(self):
        rsp = self.client.get(view_url('foo'))
        self.assertEqual(rsp.status_code, 404)
        
    def test_list_reports_forbidden(self):
        pass

    def test_show_report(self):
        for subdir in self.subdir_slugs:
            for slug in self.subdir_slugs[subdir]:
                rsp = self.client.get(view_url(subdir, slug))
                self.assertEqual(rsp.status_code, 200)
                self.assertIn(slug, rsp.data)

    def test_show_report_not_found(self):
        for subdir in self.subdir_slugs:
            rsp = self.client.get(view_url(subdir, 'foo'))
            self.assertEqual(rsp.status_code, 404)

        rsp = self.client.get(view_url('foo', 'bar'))
        self.assertEqual(rsp.status_code, 404)

    # TODO: def test_show_report_forbidden(self):

    def test_upload_file(self):
        slug = 'test'

        rsp = self.client.post(view_url(self.subdir), 
            data={'file': (StringIO('foo\nbar'), slug + REPORT_EXT)})

        self.assertEqual(rsp.status_code, 302)
        self.assertIn(view_url(self.subdir, slug), rsp.location)

    def test_upload_file_redirect(self):
        slug = 'test'
        contents = """
        report title

        column one\tcolumn two\t
        data one\tdata two\t
        """

        rsp = self.client.post(view_url(self.subdir), 
            data={'file': (StringIO(contents), slug + REPORT_EXT)},
            follow_redirects=True)

        self.assertEqual(rsp.status_code, 200)
        self.assertIn('report title', rsp.data)
        self.assertIn('column one', rsp.data)
        self.assertIn('data two', rsp.data)

    def test_upload_file_invalid(self):
        subdir_url = view_url(self.subdir)
        invalid_data = [
            {'file': (StringIO(''), '')},
            {'file': (StringIO('foo\nbar'), '')},
            {'file': (StringIO(''), 'foo.bar')},
            {'file': (StringIO('foo\nbar'), 'foo.bar')}
        ]

        for data in invalid_data:
            rsp = self.client.post(subdir_url, data=data)
            self.assertEqual(rsp.status_code, 200)
            self.assertIn('Invalid file', rsp.data)
            self.assertIn(self.subdir, rsp.data)

    def test_upload_file_not_found(self):
        rsp = self.client.post(view_url('foo'), 
            data={'file': (StringIO('foo\nbar'), 'foo.txt')},
            follow_redirects=True)

        self.assertEquals(rsp.status_code, 404)

    def test_delete_report(self):
        slug = self.subdir_slugs[self.subdir][0]

        rsp = self.client.post(view_url(self.subdir, slug, 'delete'))
        self.assertEqual(rsp.status_code, 302)
        self.assertIn(view_url(self.subdir), rsp.location)

    def test_delete_report_redirect(self):
        slug = self.subdir_slugs[self.subdir][0]

        rsp = self.client.post(view_url(self.subdir, slug, 'delete'),
                               follow_redirects=True)

        self.assertEqual(rsp.status_code, 200)
        self.assertNotIn(slug, rsp.data)

    def test_delete_report_get(self):
        slug = self.subdir_slugs[self.subdir][0]

        rsp = self.client.get(view_url(self.subdir, slug, 'delete'))
        self.assertEqual(rsp.status_code, 405)

    def test_delete_report_not_found(self):
        slug = 'foo'
        rsp = self.client.post(view_url(self.subdir, slug, 'delete'),
                              follow_redirects=True)
        
        self.assertEqual(rsp.status_code, 404)
