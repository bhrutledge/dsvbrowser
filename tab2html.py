import csv
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


def get_report_name(report_fname):
    return os.path.splitext(os.path.basename(report_fname))[0]


def get_report_path(report_dir, report_fname):
    return os.path.join(REPORT_DIR, report_dir, secure_filename(report_fname))


def upload_report(report_dir, report_file):
    if report_file and report_file.filename.endswith(REPORT_EXT):
        report_path = get_report_path(report_dir, report_file.filename)
        report_file.save(report_path)
        return get_report_name(report_path)

    return None


def nonblank_lines(line_iter):
    for line in (l.strip() for l in line_iter):
        if line:
            yield line


class Report(object):
    # TODO: Add @classmethods from_path, from_name, from_upload

    def __init__(self, report_path):
        # TODO: self.date
        self.name = get_report_name(report_path)

        with open(report_path, 'U') as report_file:
            line_iter = nonblank_lines(report_file)        
            self.title = line_iter.next()

            row_iter = csv.reader(line_iter, delimiter='\t')
            self.head = row_iter.next()
            self.body = list(row_iter)


@app.route('/')
def list_directories():
    try:
        report_dirs = [ d for d in os.listdir(REPORT_DIR) 
                       if os.path.isdir(os.path.join(REPORT_DIR, d)) ]
    except OSError:
        abort(404)

    return render_template(DIRS_TEMPLATE, report_dirs=report_dirs)


@app.route('/<report_dir>', methods=['GET', 'POST'])
def list_reports(report_dir):
    if not os.path.isdir(os.path.join(REPORT_DIR, report_dir)):
        abort(404)

    if request.method == 'POST':
        report_name = upload_report(report_dir, request.files['file'])
        # TODO: Show error message
        if report_name:
            return redirect(url_for('show_report', report_dir=report_dir, 
                                    report_name=report_name))

    report_glob = os.path.join(REPORT_DIR, report_dir, '*' + REPORT_EXT)
    reports = [ Report(f) for f in glob.glob(report_glob) ]

    return render_template(REPORTS_TEMPLATE,
                           report_dir=report_dir, reports=reports)


@app.route('/<report_dir>/<report_name>')
def show_report(report_dir, report_name):
    report_path = get_report_path(report_dir, report_name + REPORT_EXT)

    try:
        report = Report(report_path)
    except IOError:
        abort(404)

    return render_template(report_dir + TEMPLATE_EXT, 
                           report_dir=report_dir, report=report)


if __name__ == '__main__':
    app.run(debug=True)
