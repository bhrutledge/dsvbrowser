import csv
import glob
import os
import sys

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug import secure_filename

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPORT_DIR = os.path.join(SCRIPT_DIR, 'reports')
REPORT_EXT = '.txt'

app = Flask(__name__)


def get_report_name(report_fname):
    return os.path.splitext(os.path.basename(report_fname))[0]


def get_report_path(report_dir, report_fname):
    return os.path.join(REPORT_DIR, report_dir, secure_filename(report_fname))
    

def list_report_dir(report_dir):
    report_path = os.path.join(REPORT_DIR, report_dir, '*' + REPORT_EXT)
    return [ get_report_name(f) for f in glob.glob(report_path) ]


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


def parse_input(in_path):    
    with open(in_path, 'U') as in_file:
        line_iter = nonblank_lines(in_file)        
        title = line_iter.next()

        row_iter = csv.reader(line_iter, delimiter='\t')
        head_row = row_iter.next()
        body_rows = list(row_iter)
        
    return (title, head_row, body_rows)


@app.route('/')
def list_directories():
    try:
        report_dirs = [ d for d in os.listdir(REPORT_DIR) 
                    if os.path.isdir(os.path.join(REPORT_DIR, d)) ]
    except OSError:
        abort(404)

    return render_template('directories.html', report_dirs=report_dirs)


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

    return render_template('reports.html',
                           report_dir=report_dir,
                           report_names=list_report_dir(report_dir))


@app.route('/<report_dir>/<report_name>')
def show_report(report_dir, report_name):
    report_path = get_report_path(report_dir, report_name + REPORT_EXT)

    try:
        title, head, body = parse_input(report_path)
    except IOError:
        abort(404)
        
    return render_template(report_dir + '.html', 
                           report_dir=report_dir, report_name=report_name,
                           title=title, head=head, body=body)


if __name__ == '__main__':
    app.run(debug=True)
