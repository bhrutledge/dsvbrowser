import csv
import errno
import flask
import os

from werkzeug.exceptions import Forbidden, NotFound
from .constants import *


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


def report_dir_path(*args):
    return os.path.join(flask.current_app.instance_path, REPORT_DIR, *args)


def valid_upload(upload):
    return bool(upload and upload.filename.endswith(REPORT_EXT))
