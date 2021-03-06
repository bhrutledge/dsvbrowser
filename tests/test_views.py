# pylint: disable=too-many-public-methods,maybe-no-member,fixme

from StringIO import StringIO
from werkzeug.datastructures import MultiDict

from dsvbrowser.constants import REPORT_EXT
from .utils import AppTestCase


SUBDIR = 'default'
SUBDIR_SLUGS = {'default': ['report_one', 'report_two']}
UPLOAD_ACTION = '?action=upload'
DELETE_ACTION = '?action=delete'


def view_url(*args):
    return '/'.join([''] + list(args))


class ViewTestCase(AppTestCase):

    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.client = self.app.test_client()

    def test_show_index(self):
        rsp = self.client.get(view_url(''))
        self.assertEqual(rsp.status_code, 200)
        for subdir in SUBDIR_SLUGS:
            self.assertIn(subdir, rsp.data)

    def test_show_subdir(self):
        for subdir in SUBDIR_SLUGS:
            rsp = self.client.get(view_url(subdir))
            self.assertEqual(rsp.status_code, 200)
            self.assertIn(subdir, rsp.data)

            for slug in SUBDIR_SLUGS[subdir]:
                self.assertIn(view_url(subdir, slug), rsp.data)

    def test_show_subdir_not_found(self):
        rsp = self.client.get(view_url('foo'))
        self.assertEqual(rsp.status_code, 404)

    # TODO: def test_show_subdir_post(self):
    # TODO: def test_show_subdir_forbidden(self):

    def test_show_report(self):
        for subdir in SUBDIR_SLUGS:
            for slug in SUBDIR_SLUGS[subdir]:
                rsp = self.client.get(view_url(subdir, slug))
                self.assertEqual(rsp.status_code, 200)
                self.assertIn(slug, rsp.data)

    def test_show_report_not_found(self):
        for subdir in SUBDIR_SLUGS:
            rsp = self.client.get(view_url(subdir, 'foo'))
            self.assertEqual(rsp.status_code, 404)

        rsp = self.client.get(view_url('foo', 'bar'))
        self.assertEqual(rsp.status_code, 404)

    # TODO: def test_show_report_post(self):
    # TODO: def test_show_report_forbidden(self):

    def test_upload_file(self):
        slug = 'test'
        data = {'file': (StringIO('foo\nbar'), slug + REPORT_EXT)}

        rsp = self.client.post(view_url(SUBDIR + UPLOAD_ACTION), data=data)

        self.assertEqual(rsp.status_code, 302)
        self.assertIn(view_url(SUBDIR, slug), rsp.location)

    def test_upload_file_redirect(self):
        slug = 'test'
        content = """
        report title

        column one\tcolumn two\t
        data one\tdata two\t
        """

        data = {'file': (StringIO(content), slug + REPORT_EXT)}
        rsp = self.client.post(view_url(SUBDIR) + UPLOAD_ACTION, data=data,
                               follow_redirects=True)

        self.assertEqual(rsp.status_code, 200)
        self.assertIn('report title', rsp.data)
        self.assertIn('column one', rsp.data)
        self.assertIn('data two', rsp.data)

    def test_upload_file_invalid(self):
        subdir_url = view_url(SUBDIR)
        invalid_data = [
            {'file': (StringIO(''), '')},
            {'file': (StringIO('foo\nbar'), '')},
            {'file': (StringIO(''), 'foo.bar')},
            {'file': (StringIO('foo\nbar'), 'foo.bar')}
        ]

        for data in invalid_data:
            rsp = self.client.post(subdir_url + UPLOAD_ACTION, data=data)
            self.assertEqual(rsp.status_code, 200)
            self.assertIn('Invalid file', rsp.data)
            self.assertIn(SUBDIR, rsp.data)

    def test_upload_file_not_found(self):
        data = {'file': (StringIO('foo\nbar'), 'foo.txt')}
        rsp = self.client.post(view_url('foo') + UPLOAD_ACTION, data=data,
                               follow_redirects=True)

        self.assertEquals(rsp.status_code, 404)

    def test_delete_report(self):
        slug = SUBDIR_SLUGS[SUBDIR][0]

        rsp = self.client.post(view_url(SUBDIR, slug + DELETE_ACTION))
        self.assertEqual(rsp.status_code, 302)
        self.assertIn(view_url(SUBDIR), rsp.location)

    def test_delete_report_redirect(self):
        slug = SUBDIR_SLUGS[SUBDIR][0]

        rsp = self.client.post(view_url(SUBDIR, slug + DELETE_ACTION),
                               follow_redirects=True)

        self.assertEqual(rsp.status_code, 200)
        self.assertNotIn(slug, rsp.data)

    def test_delete_report_not_found(self):
        slug = 'foo'
        rsp = self.client.post(view_url(SUBDIR, slug + DELETE_ACTION),
                               follow_redirects=True)

        self.assertEqual(rsp.status_code, 404)

    def test_delete_reports(self):
        rsp = self.client.post(view_url(SUBDIR + DELETE_ACTION))
        self.assertEqual(rsp.status_code, 302)
        self.assertIn(view_url(SUBDIR), rsp.location)

    def test_delete_reports_redirect(self):
        slug = SUBDIR_SLUGS[SUBDIR][0]

        rsp = self.client.post(view_url(SUBDIR + DELETE_ACTION),
                               data={'slug': slug},
                               follow_redirects=True)

        self.assertEqual(rsp.status_code, 200)
        self.assertNotIn(slug, rsp.data)

        slugs = SUBDIR_SLUGS[SUBDIR]

        rsp = self.client.post(view_url(SUBDIR + DELETE_ACTION),
                               data=MultiDict([('slug', s) for s in slugs]),
                               follow_redirects=True)

        self.assertEqual(rsp.status_code, 200)
        for slug in slugs:
            self.assertNotIn(slug, rsp.data)
