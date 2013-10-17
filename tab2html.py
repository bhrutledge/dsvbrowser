import csv
import datetime
import glob
import os
import sys

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug import secure_filename


app = Flask(__name__)


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPORT_DIR = os.path.join(SCRIPT_DIR, 'reports')
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


class Report(object):

    def __init__(self, path, content=None):
        self.path = path
        self.slug = os.path.splitext(os.path.basename(path))[0]
        self.date = datetime.datetime.fromtimestamp(os.path.getmtime(path))

        if content:
            line_iter = nonblank_lines(content)        
            self.title = line_iter.next()

            row_iter = csv.reader(line_iter, delimiter='\t')
            self.head = row_iter.next()
            self.body = list(row_iter)

    @classmethod
    def from_path(cls, path):
        with open(path, 'U') as content:
            return cls(path, content)   

    @classmethod
    def from_slug(cls, subdir, slug):
        path = join_path(subdir, secure_filename(slug + REPORT_EXT))
        return cls.from_path(path)

    @classmethod
    def from_upload(cls, subdir, upload):
        if upload and upload.filename.endswith(REPORT_EXT):
            path = join_path(subdir, secure_filename(upload.filename))
            upload.save(path)
            return cls(path)    


@app.route('/')
def list_directories():
    try:
        subdirs = os.walk(REPORT_DIR).next()[1]
    except:
        abort(404)

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
    try:
        report = Report.from_slug(subdir, slug)
    except:
        abort(404)

    return render_template(subdir + TEMPLATE_EXT, subdir=subdir, report=report)


if __name__ == '__main__':
    app.run(debug=True)
