import codecs
import datetime
import os

from werkzeug.utils import secure_filename
from .constants import REPORT_EXT
from .utils import nonblank_lines, unicode_csv_reader


class Report(object):
    # pylint: disable=too-few-public-methods

    def __init__(self, path):
        self.path = path
        self.slug = os.path.splitext(os.path.basename(path))[0]
        self.date = datetime.datetime.fromtimestamp(os.path.getmtime(path))

        self.title = ''
        self.head = []
        self.body = []

        self._read_path()

    def _read_path(self):
        with codecs.open(self.path, 'U', encoding='utf-8') as content:
            try:
                line_iter = nonblank_lines(content)
                self.title = line_iter.next()

                row_iter = unicode_csv_reader(line_iter, delimiter='\t')
                self.head = row_iter.next()
                self.body = list(row_iter)
            except StopIteration:
                pass


class ReportDirectory(object):

    def __init__(self, path):
        self.path = path

    def get_secure_path(self, filename):
        return os.path.join(self.path, secure_filename(filename))

    def get_report_paths(self):
        return [os.path.join(self.path, f) for f in os.listdir(self.path)
                if f.endswith(REPORT_EXT)]

    def get_reports(self):
        reports = []
        for path in self.get_report_paths():
            try:
                reports.append(Report(path))
            except EnvironmentError:
                # Ignore problematic paths
                continue

        return reports

    def get_report(self, slug):
        path = self.get_secure_path(slug + REPORT_EXT)
        return Report(path)

    def delete_report(self, slug):
        path = self.get_secure_path(slug + REPORT_EXT)
        os.remove(path)

    def upload_file(self, upload):
        path = self.get_secure_path(upload.filename)
        upload.save(path)
        return Report(path)
