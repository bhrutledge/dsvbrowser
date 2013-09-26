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


def get_report(filename):
    return os.path.splitext(os.path.basename(filename))[0]


def get_report_path(directory, filename):
    return os.path.join(REPORT_DIR, directory, secure_filename(filename))
    

def get_reports(directory):
    filenames = glob.glob(os.path.join(REPORT_DIR, directory, '*' + REPORT_EXT))
    return [ get_report(f) for f in filenames]


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
        directories = [ d for d in os.listdir(REPORT_DIR) 
                        if os.path.isdir(os.path.join(REPORT_DIR, d)) ]
    except OSError:
        abort(404)

    return render_template('directories.html', directories=directories)


@app.route('/<directory>', methods=['GET', 'POST'])
def list_reports(directory):
    if not os.path.isdir(os.path.join(REPORT_DIR, directory)):
        abort(404)

    if request.method == 'POST':
        report_file = request.files['file']
        if report_file and report_file.filename.endswith(REPORT_EXT):
            report_path = get_report_path(directory, report_file.filename)
            report_file.save(report_path)

            return redirect(url_for('show_report', directory=directory, 
                                    report=get_report(report_path)))

    return render_template('reports.html', directory=directory,
                           reports=get_reports(directory))


@app.route('/<directory>/<report>')
def show_report(directory, report):
    report_path = get_report_path(directory, report + REPORT_EXT)

    try:
        title, head, body = parse_input(report_path)
    except IOError:
        abort(404)
        
    return render_template(directory + '.html', 
                           directory=directory, report=report,
                           title=title, head=head, body=body)


if __name__ == '__main__':
    app.run(debug=True)
