import codecs
import datetime
import os

from werkzeug import secure_filename
from .constants import *
from .utils import *


class Report(object):

    def __init__(self, path, content=[]):
        self.path = path
        self.slug = os.path.splitext(os.path.basename(path))[0]
        self.date = datetime.datetime.fromtimestamp(os.path.getmtime(path))

        self.title = ''
        self.head = []
        self.body = []
        self.content = content

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        self._content = value
        try:
            line_iter = nonblank_lines(value)
            self.title = line_iter.next()

            row_iter = unicode_csv_reader(line_iter, delimiter='\t')
            self.head = row_iter.next()
            self.body = list(row_iter)
        except StopIteration:
            pass

    @classmethod
    def from_path(cls, path):
        with codecs.open(path, 'U', encoding='utf-8') as content:
            return cls(path, content)


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
        for p in self.get_report_paths():
            try:
                reports.append(Report.from_path(p))
            except:
                # Ignore problematic paths
                continue

        return reports

    def get_report(self, slug):
        path = self.get_secure_path(slug + REPORT_EXT)
        return Report.from_path(path)

    def delete_report(self, slug):
        path = self.get_secure_path(slug + REPORT_EXT)
        os.remove(path)

    def upload_file(self, upload):
        path = self.get_secure_path(upload.filename)
        upload.save(path)
        return Report(path)
