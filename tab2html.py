import csv
import glob
import os
import sys

from flask import Flask, render_template

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPORT_DIR = os.path.join(SCRIPT_DIR, 'reports')
REPORT_EXT = '.txt'


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


app = Flask(__name__)


@app.route('/')
def list_directories():
    directories = [ d for d in os.listdir(REPORT_DIR) 
                    if os.path.isdir(os.path.join(REPORT_DIR, d)) ]
    return render_template('directories.html', directories=directories)


@app.route('/<directory>')
def list_reports(directory):
    reports = glob.glob(os.path.join(REPORT_DIR, directory, '*' + REPORT_EXT))
    reports = [ os.path.splitext(os.path.basename(f))[0] for f in reports]
    return render_template('reports.html',
                           directory=directory, reports=reports)


@app.route('/<directory>/<report>')
def show_report(directory, report):
    # TODO: Test file
    report_path = os.path.join(REPORT_DIR, directory, report + REPORT_EXT)
    title, head_row, body_rows = parse_input(report_path)
    return render_template(directory + '.html', 
                           directory=directory, report=report,
                           title=title, head=head_row, body=body_rows)


if __name__ == '__main__':
    app.run(debug=True)
