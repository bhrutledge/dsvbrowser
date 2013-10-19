import codecs
import csv
import datetime
import glob
import os
import sys

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug import secure_filename


app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('config.py', silent=True)


REPORT_DIR = os.path.join(app.instance_path, 'reports')
REPORT_EXT = '.txt'
TEMPLATE_EXT = '.html'
DIRS_TEMPLATE = 'directories' + TEMPLATE_EXT
REPORTS_TEMPLATE = 'reports' + TEMPLATE_EXT


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
    def from_upload(cls, subdir, upload):
        if upload and upload.filename.endswith(REPORT_EXT):
            path = join_path(subdir, secure_filename(upload.filename))
            upload.save(path)
            return cls(path)    

    @staticmethod
    def path_from_slug(subdir, slug):
        return join_path(subdir, secure_filename(slug + REPORT_EXT))


@app.route('/')
def list_directories():
    subdirs = os.walk(REPORT_DIR).next()[1]
    return render_template(DIRS_TEMPLATE, subdirs=subdirs)


@app.route('/<subdir>', methods=['GET', 'POST'])
def list_reports(subdir):
    if not os.path.isdir(join_path(subdir)):
        abort(404)

    if request.method == 'POST':
        # TODO: Show error messages
        report = Report.from_upload(subdir, request.files['file'])
        if report:
            return redirect(url_for('show_report', 
                                    subdir=subdir, slug=report.slug))

    reports = [ Report.from_path(f) for 
                f in glob.glob(join_path(subdir, '*' + REPORT_EXT)) ]

    return render_template(REPORTS_TEMPLATE, subdir=subdir, reports=reports)


@app.route('/<subdir>/<slug>')
def show_report(subdir, slug):
    path = Report.path_from_slug(subdir, slug)
    if not os.path.isfile(path):
        abort(404)

    report = Report.from_path(path)
    return render_template(subdir + TEMPLATE_EXT, subdir=subdir, report=report)


if __name__ == '__main__':
    app.run()
