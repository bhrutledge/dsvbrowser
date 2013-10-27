import codecs
import csv
import datetime
import errno
import os

from werkzeug import secure_filename
from werkzeug.exceptions import Forbidden, NotFound


# TODO: Move constants and methods to class?
REPORT_EXT = '.txt'


def raise_errno(e):
    if e.errno in [errno.EPERM, errno.EACCES]:
        raise Forbidden
    elif e.errno == errno.ENOENT:
        raise NotFound
    else:
        raise


def nonblank_lines(line_iter):
    for line in (l.strip() for l in line_iter):
        if line:
            yield line


# Source: http://docs.python.org/2/library/csv.html#examples

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


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
        try:
            with codecs.open(path, 'U', encoding='utf-8') as content:
                return cls(path, content)
        except EnvironmentError as e:
            raise_errno(e)


class ReportDirectory(object):

    def __init__(self, path):
        self.path = path

    def get_report_paths(self):
        try:
            return [ os.path.join(self.path, f) for f in os.listdir(self.path)
                     if f.endswith(REPORT_EXT) ]
        except EnvironmentError as e:
            raise_errno(e)

    def get_reports(self):
        reports = []
        for p in self.get_report_paths():
            try:
                reports.append(Report.from_path(p))
            except:
                continue

        return reports

    def get_report(self, slug):
        path = os.path.join(self.path, secure_filename(slug + REPORT_EXT))
        return Report.from_path(path)

    def upload_file(self, upload):
        if upload and upload.filename.endswith(REPORT_EXT):
            path = os.path.join(self.path, secure_filename(upload.filename))
            
            try:
                upload.save(path)
            except EnvironmentError as e:
                raise_errno(e)
            
            return Report(path)    

