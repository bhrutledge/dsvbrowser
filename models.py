import codecs
import csv
import datetime
import glob
import os

from app import app
from werkzeug import secure_filename

REPORT_DIR = os.path.join(app.instance_path, 'reports')
REPORT_EXT = '.txt'


def join_path(*args):
    return os.path.join(REPORT_DIR, *args)


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

    def __init__(self, path, content=None):
        self.path = path
        self.slug = os.path.splitext(os.path.basename(path))[0]
        self.date = datetime.datetime.fromtimestamp(os.path.getmtime(path))

        if content:
            line_iter = nonblank_lines(content)        
            self.title = line_iter.next()

            row_iter = unicode_csv_reader(line_iter, delimiter='\t')
            self.head = row_iter.next()
            self.body = list(row_iter)

    @classmethod
    def from_path(cls, path):
        with codecs.open(path, 'U', encoding='utf-8') as content:
            return cls(path, content)   

    @classmethod
    def from_slug(cls, subdir, slug):
        path = join_path(subdir, secure_filename(slug + REPORT_EXT))
        if not os.path.isfile(path):
            return None

        return cls.from_path(path)

    @classmethod
    def from_upload(cls, subdir, upload):
        if upload and upload.filename.endswith(REPORT_EXT):
            path = join_path(subdir, secure_filename(upload.filename))
            upload.save(path)
            return cls(path)    

    @classmethod
    def from_subdir(cls, subdir):
        return [ cls.from_path(f) for 
                 f in glob.glob(join_path(subdir, '*' + REPORT_EXT)) ]

    @staticmethod
    def get_subdirs():
        return os.walk(REPORT_DIR).next()[1]

    @staticmethod
    def is_subdir(subdir):
        return os.path.isdir(join_path(subdir))
